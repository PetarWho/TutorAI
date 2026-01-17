from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CourseResponse(CourseBase):
    id: int
    user_id: int
    created_at: datetime
    lecture_count: int = 0
    
    class Config:
        from_attributes = True

class CourseLectureAdd(BaseModel):
    lecture_id: str

class MultiLectureSearchRequest(BaseModel):
    query: str
    course_id: Optional[int] = None  # If provided, search within course only
    limit: int = 10

class MultiLectureSource(BaseModel):
    lecture_id: str
    lecture_filename: str
    text: str
    start_time: float
    end_time: float
    start_str: str
    end_str: str
    video_timestamp: str
    course_name: Optional[str] = None
