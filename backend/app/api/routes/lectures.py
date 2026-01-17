import uuid
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.services.transcription import transcribe, load_transcript, load_duration
from app.services.embeddings import chunk_text
from app.db.qdrant_store import save_index, load_index
from app.services.ollama import get_llm
from app.db.crud import (
    create_lecture_record, verify_lecture_ownership, get_user_lectures,
    get_lecture_by_id, get_user_lecture_ids
)
from app.db.database import get_db
from app.config import LECTURE_DIR, INDEX_DIR, PDF_DIR
from app.models.schemas import (
    QuestionRequest, AnswerResponse, PDFRequest, PDFResponse, 
    TranscriptResponse, TranscriptSegment, TimestampSource
)
from app.models.user import UserResponse
from app.core.security import get_current_active_user

def generate_chunked_summary(transcript: str) -> str:
    """Generate summary by processing transcript in chunks and combining results"""
    llm = get_llm()
    
    # If transcript is short, summarize directly
    if len(transcript) <= 4000:
        prompt = f"""
        Please provide a concise summary of the following lecture transcript:
        
        {transcript}
        
        Summary:
        """
        return llm.invoke(prompt).strip()
    
    # For longer transcripts, chunk and summarize
    chunk_summaries = []
    
    # Split transcript into chunks with overlap
    chunks = []
    start = 0
    while start < len(transcript):
        end = start + 3500  # Leave room for prompt text
        if end >= len(transcript):
            end = len(transcript)
            chunks.append(transcript[start:end])
            break
        
        # Try to break at sentence boundary
        chunk_text = transcript[start:end]
        last_period = chunk_text.rfind('. ')
        last_question = chunk_text.rfind('? ')
        last_exclamation = chunk_text.rfind('! ')
        
        break_point = max(last_period, last_question, last_exclamation)
        if break_point > start + 1000:  # Ensure chunk isn't too small
            end = start + break_point + 2
        
        chunks.append(transcript[start:end])
        start = end - 500  # Overlap chunks
    
    # Summarize each chunk
    for i, chunk in enumerate(chunks):
        prompt = f"""
        Please provide a concise summary of this part of a lecture transcript (Part {i+1} of {len(chunks)}):
        
        {chunk}
        
        Summary of this part:
        """
        chunk_summary = llm.invoke(prompt).strip()
        chunk_summaries.append(chunk_summary)
    
    # Combine chunk summaries into final summary
    combined_chunks = f"{chr(10)}{chr(10)}".join(chunk_summaries)
    
    if len(combined_chunks) <= 4000:
        final_prompt = f"""
        Please create a coherent, comprehensive summary from these partial summaries of a lecture:
        
        {combined_chunks}
        
        Final Summary:
        """
        return llm.invoke(final_prompt).strip()
    else:
        # If combined chunks are still too long, summarize them in smaller groups
        mid_summaries = []
        group_size = 3
        for i in range(0, len(chunk_summaries), group_size):
            group = chunk_summaries[i:i+group_size]
            group_text = f"{chr(10)}{chr(10)}".join(group)
            
            prompt = f"""
            Please combine these partial summaries into a coherent summary (Section {i//group_size + 1}):
            
            {group_text}
            
            Combined Summary:
            """
            mid_summary = llm.invoke(prompt).strip()
            mid_summaries.append(mid_summary)
        
        final_prompt = f"""
        Please create a final, comprehensive summary from these section summaries:
        
        {chr(10).join(chr(10).join(mid_summaries))}
        
        Final Summary:
        """
        return llm.invoke(final_prompt).strip()

from app.services.ollama import get_llm
from app.services.pdf_generator import generate_transcript_pdf, generate_summary_pdf
from app.services.timestamp_service import parse_transcript_with_timestamps, find_relevant_segments
from app.services.rag import ask_question
from app.services.langgraph_workflows import run_lecture_qa, run_multi_lecture_search, run_lecture_summarization
from app.db.crud import create_lecture_record, verify_lecture_ownership, get_user_lectures, update_lecture, delete_lecture
from app.db.database import get_db
from app.config import LECTURE_DIR, INDEX_DIR, PDF_DIR
from app.models.schemas import (
    QuestionRequest, AnswerResponse, PDFRequest, PDFResponse, 
    TranscriptResponse, TranscriptSegment, TimestampSource
)
from app.models.multi_lecture_schemas import MultiLectureSearchRequest, MultiLectureSearchResponse
from app.models.edit_schemas import LectureUpdateRequest, DeleteResponse
from app.models.user import UserResponse
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/upload")
async def upload_lecture(
    file: UploadFile = File(...), 
    title: str = None,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check file size (max 1GB)
    MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB in bytes
    
    # Get file size from content-length header or by reading the file
    content_length = getattr(file, 'size', 0)
    if content_length > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.webm', '.mov']
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    lecture_id = str(uuid.uuid4())
    os.makedirs(LECTURE_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)

    file_path = f"{LECTURE_DIR}/{lecture_id}_{file.filename}"
    
    # Stream file to disk to handle large files efficiently
    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                f.write(chunk)
    except Exception as e:
        # Clean up partial file if upload fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    try:
        # Transcribe the lecture
        transcript = transcribe(file_path, lecture_id)
        chunks = chunk_text(transcript)

        # Generate summary during upload for quick access
        summary = generate_chunked_summary(transcript)

        # Save to Qdrant vector store
        collection_name = save_index(chunks, lecture_id, current_user.id)

        # Load duration from transcription
        duration = load_duration(lecture_id)

        # Create lecture record in database with both transcript and summary
        lecture_title = title if title and title.strip() else file.filename.replace('_', ' ').replace('-', ' ').split('.')[0]
        create_lecture_record(
            db=db,
            lecture_id=lecture_id,
            title=lecture_title,
            user_id=current_user.id,
            filename=file.filename,
            duration=duration,
            qdrant_collection=collection_name,
            summary=summary
        )

        return {"lecture_id": lecture_id}
    except Exception as e:
        # Clean up uploaded file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.get("/my-lectures")
def get_my_lectures(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all lectures for the current user"""
    lectures = get_user_lectures(db, current_user.id)
    return {"lectures": lectures}

@router.get("/{lecture_id}")
def get_lecture_details(
    lecture_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details for a specific lecture"""
    lecture = get_lecture_by_id(db, lecture_id, current_user.id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    return lecture

@router.post("/{lecture_id}/ask", response_model=AnswerResponse)
async def ask(
    lecture_id: str, 
    payload: QuestionRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this lecture
    if not verify_lecture_ownership(db, lecture_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Use LangGraph workflow for enhanced Q&A
        result = await run_lecture_qa(lecture_id, payload.question)
        
        if result["error"]:
            # Fallback to original method if LangGraph fails
            vector_store = load_index(lecture_id)
            answer, sources = ask_question(vector_store, payload.question, lecture_id)
        else:
            answer = result["answer"]
            sources = result["sources"]

        # Convert sources to TimestampSource format
        timestamp_sources = []
        for source in sources:
            if isinstance(source, dict) and "start_time" in source:
                timestamp_sources.append(TimestampSource(**source))
            else:
                # Fallback for simple text sources
                timestamp_sources.append(TimestampSource(
                    text=source.get("text", str(source)),
                    start_time=0.0,
                    end_time=0.0,
                    start_str="00:00:00.00",
                    end_str="00:00:00.00",
                    video_timestamp="0s"
                ))

        return {
            "answer": answer,
            "sources": timestamp_sources
        }
    except Exception as e:
        # Final fallback to original method
        vector_store = load_index(lecture_id)
        answer, sources = ask_question(vector_store, payload.question, lecture_id)
        
        # Convert sources to TimestampSource format
        timestamp_sources = []
        for source in sources:
            if isinstance(source, dict) and "start_time" in source:
                timestamp_sources.append(TimestampSource(**source))
            else:
                timestamp_sources.append(TimestampSource(
                    text=source.get("text", str(source)),
                    start_time=0.0,
                    end_time=0.0,
                    start_str="00:00:00.00",
                    end_str="00:00:00.00",
                    video_timestamp="0s"
                ))

        return {
            "answer": answer,
            "sources": timestamp_sources
        }

@router.get("/{lecture_id}/transcript", response_model=TranscriptResponse)
def get_transcript(
    lecture_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this lecture
    if not verify_lecture_ownership(db, lecture_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    transcript = load_transcript(lecture_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    segments = parse_transcript_with_timestamps(transcript)
    total_duration = segments[-1].end_time if segments else 0.0
    
    transcript_segments = [
        TranscriptSegment(
            start_time=seg.start_time,
            end_time=seg.end_time,
            text=seg.text,
            start_str=seg.start_str,
            end_str=seg.end_str
        ) for seg in segments
    ]
    
    return TranscriptResponse(
        segments=transcript_segments,
        total_duration=total_duration
    )

@router.get("/{lecture_id}/search")
def search_transcript(
    lecture_id: str, 
    q: str, 
    limit: int = 5,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this lecture
    if not verify_lecture_ownership(db, lecture_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    transcript = load_transcript(lecture_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    segments = parse_transcript_with_timestamps(transcript)
    relevant_segments = find_relevant_segments(q, segments, limit)
    
    results = []
    for seg in relevant_segments:
        results.append({
            "text": seg.text,
            "start_time": seg.start_time,
            "end_time": seg.end_time,
            "start_str": seg.start_str,
            "end_str": seg.end_str,
            "video_timestamp": seg.start_str
        })
    
    return {"results": results, "query": q, "total_found": len(results)}

@router.post("/{lecture_id}/pdf", response_model=PDFResponse)
async def generate_pdf(
    lecture_id: str, 
    payload: PDFRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this lecture
    lecture = get_lecture_by_id(db, lecture_id, current_user.id)
    if not lecture:
        raise HTTPException(status_code=403, detail="Access denied")
    
    os.makedirs(PDF_DIR, exist_ok=True)
    
    if payload.type == "transcript":
        transcript = load_transcript(lecture_id)
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        pdf_path = generate_transcript_pdf(transcript, lecture_id)
    elif payload.type == "summary":
        # Use stored summary if available, otherwise generate it
        if lecture.summary:
            summary = lecture.summary
        else:
            transcript = load_transcript(lecture_id)
            if not transcript:
                raise HTTPException(status_code=404, detail="Transcript not found")
            summary = generate_chunked_summary(transcript)
            # Update the lecture record with the generated summary
            lecture.summary = summary
            db.commit()
        
        pdf_path = generate_summary_pdf(summary, lecture_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid PDF type. Use 'transcript' or 'summary'")
    
    filename = os.path.basename(pdf_path)
    return {"pdf_path": pdf_path, "filename": filename}

@router.get("/{lecture_id}/summary")
async def get_summary(
    lecture_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this lecture
    lecture = get_lecture_by_id(db, lecture_id, current_user.id)
    if not lecture:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Use LangGraph workflow for enhanced summarization
        result = await run_lecture_summarization(lecture_id)
        
        if result["error"] or not result["summary"]:
            # Fallback to original method if LangGraph fails
            if lecture.summary:
                return {"summary": lecture.summary}
            
            transcript = load_transcript(lecture_id)
            if not transcript:
                raise HTTPException(status_code=404, detail="Transcript not found")
            
            summary = generate_chunked_summary(transcript)
            
            # Store the generated summary for future use
            lecture.summary = summary
            db.commit()
            
            return {"summary": summary}
        else:
            # Update stored summary with LangGraph generated one
            lecture.summary = result["summary"]
            db.commit()
            
            return {
                "summary": result["summary"],
                "key_topics": result["key_topics"],
                "important_timestamps": result["timestamps"]
            }
    except Exception as e:
        # Final fallback to original method
        if lecture.summary:
            return {"summary": lecture.summary}
        
        transcript = load_transcript(lecture_id)
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        summary = generate_chunked_summary(transcript)
        
        # Store the generated summary for future use
        lecture.summary = summary
        db.commit()
        
        return {"summary": summary}

@router.post("/multi-search", response_model=MultiLectureSearchResponse)
async def multi_lecture_search(
    payload: MultiLectureSearchRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search across multiple lectures using LangGraph workflow"""
    try:
        # Verify user owns all specified lectures
        user_lecture_ids = get_user_lecture_ids(db, current_user.id)
        invalid_lectures = set(payload.lecture_ids) - set(user_lecture_ids)
        
        if invalid_lectures:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied to lectures: {list(invalid_lectures)}"
            )
        
        # Use LangGraph workflow for multi-lecture search
        result = await run_multi_lecture_search(payload.query, payload.lecture_ids)
        
        if result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return MultiLectureSearchResponse(
            results=result["results"][:payload.limit],
            consolidated_answer=result["consolidated_answer"],
            total_found=len(result["results"]),
            query=payload.query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-lecture search failed: {str(e)}")

@router.get("/{lecture_id}/pdf/{filename}")
async def download_pdf(
    lecture_id: str, 
    filename: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this lecture
    if not verify_lecture_ownership(db, lecture_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    pdf_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename
    )

@router.put("/{lecture_id}", response_model=dict)
async def update_lecture_endpoint(
    lecture_id: str,
    payload: LectureUpdateRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update lecture details"""
    try:
        updated_lecture = update_lecture(
            db, lecture_id, current_user.id, 
            title=payload.title, 
            course_id=payload.course_id
        )
        
        if not updated_lecture:
            raise HTTPException(status_code=404, detail="Lecture not found or access denied")
        
        return {
            "lecture_id": updated_lecture.lecture_id,
            "title": updated_lecture.title,
            "course_id": updated_lecture.course_id,
            "message": "Lecture updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lecture: {str(e)}")

@router.delete("/{lecture_id}", response_model=DeleteResponse)
async def delete_lecture_endpoint(
    lecture_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a lecture and all its associated data"""
    try:
        # Get lecture details for cleanup
        lecture = get_lecture_by_id(db, lecture_id, current_user.id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Delete lecture from database
        success = delete_lecture(db, lecture_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete lecture")
        
        # Clean up files
        import os
        from app.config import LECTURE_DIR, INDEX_DIR, PDF_DIR
        
        # Delete audio/video file
        for file in os.listdir(LECTURE_DIR):
            if file.startswith(lecture_id):
                file_path = os.path.join(LECTURE_DIR, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # Delete transcript file
        transcript_path = os.path.join(LECTURE_DIR, f"{lecture_id}_transcript.txt")
        if os.path.exists(transcript_path):
            os.remove(transcript_path)
        
        # Delete duration file
        duration_path = os.path.join(LECTURE_DIR, f"{lecture_id}_duration.txt")
        if os.path.exists(duration_path):
            os.remove(duration_path)
        
        # Delete Qdrant collection
        try:
            from app.db.qdrant_store import qdrant_store
            collection_name = f"lecture_{lecture_id}"
            qdrant_store.delete_collection(collection_name)
        except Exception:
            # Continue even if vector store cleanup fails
            pass
        
        # Delete PDF files
        for file in os.listdir(PDF_DIR):
            if file.startswith(lecture_id) and file.endswith('.pdf'):
                pdf_path = os.path.join(PDF_DIR, file)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
        
        return DeleteResponse(
            message="Lecture and all associated data deleted successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete lecture: {str(e)}")
