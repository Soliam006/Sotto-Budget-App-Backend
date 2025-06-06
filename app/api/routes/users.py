from fastapi import (APIRouter, HTTPException, Depends, Form)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user, get_current_active_superuser
from app.models.response import Response
from app.models.user import User, UserRegister, UserUpdate, UserOut, UsersOut, UserRole, LoginForm, ClientOut, \
    WorkerOut, AdminOut, FollowOut
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
async def read_users_me(current_user: UserOut = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    try:

        current_user = enrich_user_with_follow_data(session=session, user=current_user)

        current_user = enrich_user_with_role_data(session=session, current_user=current_user)

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )

    return Response(statusCode=200, data=current_user, message="User found")


@router.get("/", response_model=Response)
def get_first_user(session: Session = Depends(get_session)):
    try:
        result: UserOut = crud.get_user(session=session, user_id=1)
        if result:
            return Response(statusCode=200, data=result, message="User found")
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )
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
                role=user.role, phone=user.phone, location=user.location, created_at=user.created_at,
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

    client = enrich_user_with_follow_data(session=session, user=client)

    return Response(statusCode=200, data={"user": client}, message="User found")

# ----------------------------- POSTS --------------------------------
def enrich_user_with_follow_data(session: Session, user: UserOut|ClientOut|WorkerOut|AdminOut):
    followers = follow_crud.get_followers(session=session, user_id=user.id)
    following = follow_crud.get_following(session=session, user_id=user.id)
    requests = follow_crud.get_follow_requests(session=session, user_id=user.id)
    user.followers = [FollowOut.from_follow(f, current_user_id=user.id) for f in followers]
    user.following = [FollowOut.from_follow(f, current_user_id=user.id) for f in following]
    user.requests = [FollowOut.from_follow(f, current_user_id=user.id) for f in requests]
    return user

def enrich_user_with_role_data(session: Session, current_user:UserOut):
    if current_user.role == UserRole.CLIENT:
        current_user.client = crud.get_user_client(session=session, user_id=current_user.id)
    elif current_user.role == UserRole.WORKER:
        current_user.worker = crud.get_user_worker(session=session, user_id=current_user.id)
    elif current_user.role == UserRole.ADMIN:
        current_user.admin = crud.get_user_admin(session=session, user_id=current_user.id)
    return current_user

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

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

        # Si el User está autenticado, buscamos si tiene un perfil de Admin, Worker o Client
        user_role = enrich_user_with_role_data( session=session, current_user=user)
        user_role = enrich_user_with_follow_data(session=session, user=user_role)

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )

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

    try:
        user_role = enrich_user_with_role_data(session=session, current_user=user)

        user_role = enrich_user_with_follow_data(session=session, user=user_role)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )

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
