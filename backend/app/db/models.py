from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lectures = relationship("Lecture", back_populates="user")
    courses = relationship("Course", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="courses")
    lectures = relationship("Lecture", back_populates="course")

class Lecture(Base):
    __tablename__ = "lectures"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float)  # Duration in seconds
    summary = Column(Text)  # Pre-generated summary for quick access
    
    # Qdrant collection name for this lecture
    qdrant_collection = Column(String, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="lectures")
    course = relationship("Course", back_populates="lectures")
