from fastapi import (APIRouter, HTTPException, Depends)
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user, oauth2_scheme
from app.models.response import Response
from app.models.user import User, UserRole, Admin, Worker, Client, UserRegister, UserUpdate, UserOut, UsersOut
import app.crud.user as crud
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from app.core.security import authenticate_user, authenticate_user_with_email

router = APIRouter()


@router.get("/me", response_model=Response)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return Response(statusCode=200, data=current_user, message="User found")


@router.get("/", response_model=Response)
def get_first_user(session: Session = Depends(get_session)):
    result: UserOut = crud.get_user(session=session, user_id=1)
    if result:
        return Response(statusCode=200, data=result, message="User found")
    return Response(statusCode=404, data=None, message="User not found")

# Endpoint para obtener todos los usuarios
@router.get("/all",
            response_model=Response)
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    users = crud.get_all_users(session=session)

    if not users:
        return Response(statusCode=404, data=None, message="Users not found")

    try:
        users_out = [
            UserOut(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                language_preference=user.language_preference
            ) for user in users
        ]
    except Exception as e:
        return Response(statusCode=400, data=None, message="Error parsing users")

    return Response(statusCode=200, data=UsersOut(users=users_out), message="Users found")


@router.get("/{user_id}", response_model=Response)
async def read_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user = crud.get_user(session=session, user_id=user_id)
    if user is None:
        return Response(statusCode=404, data=None, message="User not found")
    return Response(statusCode=200, data=user, message="User found")


@router.post("/", response_model=Response)
async def create_user(new_user: UserRegister, session: Session = Depends(get_session)):
    user = crud.create_user(session=session, user_create=new_user)
    if user is None:
        return Response(statusCode=400, data=None, message="Error creating user")
    return Response(statusCode=200, data=user, message="User created")


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    if not user:
        return Response(statusCode=400, data=None, message="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("token/{email}")
async def login_for_access_token(email: str, password: str, session: Session = Depends(get_session)):
    user = authenticate_user_with_email(session=session, email=email, password=password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.id}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/{user_id}", response_model=Response)
async def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = crud.update_user(session=session, user_id=user_id, user=user)
    if result is None:
        return Response(statusCode=404, data=None, message="User not found")
    return Response(statusCode=200, data=result, message="User updated")