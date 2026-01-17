from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.crud import (
    create_course, get_user_courses, update_lecture_course, 
    get_course_by_id, verify_course_ownership, verify_lecture_ownership,
    get_user_lecture_ids, update_course, delete_course
)
from app.db.qdrant_store import search_lectures
from app.models.course import (
    CourseCreate, CourseResponse, CourseLectureAdd, 
    MultiLectureSearchRequest, MultiLectureSource
)
from app.models.edit_schemas import CourseUpdateRequest, DeleteResponse
from app.models.user import UserResponse
from app.db.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=CourseResponse)
def create_course_endpoint(
    course: CourseCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new course"""
    try:
        db_course = create_course(db, course, current_user.id)
        return CourseResponse(
            id=db_course.id,
            name=db_course.name,
            description=db_course.description,
            user_id=db_course.user_id,
            created_at=db_course.created_at,
            lecture_count=0  # Will be updated when lectures are added
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CourseResponse])
def get_courses(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all courses for the current user"""
    courses = get_user_courses(db, current_user.id)
    
    # Convert to response format with lecture counts
    course_responses = []
    for course in courses:
        lecture_count = len(course.lectures) if course.lectures else 0
        course_responses.append(CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            user_id=course.user_id,
            created_at=course.created_at,
            lecture_count=lecture_count
        ))
    
    return course_responses

@router.post("/{course_id}/lectures")
def add_lecture_to_course_endpoint(
    course_id: int,
    request: CourseLectureAdd,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a lecture to a course"""
    # Verify user owns the course
    if not verify_course_ownership(db, course_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify user owns the lecture
    if not verify_lecture_ownership(db, request.lecture_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = update_lecture_course(db, request.lecture_id, course_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    return {"message": "Lecture added to course successfully"}

@router.get("/{course_id}/lectures")
def get_course_lectures_endpoint(
    course_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all lectures in a course"""
    # Verify user owns the course
    if not verify_course_ownership(db, course_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.db.crud import get_user_lectures
    lectures = get_user_lectures(db, current_user.id, course_id)
    return {"lectures": lectures}

@router.post("/search")
def search_multiple_lectures_endpoint(
    request: MultiLectureSearchRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search across multiple lectures (all user lectures or within a specific course)"""
    
    # Get lecture IDs to search
    if request.course_id:
        # Verify user owns the course
        if not verify_course_ownership(db, request.course_id, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        lecture_ids = get_user_lecture_ids(db, current_user.id, request.course_id)
    else:
        # Search across all user lectures
        lecture_ids = get_user_lecture_ids(db, current_user.id)
    
    if not lecture_ids:
        return {"results": [], "query": request.query, "total_found": 0}
    
    # Perform search using Qdrant
    search_results = search_lectures(request.query, lecture_ids, current_user.id, request.limit)
    
    # Get metadata for all lectures
    from app.db.crud import get_user_lectures
    all_lectures = get_user_lectures(db, current_user.id)
    lecture_metadata = {lecture.lecture_id: lecture for lecture in all_lectures}
    
    # Format results with metadata
    formatted_results = []
    for result in search_results:
        lecture = lecture_metadata.get(result["lecture_id"])
        if lecture:
            formatted_result = MultiLectureSource(
                lecture_id=result["lecture_id"],
                lecture_filename=lecture.filename,
                text=result["text"],
                start_time=0.0,  # Will be enhanced with timestamp service
                end_time=0.0,
                start_str="00:00:00.00",
                end_str="00:00:00.00",
                video_timestamp="0s",
                course_name=lecture.course.name if lecture.course else None
            )
            formatted_results.append(formatted_result.dict())
    
    return {
        "results": formatted_results,
        "query": request.query,
        "total_found": len(formatted_results)
    }

@router.put("/{course_id}", response_model=dict)
async def update_course_endpoint(
    course_id: int,
    payload: CourseUpdateRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update course details"""
    try:
        updated_course = update_course(
            db, course_id, current_user.id,
            name=payload.name,
            description=payload.description
        )
        
        if not updated_course:
            raise HTTPException(status_code=404, detail="Course not found or access denied")
        
        return {
            "id": updated_course.id,
            "name": updated_course.name,
            "description": updated_course.description,
            "message": "Course updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update course: {str(e)}")

@router.delete("/{course_id}", response_model=DeleteResponse)
async def delete_course_endpoint(
    course_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a course (lectures will be unassociated but not deleted)"""
    try:
        success = delete_course(db, course_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Course not found or access denied")
        
        return DeleteResponse(
            message="Course deleted successfully. Lectures have been unassociated but not deleted.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete course: {str(e)}")
