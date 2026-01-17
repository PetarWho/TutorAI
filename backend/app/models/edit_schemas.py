from pydantic import BaseModel
from typing import List, Optional


class LectureUpdateRequest(BaseModel):
    title: Optional[str] = None
    course_id: Optional[int] = None


class CourseUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DeleteResponse(BaseModel):
    message: str
    success: bool
