from fastapi import (APIRouter, HTTPException, Depends, Form)
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user, get_current_active_superuser
from app.models.follow import FollowOut
from app.models.response import Response
from app.models.user import User, UserRegister, UserUpdate, UserOut, UsersOut, UserRole, LoginForm
import app.crud.user as crud
import app.crud.follow as follow_crud
from sqlmodel import Session
from app.core.database import get_session
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from app.core.security import authenticate_user, authenticate_user_with_email

router = APIRouter()

# -------------------------------- GETTERS --------------------------------
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
                id=user.id, name=user.name, username=user.username, email=user.email,
                role=user.role, phone=user.phone, location=user.location,
                description=user.description, language_preference=user.language_preference
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


@router.get("/userInDB/{user_id}", response_model=Response)
async def read_user_in_db(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_superuser)):
    user = crud.get_user_in_db(session=session, user_id=user_id)
    if user is None:
        return Response(statusCode=404, data=None, message="User not found")
    return Response(statusCode=200, data=user, message="User found")


@router.get("/get_user_client/{user_id}", response_model=Response)
async def get_user_client(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    client = crud.get_user_client(session=session, user_id=user_id)
    if client is None:
        return Response(statusCode=404, data=None, message="User not found")

    list_availabilities = crud.get_availabilities(session=session, client_id=client.client_id)

    return Response(statusCode=200, data={"user": client, "availabilities": list_availabilities}, message="User found")

# ----------------------------- POSTS --------------------------------


@router.post("/", response_model=Response)
async def create_user(new_user: UserRegister, session: Session = Depends(get_session)):
    try:
        new_user = crud.create_user(session=session, user_data=new_user)
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    return Response(statusCode=200, data=new_user, message="User created")


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    try:
        user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token_username", response_model=Response)
async def login_for_access_token(credentials: LoginForm,
                                 session: Session = Depends(get_session)):
    try:
        user = authenticate_user(session=session, username=credentials.username, password=credentials.password)
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    # Si el User está autenticado, buscamos si tiene un perfil de Admin, Worker o Client
    if user.role == UserRole.ADMIN:
        user_role = crud.get_user_admin(session=session, user_id=user.id)
    elif user.role == UserRole.WORKER:
        user_role = crud.get_user_worker(session=session, user_id=user.id)
    else:
        user_role = crud.get_user_client(session=session, user_id=user.id)
        list_availabilities = crud.get_availabilities(session=session, client_id=user_role.client_id)
        return Response(statusCode=200,
                        data={ "access_token": access_token,
                               "token_type": "bearer",
                               "user": user_role,
                               "availabilities": list_availabilities},
                        message="Welcome Back "+user_role.username)

    return Response(statusCode=200,
                    data={ "access_token": access_token,
                           "token_type": "bearer",
                           "user": user_role},
                    message= "Welcome Back "+user_role.username)


@router.post("/token_email")
async def login_for_access_token(credentials: LoginForm,
                                 session: Session = Depends(get_session)):
    try:
        user = authenticate_user_with_email(session=session, email=credentials.email, password=credentials.password)
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    # Si el User está autenticado, buscamos si tiene un perfil de Admin, Worker o Client
    if user.role == UserRole.ADMIN:
        user_role = crud.get_user_admin(session=session, user_id=user.id)
    elif user.role == UserRole.WORKER:
        user_role = crud.get_user_worker(session=session, user_id=user.id)
    else:
        user_role = crud.get_user_client(session=session, user_id=user.id)
        list_availabilities = crud.get_availabilities(session=session, client_id=user_role.client_id)
        return Response(statusCode=200,
                        data={ "access_token": access_token,
                               "token_type": "bearer",
                               "user": user_role,
                               "availabilities": list_availabilities},
                        message="Welcome Back "+user_role.username)

    return Response(statusCode=200,
                    data={ "access_token": access_token,
                           "token_type": "bearer",
                           "user": user_role},
                    message= "Welcome Back "+user_role.username)


# ----------------------------- PUTS --------------------------------
@router.put("/{user_id}", response_model=Response)
async def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    try:
        result = crud.update_user(session=session, user_id=user_id, user=user)
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    if result is None:
        return Response(statusCode=404, data=None, message="User not found")
    return Response(statusCode=200, data=result, message="User updated")

# ----------------------------- DELETES --------------------------------
@router.delete("/{user_id}", response_model=Response)
async def delete_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = crud.delete_user(session=session, user_id=user_id)
    if result is None:
        return Response(statusCode=404, data=None, message="User not found")
    return Response(statusCode=200, data=result, message="User deleted")
