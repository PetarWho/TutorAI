from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str

class TimestampSource(BaseModel):
    text: str
    start_time: float
    end_time: float
    start_str: str
    end_str: str
    video_timestamp: str  # Formatted for video jumping

class AnswerResponse(BaseModel):
    answer: str
    sources: List[TimestampSource]

class PDFRequest(BaseModel):
    type: str  # 'transcript' or 'summary'

class PDFResponse(BaseModel):
    pdf_path: str
    filename: str

class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    start_str: str
    end_str: str

class TranscriptResponse(BaseModel):
    segments: List[TranscriptSegment]
    total_duration: float
