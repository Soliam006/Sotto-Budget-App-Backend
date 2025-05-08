""" User related CRUD methods """
from fastapi import HTTPException, status
from typing import Any
from sqlmodel import Session, select
from sqlalchemy import or_

from app.core.security import get_password_hash
from app.models.user import User, UserUpdate, UserOut, UserRegister, UserRole, Admin, Client, Worker, \
    ClientAvailability, ClientOut, AdminOut, WorkerOut

crud_id = "---------------------[User CRUD]"

def create_user(*, session: Session, user_data: UserRegister) -> UserOut:
    # Usar or_ para combinar condiciones
    existing_user = session.exec(
        select(User).where(
            or_(User.email == user_data.email, User.username == user_data.username)
        )
    ).first()

    print(f"{crud_id} Verifying if user already exists...")
    print(f"{crud_id} Existing user: ", existing_user)
    if existing_user:
        print("[User CRUD] => User already exists.")
        print("[User CRUD] => User is deleted: ", existing_user.is_deleted)
        if existing_user.is_deleted:
            existing_user.is_deleted = False
            existing_user.password = get_password_hash(user_data.password)
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name, username=user_data.username,
        email=user_data.email, phone=user_data.phone,
        password=hashed_password, location=user_data.location,
        role=user_data.role, description=user_data.description,
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
        print(f"{crud_id} Worker created- User ID: ", new_user.id)

    session.commit()

    return UserOut(
        id=new_user.id, name=new_user.name, username=new_user.username, email=new_user.email,
        role=new_user.role, phone=new_user.phone, location=new_user.location, description=new_user.description,
        language_preference=new_user.language_preference, created_at=new_user.created_at
    )


def get_user_client(*, session: Session, user_id: int) -> ClientOut | None:
    user = session.get(User, user_id)
    try:
        if user:
            client = session.exec(select(Client).where(Client.user_id == user.id, Client.is_deleted == False)).first()
            if client:
                return ClientOut.model_validate(user, update=
                {
                    "budget_limit": client.budget_limit,
                    "client_id": client.id
                })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al obtener el cliente")
    return None


def get_user_admin(*, session: Session, user_id: int) -> AdminOut | None:
    user = session.get(User, user_id)
    if user:
        admin = session.exec(select(Admin).where(Admin.user_id == user.id)).first()
        return AdminOut.model_validate(user, update={"admin_id": admin.id})
    return None


def get_user_worker(*, session: Session, user_id: int) -> WorkerOut | None:
    user = session.get(User, user_id)
    if user:
        worker = session.exec(select(Worker).where(Worker.user_id == user.id)).first()
        return WorkerOut.model_validate(user, update={"worker_id": worker.id})
    return None


def get_availabilities(*, session: Session, client_id: int) -> Any:
    availabilities = session.exec(select(ClientAvailability).where(ClientAvailability.client_id == client_id)).all()
    return availabilities


def update_user(*, session: Session, user_id: int, user: UserUpdate) -> UserOut:
    # 1. Obtener el usuario de la base de datos
    db_user: User | None = session.get(User, user_id)
    if not db_user:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND,  detail="Usuario no encontrado" )

    # 2. Verificar si el nuevo username / email ya existen en otro usuario
    if user.username or user.email:
        existing_user = None

        if user.username:
            existing_user = session.exec(
                select(User).where(User.username == user.username)
            ).first()

        # Si aún no se encontró, buscar por email
        if not existing_user and user.email:
            existing_user = session.exec(
                select(User).where(User.email == user.email)
            ).first()

        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El usuario con ese username o email ya existe"
            )

    # 3. Extraer los campos a actualizar (solo los que llegan en la petición)
    user_data = user.model_dump(exclude_unset=True)

    # 4. Si se incluye contraseña nueva, se hashea
    if "password" in user_data:
        user_data["password"] = get_password_hash(user_data["password"])

    # 5. Manejo de cambio de rol (soft-delete y posible reactivación si ya existía un perfil)
    if "role" in user_data:
        new_role = user_data["role"]
        old_role = db_user.role

        if new_role != old_role:
            # a) Soft-delete de perfiles anteriores
            if db_user.admin_profile:
                db_user.admin_profile.is_deleted = True
            if db_user.worker_profile:
                db_user.worker_profile.is_deleted = True
            if db_user.client_profile:
                db_user.client_profile.is_deleted = True

            # b) Asignar el nuevo rol, buscando si el usuario ya tenía un perfil para reactivarlo
            if new_role == UserRole.ADMIN:
                # ¿Ya existe un perfil ADMIN soft-deleted para este user?
                existing_admin = session.exec(
                    select(Admin).where(Admin.user_id == db_user.id)
                ).first()
                if existing_admin:
                    existing_admin.is_deleted = False
                    db_user.admin_profile = existing_admin
                else:
                    admin = Admin(user_id=db_user.id)
                    db_user.admin_profile = admin
                    session.add(admin)

            elif new_role == UserRole.WORKER:
                existing_worker = session.exec(
                    select(Worker).where(Worker.user_id == db_user.id)
                ).first()
                if existing_worker:
                    existing_worker.is_deleted = False
                    db_user.worker_profile = existing_worker
                else:
                    worker = Worker(user_id=db_user.id)
                    db_user.worker_profile = worker
                    session.add(worker)

            elif new_role == UserRole.CLIENT:
                existing_client = session.exec(
                    select(Client).where(Client.user_id == db_user.id)
                ).first()
                if existing_client:
                    existing_client.is_deleted = False
                    db_user.client_profile = existing_client
                else:
                    client = Client(user_id=db_user.id)
                    db_user.client_profile = client
                    session.add(client)

    # 6. Actualizar campos en el objeto `User`
    db_user.sqlmodel_update(user_data)
    session.add(db_user)

    # 7. Confirmar cambios
    session.commit()
    session.refresh(db_user)

    # 8. Retornar datos en el modelo de salida
    return UserOut(
        id=user.id, name=user.name, username=user.username, location=user.location,
        description=user.description, email=user.email, role=user.role, phone=user.phone,
        language_preference=user.language_preference, created_at=user.created_at
    )



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
        id=user.id, name=user.name, username=user.username, location=user.location, 
        description=user.description, email=user.email, role=user.role, phone=user.phone, 
        language_preference=user.language_preference, created_at=user.created_at
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
