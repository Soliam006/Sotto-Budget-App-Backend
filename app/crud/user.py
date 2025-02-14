""" User related CRUD methods """
from typing import Any
from sqlmodel import Session, select
from app.models.user import User, UserCreate, UserUpdate
#from app.core.security import get_password_hash, verify_password
from sqlalchemy import or_

def create_user(*, session: Session, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create
        #update={"password": get_password_hash(user_create.password)}
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

"""
def update_user(*, session: Session, user_id: int, user: UserUpdate) -> Any:
    db_user : User = session.get(User, user_id)

    if db_user:
        user_data = user.model_dump(exclude_unset=True)
        if "password" in user_data:
            password = get_password_hash(user_data["password"])
            user_data["password"] = password

        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    return None
"""
def delete_user(*, session: Session, user_id: int) -> Any:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return user
    return None

def get_user(*, session: Session, user_id: int) -> Any:
    user = session.get(User, user_id)
    return user

def get_user_by_name(*, session: Session, name: str) -> Any:
    user = session.exec(select(User).where(User.username == name)).first()
    return user

def get_all_users(*, session: Session) -> Any:
    users = session.exec(select(User)).all()
    return users

def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(or_(User.email == email ,User.username == email))
    session_user = session.exec(statement).first()
    return session_user

def get_user_by_id(*, session: Session, id: int) -> User | None:
    statement = select(User).where(User.id == id)
    session_user = session.exec(statement).first()
    return session_user
"""
def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(db_user.password, password):
        return None
    return db_user
"""