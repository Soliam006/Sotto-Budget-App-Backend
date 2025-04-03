""" Follow CRUD operations. """
from sqlmodel import Session, select

from app.models.user import Follow


def get_followers(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.following_id == user_id, Follow.status == "ACCEPTED")).all()


def get_following(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.follower_id == user_id, Follow.status == "ACCEPTED")).all()


def get_follow_requests(*, session: Session, user_id: int):
    return session.exec(select(Follow).where(Follow.following_id == user_id, Follow.status == "PENDING")).all()


def follow_user(*, session: Session, follower_id: int, following_id: int) -> Follow:
    follow = Follow(follower_id=follower_id, following_id=following_id, status="PENDING")
    session.add(follow)
    session.commit()
    session.refresh(follow)
    return follow


def accept_follow_request(*, session: Session, follower_id: int, following_id: int) -> Follow:
    follow = session.exec(select(Follow).where(Follow.follower_id == follower_id,
                                               Follow.following_id == following_id,
                                               Follow.status == "PENDING"
                                               )).first()
    follow.status = "ACCEPTED"
    session.add(follow)
    session.commit()
    session.refresh(follow)
    return follow


def reject_follow_request(*, session: Session, follower_id: int, following_id: int) -> Follow:
    # Status = PENDING
    follow = session.exec(select(Follow).where(Follow.follower_id == follower_id,
                                               Follow.following_id == following_id,
                                               Follow.status == "PENDING")).first()
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
