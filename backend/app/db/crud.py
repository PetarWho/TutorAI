from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from passlib.context import CryptContext
from app.db.models import User, Course, Lecture
from app.models.user import UserCreate, UserResponse
from app.models.course import CourseCreate, CourseResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        # Ensure password is not too long for bcrypt
        if len(password.encode('utf-8')) > 72:
            raise ValueError("Password cannot be longer than 72 bytes when encoded as UTF-8")
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Error hashing password: {e}")
        raise ValueError(f"Password hashing failed: {str(e)}")

# User CRUD operations
def create_user(db: Session, user: UserCreate) -> UserResponse:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        created_at=db_user.created_at
    )

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# Course CRUD operations
def create_course(db: Session, course: CourseCreate, user_id: int) -> Course:
    """Create a new course"""
    db_course = Course(
        name=course.name,
        description=course.description,
        user_id=user_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_user_courses(db: Session, user_id: int) -> List[Course]:
    """Get all courses for a user with lecture counts"""
    return db.query(Course).filter(Course.user_id == user_id).all()

def get_course_by_id(db: Session, course_id: int, user_id: int) -> Optional[Course]:
    """Get course by ID and verify ownership"""
    return db.query(Course).filter(
        and_(Course.id == course_id, Course.user_id == user_id)
    ).first()

# Lecture CRUD operations
def create_lecture_record(
    db: Session, 
    lecture_id: str, 
    title: str,
    user_id: int, 
    filename: str, 
    course_id: Optional[int] = None,
    duration: Optional[float] = None,
    qdrant_collection: Optional[str] = None,
    summary: Optional[str] = None
) -> Lecture:
    """Create a lecture record"""
    db_lecture = Lecture(
        lecture_id=lecture_id,
        title=title,
        user_id=user_id,
        course_id=course_id,
        filename=filename,
        duration=duration,
        summary=summary,
        qdrant_collection=qdrant_collection or f"lecture_{lecture_id}"
    )
    db.add(db_lecture)
    db.commit()
    db.refresh(db_lecture)
    return db_lecture

def get_user_lectures(db: Session, user_id: int, course_id: Optional[int] = None) -> List[Lecture]:
    """Get all lectures for a user, optionally filtered by course"""
    query = db.query(Lecture).filter(Lecture.user_id == user_id)
    if course_id is not None:
        query = query.filter(Lecture.course_id == course_id)
    return query.order_by(Lecture.upload_date.desc()).all()

def get_lecture_by_id(db: Session, lecture_id: str, user_id: int) -> Optional[Lecture]:
    """Get lecture by ID and verify ownership"""
    return db.query(Lecture).filter(
        and_(Lecture.lecture_id == lecture_id, Lecture.user_id == user_id)
    ).first()

def update_lecture_course(db: Session, lecture_id: str, course_id: int, user_id: int) -> bool:
    """Update lecture's course association"""
    lecture = get_lecture_by_id(db, lecture_id, user_id)
    if not lecture:
        return False
    
    lecture.course_id = course_id
    db.commit()
    return True

def get_user_lecture_ids(db: Session, user_id: int, course_id: Optional[int] = None) -> List[str]:
    """Get all lecture IDs for a user, optionally filtered by course"""
    query = db.query(Lecture.lecture_id).filter(Lecture.user_id == user_id)
    if course_id is not None:
        query = query.filter(Lecture.course_id == course_id)
    result = query.all()
    return [row.lecture_id for row in result]

def verify_lecture_ownership(db: Session, lecture_id: str, user_id: int) -> bool:
    """Verify that a user owns a specific lecture"""
    lecture = get_lecture_by_id(db, lecture_id, user_id)
    return lecture is not None

def verify_course_ownership(db: Session, course_id: int, user_id: int) -> bool:
    """Verify that a user owns a specific course"""
    course = get_course_by_id(db, course_id, user_id)
    return course is not None

def update_lecture(db: Session, lecture_id: str, user_id: int, title: Optional[str] = None, course_id: Optional[int] = None) -> Optional[Lecture]:
    """Update lecture details"""
    lecture = get_lecture_by_id(db, lecture_id, user_id)
    if not lecture:
        return None
    
    if title is not None:
        lecture.title = title
    
    if course_id is not None:
        # Verify user owns the course if course_id is provided
        if course_id != 0:  # 0 means remove from course
            if not verify_course_ownership(db, course_id, user_id):
                return None
        lecture.course_id = course_id if course_id != 0 else None
    
    db.commit()
    db.refresh(lecture)
    return lecture

def delete_lecture(db: Session, lecture_id: str, user_id: int) -> bool:
    """Delete a lecture and all its associated data"""
    lecture = get_lecture_by_id(db, lecture_id, user_id)
    if not lecture:
        return False
    
    try:
        # Delete the lecture (cascade will handle related records)
        db.delete(lecture)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e

def update_course(db: Session, course_id: int, user_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Course]:
    """Update course details"""
    course = get_course_by_id(db, course_id, user_id)
    if not course:
        return None
    
    if name is not None:
        course.name = name
    
    if description is not None:
        course.description = description
    
    db.commit()
    db.refresh(course)
    return course

def delete_course(db: Session, course_id: int, user_id: int) -> bool:
    """Delete a course and unassociate all lectures"""
    course = get_course_by_id(db, course_id, user_id)
    if not course:
        return False
    
    try:
        # First, unassociate all lectures from this course
        db.query(Lecture).filter(Lecture.course_id == course_id).update({"course_id": None})
        
        # Then delete the course
        db.delete(course)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
