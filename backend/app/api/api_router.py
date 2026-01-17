from fastapi import APIRouter
from app.api.routes import lectures, health, auth, courses

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(lectures.router, prefix="/lectures", tags=["Lectures"])
