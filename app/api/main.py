""" Main API routes definition """
from fastapi import APIRouter
from app.api.routes import users
from app.api.routes import follows
from app.api.routes import projects
from app.api.routes import tasks
from app.api.routes import teams
from app.api.routes import expenses
from app.api.routes import notifications

# python -m venv venv
# .\venv\Scripts\activate
# pip install poetry alembic uvicorn fastapi python-jose sqlmodel pydantic_settings pymysql passlib python-multipart bcrypt
api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(follows.router, prefix="/follows", tags=["follows"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])   
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

