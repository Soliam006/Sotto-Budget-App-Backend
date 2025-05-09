""" Main API routes definition """
from fastapi import APIRouter
from app.api.routes import users
from app.api.routes import follows
from app.api.routes import projects
from app.api.routes import tasks

# python -m venv venv
# .\venv\Scripts\activate
# pip install poetry alembic uvicorn fastapi python-jose sqlmodel pydantic_settings pymysql passlib python-multipart bcrypt
api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(follows.router, prefix="/follows", tags=["follows"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

