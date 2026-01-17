from typing import List, Dict, Any
from app.db.qdrant_store import qdrant_store
from app.services.transcription import load_transcript
from app.services.timestamp_service import parse_transcript_with_timestamps, format_timestamp_for_video
from app.config import TOP_K

def search_multiple_lectures(
    query: str, 
    lecture_ids: List[str], 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search across multiple lectures and return ranked results with timestamps
    """
    all_results = []
    
    for lecture_id in lecture_ids:
        try:
            # Use Qdrant to search for relevant documents
            collection_name = f"lecture_{lecture_id}"
            
            # Check if collection exists
            collection_info = qdrant_store.get_collection_info(collection_name)
            if collection_info is None:
                continue
            
            # Search for relevant documents
            docs = qdrant_store.similarity_search(
                collection_name=collection_name,
                query=query,
                k=TOP_K
            )
            
            # Load transcript to get timestamp information
            transcript = load_transcript(lecture_id)
            if transcript:
                segments = parse_transcript_with_timestamps(transcript)
                
                for doc in docs:
                    # Find matching segment for each document
                    for segment in segments:
                        if doc.page_content.strip() in segment.text or segment.text.strip() in doc.page_content:
                            result = {
                                "lecture_id": lecture_id,
                                "text": doc.page_content,
                                "start_time": segment.start_time,
                                "end_time": segment.end_time,
                                "start_str": segment.start_str,
                                "end_str": segment.end_str,
                                "video_timestamp": format_timestamp_for_video(segment.start_time),
                                "relevance_score": doc.metadata.get("score", 0.0)  # Score from vector search metadata
                            }
                            all_results.append(result)
                            break
                    else:
                        # Fallback if no exact match found
                        result = {
                            "lecture_id": lecture_id,
                            "text": doc.page_content,
                            "start_time": 0.0,
                            "end_time": 0.0,
                            "start_str": "00:00:00.00",
                            "end_str": "00:00:00.00",
                            "video_timestamp": "0s",
                            "relevance_score": doc.metadata.get("score", 0.0)
                        }
                        all_results.append(result)
            
        except Exception as e:
            # Skip lectures that can't be loaded (corrupted index, etc.)
            continue
    
    # Sort by relevance score (if available) and limit results
    if all_results and any("relevance_score" in r for r in all_results):
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return all_results[:limit]

def get_lecture_metadata(lecture_ids: List[str]) -> Dict[str, Dict[str, str]]:
    """Get metadata for multiple lectures (filename, course info, etc.)"""
    from sqlalchemy.orm import Session
    from sqlalchemy import and_
    from app.db.database import get_db
    from app.db.models import Lecture
    
    metadata = {}
    
    # Get database session
    db = next(get_db())
    
    try:
        # Query lectures with their course information
        lectures = db.query(Lecture).filter(
            and_(Lecture.lecture_id.in_(lecture_ids))
        ).all()
        
        for lecture in lectures:
            metadata[lecture.lecture_id] = {
                'filename': lecture.filename,
                'course_name': lecture.course.name if lecture.course else None
            }
    finally:
        db.close()
    
    return metadata
