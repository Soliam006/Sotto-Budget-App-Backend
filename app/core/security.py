from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from sqlmodel import Session, select
from app.models.user import User, UserOut
from sqlalchemy import or_

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key and algorithm for JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 40


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(or_(User.email == email ,User.username == email))
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_username(*, session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    session_user = session.exec(statement).first()
    return session_user


def authenticate_user_with_email(session: Session, email: str, password: str) -> UserOut:
    user = get_user_by_email(session=session, email=email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return UserOut.model_validate(user)


def authenticate_user(session: Session, username: str, password: str) -> UserOut:
    user = get_user_by_username(session=session, username=username)
    if not user or  not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return UserOut.model_validate(user)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
