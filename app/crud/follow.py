""" Follow CRUD operations. """


from sqlmodel import Session, select

from app.models.user import Follow
from fastapi import HTTPException


def get_followers(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.following_id == user_id, Follow.status == "ACCEPTED")).all()


def get_following(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.follower_id == user_id, Follow.status == "ACCEPTED")).all()


def get_follow_requests(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.following_id == user_id, Follow.status == "PENDING")).all()


def follow_user(*, session: Session, follower_id: int, following_id: int):
    # Check if the follow relationship already exists
    existing_follow = session.exec(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)).first()
    # If it exists and is accepted, return None
    if existing_follow:
        print("[Follow CRUD] => relationship already exists.")
        # Devolver directamente el Array de Followes
        return get_followers(session=session, user_id=follower_id)

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
    follow = session.exec(select(Follow).where(Follow.follower_id == follower_id,
                                               Follow.following_id == following_id,
                                               Follow.status == "PENDING"
                                               )).first()

    if not follow:
        return None

    follow.status = "ACCEPTED"
    session.add(follow)
    session.commit()
    session.refresh(follow)
    return get_followers(session=session, user_id=follower_id)


def reject_follow_request(*, session: Session, follower_id: int, following_id: int) -> Follow:
    # Status = PENDING
    follow = session.exec(select(Follow).where(Follow.follower_id == follower_id,
                                               Follow.following_id == following_id,
                                               Follow.status == "PENDING")).first()
    if not follow:
        return None

    follow.status = "REJECTED"
    session.add(follow)
    session.commit()
    session.refresh(follow)
    return follow


def unfollow_user(*, session: Session, follower_id: int, following_id: int) -> Follow:
    follow = session.exec(select(Follow).where(Follow.follower_id == follower_id,
                                               Follow.following_id == following_id,
                                               Follow.status == "ACCEPTED"
                                               )).first()
    session.delete(follow)
    session.commit()
    return follow
