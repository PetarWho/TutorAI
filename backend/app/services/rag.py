from typing import List, Dict, Any, Tuple
from app.services.ollama import get_llm
from app.services.transcription import load_transcript
from app.services.timestamp_service import parse_transcript_with_timestamps, format_timestamp_for_video

def ask_question(vector_store, question: str, lecture_id: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Answer a question using RAG with the full transcript as context
    """
    # Load the full transcript for comprehensive context
    transcript = load_transcript(lecture_id)
    if not transcript:
        return "Transcript not found for this lecture.", []
    
    # Get relevant chunks from vector store
    try:
        docs = vector_store.similarity_search(question, k=5)
        relevant_chunks = [doc.page_content for doc in docs]
    except Exception as e:
        # Fallback to using transcript chunks if vector search fails
        relevant_chunks = [transcript[i:i+1000] for i in range(0, len(transcript), 2000)][:5]
    
    # Combine relevant chunks for context
    context = "\n\n".join(relevant_chunks)
    
    # Generate answer using LLM with full transcript context
    llm = get_llm()
    prompt = f"""
    Based on the following lecture transcript, please answer the user's question comprehensively.
    Use the full transcript context to provide a detailed and accurate answer.
    
    Lecture Transcript:
    {transcript}
    
    User Question: {question}
    
    Please provide a comprehensive answer based on the lecture content above:
    """
    
    try:
        answer = llm.invoke(prompt).strip()
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
    
    # Get timestamp information for sources
    segments = parse_transcript_with_timestamps(transcript)
    sources = []
    
    for chunk in relevant_chunks:
        # Find matching segment for each chunk
        for segment in segments:
            if chunk.strip() in segment.text or segment.text.strip() in chunk:
                source = {
                    "text": segment.text,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "start_str": segment.start_str,
                    "end_str": segment.end_str,
                    "video_timestamp": format_timestamp_for_video(segment.start_time)
                }
                sources.append(source)
                break
    
    return answer, sources