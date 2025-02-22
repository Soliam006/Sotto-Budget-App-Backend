from fastapi import (APIRouter, HTTPException, Depends)
from app.models.response import Response
from app.models.user import User, UserRole, Admin, Worker, Client, UserCreate, UserUpdate, UserOut, UsersOut
import app.crud.user as crud
from sqlmodel import Session, select
from app.core.database import get_session

router = APIRouter()

@router.get("/", response_model=Response)
def get_first_user(session: Session = Depends(get_session)):
    result: User = crud.get_user(session=session, user_id=1)
    if result:
        return Response(statusCode=200, data=result, message="User found")
    return Response(statusCode=404, data=None, message="User not found")

# Endpoint para obtener todos los usuarios
@router.get("/all",
            response_model=UsersOut)
def get_all_users(session: Session = Depends(get_session)):
    users = crud.get_all_users(session=session)

    users_out = [
        UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            language_preference=user.language_preference
        ) for user in users
    ]

    return UsersOut(users=users_out)


@router.get("/{user_id}")
async def read_user(user_id: int, session: Session = Depends(get_session)):
    user = crud.get_user(session=session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/")
async def create_user(new_user: UserCreate, session: Session = Depends(get_session)):
    user = crud.create_user(session=session, user_create=new_user)
    if user is None:
        raise HTTPException(status_code=400, detail="User not created")
    return user