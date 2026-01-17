from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import json

from app.services.ollama import get_llm
from app.services.transcription import load_transcript
from app.services.timestamp_service import parse_transcript_with_timestamps, format_timestamp_for_video
from app.db.qdrant_store import qdrant_store
from app.config import TOP_K


class LectureProcessingState(BaseModel):
    """State for lecture processing workflow"""
    lecture_id: str = Field(description="ID of the lecture being processed")
    transcript: Optional[str] = Field(default=None, description="Full transcript text")
    question: Optional[str] = Field(default=None, description="User question")
    context_chunks: List[str] = Field(default_factory=list, description="Relevant context chunks")
    answer: Optional[str] = Field(default=None, description="Generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source information")
    error: Optional[str] = Field(default=None, description="Error message if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MultiLectureState(BaseModel):
    """State for multi-lecture search workflow"""
    query: str = Field(description="Search query")
    lecture_ids: List[str] = Field(description="List of lecture IDs to search")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Search results")
    consolidated_answer: Optional[str] = Field(default=None, description="Consolidated answer")
    error: Optional[str] = Field(default=None, description="Error message if any")


class SummarizationState(BaseModel):
    """State for lecture summarization workflow"""
    lecture_id: str = Field(description="ID of the lecture to summarize")
    transcript: Optional[str] = Field(default=None, description="Full transcript text")
    summary: Optional[str] = Field(default=None, description="Generated summary")
    key_topics: List[str] = Field(default_factory=list, description="Key topics extracted")
    timestamps: List[Dict[str, Any]] = Field(default_factory=list, description="Important timestamps")
    error: Optional[str] = Field(default=None, description="Error message if any")


def load_transcript_node(state: LectureProcessingState) -> LectureProcessingState:
    """Load transcript for the lecture"""
    try:
        transcript = load_transcript(state.lecture_id)
        if not transcript:
            state.error = f"Transcript not found for lecture {state.lecture_id}"
            return state
        
        state.transcript = transcript
        return state
    except Exception as e:
        state.error = f"Error loading transcript: {str(e)}"
        return state


def retrieve_relevant_chunks(state: LectureProcessingState) -> LectureProcessingState:
    """Retrieve relevant chunks using vector search"""
    try:
        if not state.question:
            state.error = "No question provided"
            return state
        
        collection_name = f"lecture_{state.lecture_id}"
        
        # Check if collection exists
        collection_info = qdrant_store.get_collection_info(collection_name)
        if collection_info is None:
            # Fallback to chunking the transcript
            if state.transcript:
                chunks = [state.transcript[i:i+1000] for i in range(0, len(state.transcript), 2000)][:5]
                state.context_chunks = chunks
            return state
        
        # Search for relevant documents
        docs = qdrant_store.similarity_search(
            collection_name=collection_name,
            query=state.question,
            k=TOP_K
        )
        
        state.context_chunks = [doc.page_content for doc in docs]
        return state
    except Exception as e:
        state.error = f"Error retrieving chunks: {str(e)}"
        return state


def generate_answer_node(state: LectureProcessingState) -> LectureProcessingState:
    """Generate answer using LLM with context"""
    try:
        if not state.question:
            state.error = "No question provided"
            return state
        
        llm = get_llm()
        
        # Prepare context
        context = "\n\n".join(state.context_chunks) if state.context_chunks else state.transcript or ""
        
        prompt = f"""
        Based on the following lecture transcript, please answer the user's question comprehensively.
        Use the provided context to give a detailed and accurate answer.
        
        Context:
        {context}
        
        User Question: {state.question}
        
        Please provide a comprehensive answer based on the lecture content above:
        """
        
        response = llm.invoke(prompt)
        state.answer = response.strip()
        return state
    except Exception as e:
        state.error = f"Error generating answer: {str(e)}"
        return state


def extract_sources_node(state: LectureProcessingState) -> LectureProcessingState:
    """Extract source information with timestamps"""
    try:
        if not state.transcript:
            return state
        
        segments = parse_transcript_with_timestamps(state.transcript)
        sources = []
        
        for chunk in state.context_chunks:
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
        
        state.sources = sources
        return state
    except Exception as e:
        state.error = f"Error extracting sources: {str(e)}"
        return state


def search_lecture_node(state: MultiLectureState, lecture_id: str) -> List[Dict[str, Any]]:
    """Search within a single lecture"""
    try:
        collection_name = f"lecture_{lecture_id}"
        
        # Check if collection exists
        collection_info = qdrant_store.get_collection_info(collection_name)
        if collection_info is None:
            return []
        
        # Search for relevant documents
        docs = qdrant_store.similarity_search(
            collection_name=collection_name,
            query=state.query,
            k=TOP_K
        )
        
        # Load transcript to get timestamp information
        transcript = load_transcript(lecture_id)
        results = []
        
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
                            "relevance_score": doc.metadata.get("score", 0.0)
                        }
                        results.append(result)
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
                    results.append(result)
        
        return results
    except Exception as e:
        return []


def search_all_lectures_node(state: MultiLectureState) -> MultiLectureState:
    """Search across all specified lectures"""
    all_results = []
    
    for lecture_id in state.lecture_ids:
        results = search_lecture_node(state, lecture_id)
        all_results.extend(results)
    
    # Sort by relevance score and limit results
    if all_results and any("relevance_score" in r for r in all_results):
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    state.results = all_results[:20]  # Limit to top 20 results
    return state


def consolidate_answer_node(state: MultiLectureState) -> MultiLectureState:
    """Consolidate search results into a comprehensive answer"""
    try:
        if not state.results:
            state.consolidated_answer = "No relevant information found across the lectures."
            return state
        
        llm = get_llm()
        
        # Prepare context from top results
        top_results = state.results[:10]
        context = "\n\n".join([
            f"Lecture {result['lecture_id']} ({result['video_timestamp']}): {result['text']}"
            for result in top_results
        ])
        
        prompt = f"""
        Based on the following search results from multiple lectures, provide a comprehensive answer to the user's query.
        
        Query: {state.query}
        
        Search Results:
        {context}
        
        Please provide a consolidated answer that synthesizes information from all relevant lectures:
        """
        
        response = llm.invoke(prompt)
        state.consolidated_answer = response.strip()
        return state
    except Exception as e:
        state.error = f"Error consolidating answer: {str(e)}"
        return state


def load_transcript_for_summary(state: SummarizationState) -> SummarizationState:
    """Load transcript for summarization"""
    try:
        transcript = load_transcript(state.lecture_id)
        if not transcript:
            state.error = f"Transcript not found for lecture {state.lecture_id}"
            return state
        
        state.transcript = transcript
        return state
    except Exception as e:
        state.error = f"Error loading transcript: {str(e)}"
        return state


def generate_summary_node(state: SummarizationState) -> SummarizationState:
    """Generate comprehensive summary"""
    try:
        if not state.transcript:
            state.error = "No transcript available for summarization"
            return state
        
        llm = get_llm()
        
        prompt = f"""
        Please provide a comprehensive summary of the following lecture transcript. Include:
        1. Main topics covered
        2. Key concepts and definitions
        3. Important examples or demonstrations
        4. Overall themes and conclusions
        
        Transcript:
        {state.transcript}
        
        Summary:
        """
        
        response = llm.invoke(prompt)
        state.summary = response.strip()
        return state
    except Exception as e:
        state.error = f"Error generating summary: {str(e)}"
        return state


def extract_key_topics_node(state: SummarizationState) -> SummarizationState:
    """Extract key topics from the lecture"""
    try:
        if not state.transcript:
            return state
        
        llm = get_llm()
        
        prompt = f"""
        Based on the following lecture transcript, extract the main topics and key concepts discussed.
        Return them as a comma-separated list.
        
        Transcript:
        {state.transcript}
        
        Key topics:
        """
        
        response = llm.invoke(prompt)
        topics = [topic.strip() for topic in response.split(',')]
        state.key_topics = topics
        return state
    except Exception as e:
        state.error = f"Error extracting topics: {str(e)}"
        return state


def extract_important_timestamps_node(state: SummarizationState) -> SummarizationState:
    """Extract important timestamps from the lecture"""
    try:
        if not state.transcript:
            return state
        
        segments = parse_transcript_with_timestamps(state.transcript)
        llm = get_llm()
        
        # Sample key segments for analysis
        sample_segments = segments[::max(1, len(segments)//20)]  # Sample every 20th segment
        
        segment_texts = []
        for segment in sample_segments:
            segment_texts.append(f"{segment.start_str}: {segment.text[:200]}...")
        
        prompt = f"""
        Based on these lecture segments, identify the most important moments that would be valuable for quick navigation.
        Look for topic introductions, key definitions, important examples, or conclusions.
        
        Segments:
        {chr(10).join(segment_texts)}
        
        Return the important timestamps as a JSON array with format: [{"timestamp": "MM:SS", "description": "Description"}]
        """
        
        response = llm.invoke(prompt)
        try:
            timestamps = json.loads(response)
            state.timestamps = timestamps
        except json.JSONDecodeError:
            # Fallback to simple extraction
            state.timestamps = []
        
        return state
    except Exception as e:
        state.error = f"Error extracting timestamps: {str(e)}"
        return state


# Create the workflow graphs
def create_lecture_qa_workflow() -> StateGraph:
    """Create a workflow for lecture Q&A"""
    workflow = StateGraph(LectureProcessingState)
    
    # Add nodes
    workflow.add_node("load_transcript", load_transcript_node)
    workflow.add_node("retrieve_chunks", retrieve_relevant_chunks)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("extract_sources", extract_sources_node)
    
    # Add edges
    workflow.set_entry_point("load_transcript")
    workflow.add_edge("load_transcript", "retrieve_chunks")
    workflow.add_edge("retrieve_chunks", "generate_answer")
    workflow.add_edge("generate_answer", "extract_sources")
    workflow.add_edge("extract_sources", END)
    
    return workflow.compile()


def create_multi_lecture_search_workflow() -> StateGraph:
    """Create a workflow for multi-lecture search"""
    workflow = StateGraph(MultiLectureState)
    
    # Add nodes
    workflow.add_node("search_all_lectures", search_all_lectures_node)
    workflow.add_node("consolidate_answer", consolidate_answer_node)
    
    # Add edges
    workflow.set_entry_point("search_all_lectures")
    workflow.add_edge("search_all_lectures", "consolidate_answer")
    workflow.add_edge("consolidate_answer", END)
    
    return workflow.compile()


def create_summarization_workflow() -> StateGraph:
    """Create a workflow for lecture summarization"""
    workflow = StateGraph(SummarizationState)
    
    # Add nodes
    workflow.add_node("load_transcript", load_transcript_for_summary)
    workflow.add_node("generate_summary", generate_summary_node)
    workflow.add_node("extract_topics", extract_key_topics_node)
    workflow.add_node("extract_timestamps", extract_important_timestamps_node)
    
    # Add edges
    workflow.set_entry_point("load_transcript")
    workflow.add_edge("load_transcript", "generate_summary")
    workflow.add_edge("load_transcript", "extract_topics")
    workflow.add_edge("load_transcript", "extract_timestamps")
    workflow.add_edge("generate_summary", END)
    workflow.add_edge("extract_topics", END)
    workflow.add_edge("extract_timestamps", END)
    
    return workflow.compile()


# Instantiate the workflows
lecture_qa_workflow = create_lecture_qa_workflow()
multi_lecture_search_workflow = create_multi_lecture_search_workflow()
summarization_workflow = create_summarization_workflow()


async def run_lecture_qa(lecture_id: str, question: str) -> Dict[str, Any]:
    """Run the lecture Q&A workflow"""
    initial_state = LectureProcessingState(
        lecture_id=lecture_id,
        question=question
    )
    
    result = await lecture_qa_workflow.ainvoke(initial_state)
    
    return {
        "answer": result.answer,
        "sources": result.sources,
        "error": result.error
    }


async def run_multi_lecture_search(query: str, lecture_ids: List[str]) -> Dict[str, Any]:
    """Run the multi-lecture search workflow"""
    initial_state = MultiLectureState(
        query=query,
        lecture_ids=lecture_ids
    )
    
    result = await multi_lecture_search_workflow.ainvoke(initial_state)
    
    return {
        "results": result.results,
        "consolidated_answer": result.consolidated_answer,
        "error": result.error
    }


async def run_lecture_summarization(lecture_id: str) -> Dict[str, Any]:
    """Run the lecture summarization workflow"""
    initial_state = SummarizationState(
        lecture_id=lecture_id
    )
    
    result = await summarization_workflow.ainvoke(initial_state)
    
    return {
        "summary": result.summary,
        "key_topics": result.key_topics,
        "timestamps": result.timestamps,
        "error": result.error
    }
