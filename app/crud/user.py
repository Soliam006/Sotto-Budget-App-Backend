""" User related CRUD methods """
from typing import Any
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.user import User, UserCreate, UserUpdate, UserBase, UserOut


def create_user(*, session: Session, user_create: UserCreate) -> UserOut:
    user = User.model_validate(
        user_create,
        update={"password": get_password_hash(user_create.password)}
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        language_preference=user.language_preference
    )

def update_user(*, session: Session, user_id: int, user: UserUpdate) -> Any:
    db_user : User|None = session.get(User, user_id)

    if db_user:
        user_data = user.model_dump(exclude_unset=True)
        if "password" in user_data:
            password = get_password_hash(user_data["password"])
            user_data["password"] = password

        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return UserOut( id=db_user.id, username=db_user.username,email=db_user.email,
                        role=db_user.role,language_preference=db_user.language_preference)
    return None

def delete_user(*, session: Session, user_id: int) -> Any:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return user
    return None

def get_user(*, session: Session, user_id: int) -> UserOut:
    user = session.get(User, user_id)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        language_preference=user.language_preference
    )

def get_user_by_username(*, session: Session, username: str) -> Any:
    user = session.exec(select(User).where(User.username == username)).first()
    return user

def get_all_users(*, session: Session) -> Any:
    users = session.exec(select(User)).all()
    return users


def get_user_by_id(*, session: Session, id: int) -> User | None:
    statement = select(User).where(User.id == id)
    session_user = session.exec(statement).first()
    return session_user