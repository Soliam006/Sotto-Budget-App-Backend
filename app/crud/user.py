""" User related CRUD methods """
from fastapi import HTTPException, status
from typing import Any
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.user import User, UserUpdate, UserBase, UserOut, UserRegister, UserRole, Admin, Client, Worker, \
    ClientAvailability


def create_user(*, session: Session, user_data: UserRegister) -> UserOut:
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()

    if existing_user:
        if existing_user.is_deleted:
            existing_user.is_deleted = False
            existing_user.password = get_password_hash(user_data.password)
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role,
        language_preference=user_data.language_preference,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    if new_user.role == UserRole.ADMIN:
        session.add(Admin(user_id=new_user.id))
    elif new_user.role == UserRole.CLIENT:
        session.add(Client(user_id=new_user.id))
    elif new_user.role == UserRole.WORKER:
        session.add(Worker(user_id=new_user.id))

    session.commit()
    return UserOut(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        language_preference=new_user.language_preference
    )

def get_user_client(*, session: Session, user_id: int) -> Any:
    user = session.get(User, user_id)
    try:
        if user:
            client = session.exec(select(Client).where(Client.user_id == user.id, Client.is_deleted == False)).first()
            if client:
                return client
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al obtener el cliente")
    return None


def get_availabilities(*, session: Session, user_id: int) -> Any:

    availabilities = session.exec(select(ClientAvailability).where(ClientAvailability.client_id == user_id, ClientAvailability.is_deleted == False)).all()
    return availabilities


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

def get_user_in_db(*, session: Session, user_id: int) -> User | None:
    user = session.get(User, user_id)
    return user

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