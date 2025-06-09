""" Follow CRUD operations. """
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.models.user import Follow, User, Worker, WorkerRead


def get_followers(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.following_id == user_id, Follow.status == "ACCEPTED")).all()


def get_following(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.follower_id == user_id, Follow.status == "ACCEPTED")).all()


def get_follow_requests(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.following_id == user_id, Follow.status == "PENDING")).all()

def get_follows_bd_relationship(*, session: Session, user_id: int):
    """
    Devuelve una lista de admins con su relación de follow respecto al user_id dado.
    Si existe un Follow, el status será el del Follow, si no existe, será "NONE".
    """
    # Obtener todos los usuarios con rol 'admin'
    admins = session.exec(select(User).where(User.role == "admin")).all()

    # Obtener todos los follows donde el user_id sigue a un admin
    follows = session.exec(
        select(Follow).where(
            (Follow.follower_id == user_id) & (Follow.following_id.in_([a.id for a in admins]))
        )
    ).all()

    # Crear un diccionario para buscar rápidamente la relación
    follow_map = {f.following_id: f.status for f in follows}

    # Construir la lista de admins con status
    result = []
    for admin in admins:
        status = follow_map.get(admin.id, "NONE")
        result.append({
            "id": admin.id,
            "name": admin.name,
            "username": admin.username,
            "role": admin.role,
            "status": status,
            "avatar": "/favicon.ico"
        })
    return result


def follow_user(*, session: Session, follower_id: int, following_id: int):
    # Check if the follow relationship already exists
    existing_follow = session.exec(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)).first()
    # If it exists and is accepted, return None
    if existing_follow:
        print("[Follow CRUD] => relationship already exists.")
        # Devolver directamente el Array de Followes
        return get_followers(session=session, user_id=follower_id)

    # Verificar que el usuario es cliente y el que sigue es admin
    following_user = session.get(User, following_id)
    if not following_user or following_user.role != "admin":
        raise HTTPException( status_code=400, detail="You can only follow admins." )

    # Create a new follow relationship
    new_follow = Follow(follower_id=follower_id, following_id=following_id, status="PENDING")
    # Add the new follow relationship to the session
    try:
        session.add(new_follow)
        session.commit()
        session.refresh(new_follow)
        print("[Follow CRUD] => relationship added successfully.")
        return get_followers(session=session, user_id=follower_id)
    except Exception as e:
        session.rollback()
        print(f"[Follow CRUD] => Failed to add follow relationship: {e}")
        return None


def accept_follow_request(*, session: Session, follower_id: int, following_id: int):
    follow = session.exec(
        select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
            Follow.status == "PENDING"
        )
    ).first()

    if not follow:
        return None

    follow.status = "ACCEPTED"
    session.add(follow)
    session.commit()
    session.refresh(follow)

    user = session.exec(select(User).where(User.id == follower_id)).first()
    is_following = session.exec(
        select(Follow).where(
            Follow.follower_id == following_id,
            Follow.following_id == follower_id,
            Follow.status == "ACCEPTED"
        )
    ).first() is not None

    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "role": user.role,
        "avatar": "/favicon.ico",
        "isFollowing": is_following
    }


def reject_follow_request(*, session: Session, follower_id: int, following_id: int) -> None:
    follow = session.exec(
        select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
            Follow.status == "PENDING"
        )
    ).first()
    if not follow:
        raise HTTPException (status_code=404, detail="Follow request not found")

    session.delete(follow)
    session.commit()
    return None


def unfollow_user(*, session: Session, follower_id: int, following_id: int) -> Follow:
    follow = session.exec(select(Follow).where(Follow.follower_id == follower_id,
                                               Follow.following_id == following_id,
                                               Follow.status == "ACCEPTED"
                                               )).first()
    session.delete(follow)
    session.commit()
    return follow


def get_workers_follows(session: Session, user_id: int):
    """
    Devuelve una lista de Workers que siguen al Admin especificado por user_id.
    """
    # Obtener los follows aceptados donde el usuario es seguido
    follows = session.exec(
        select(Follow.follower_id)
        .join(User, Follow.follower_id == User.id)
        .where(
            Follow.following_id == user_id,
            Follow.status == "ACCEPTED",
            User.role == "worker"
        )
    ).all()

    worker_ids = [fid[0] if isinstance(fid, tuple) else fid for fid in follows]

    if not worker_ids:
        return []

    # Obtener los Workers que siguen al Admin
    workers = session.exec(
        select(Worker)
        .where(Worker.user_id.in_(worker_ids))
        .options(
            selectinload(Worker.user),
            selectinload(Worker.projects),
            selectinload(Worker.tasks)
        )
    ).all()

    return [WorkerRead.from_worker(worker) for worker in workers]