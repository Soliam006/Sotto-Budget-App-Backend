from fastapi import (APIRouter, HTTPException, Depends)

from app.models.user import User, UserRole, Admin, Worker, Client, UserCreate, UserUpdate, UserOut

from sqlmodel import Session, select
from app.core.database import get_session

router = APIRouter()

@router.get("/")
async def read_users():
    users = await User.objects.all()
    return users

@router.get("/{user_id}")
async def read_user(user_id: int):
    user = await User.objects.get(id=user_id)
    return user

@router.post("/")
async def create_user(new_user: UserCreate, session: Session = Depends(get_session)):
    user = create_user_(session=session, user_create=new_user)
    return user


def create_user_(*, session: Session, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user