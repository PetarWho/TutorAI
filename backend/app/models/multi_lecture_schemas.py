from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MultiLectureSearchRequest(BaseModel):
    """Request model for multi-lecture search"""
    query: str = Field(..., description="Search query")
    lecture_ids: List[str] = Field(..., description="List of lecture IDs to search")
    limit: Optional[int] = Field(20, description="Maximum number of results to return")


class MultiLectureSearchResponse(BaseModel):
    """Response model for multi-lecture search"""
    results: List[Dict[str, Any]] = Field(..., description="Search results with timestamps and relevance scores")
    consolidated_answer: Optional[str] = Field(None, description="Consolidated answer from multiple lectures")
    total_found: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="Original search query")
