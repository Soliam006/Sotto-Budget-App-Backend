""" Main API routes definition """
from fastapi import APIRouter
from app.api.routes import users
from app.api.routes import follows

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(follows.router, prefix="/follows", tags=["follows"])