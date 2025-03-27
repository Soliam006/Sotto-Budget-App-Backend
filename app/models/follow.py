from .deps import *
from app.models.user import UserRole, User


class Follow(SQLModel, table=True):
    follower_id: int = Field(foreign_key="user.id", primary_key=True)
    following_id: int = Field(foreign_key="user.id", primary_key=True)
    status: str  # "PENDING", "ACCEPTED", "REJECTED"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    follower: Optional[User] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "User.id==Follow.follower_id"}
    )
    following: Optional[User] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "User.id==Follow.following_id"}
    )


class FollowUpdate(SQLModel):
    status: str  # "PENDING", "ACCEPTED", "REJECTED"
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FollowOut(SQLModel):
    id: int  # Será el ID del otro usuario en la relación
    name: Optional[str] = None  # Si cuentas con un campo "name" en User, o puedes usar "username" en su defecto
    username: str
    role: UserRole
    isFollowing: bool

    @classmethod
    def from_follow(cls, follow: Follow, current_user_id: int) -> "FollowOut":
        """
        Determina el 'otro' usuario en la relación dependiendo del contexto:
        - En 'followers': current_user es seguido (following_id = current_user_id),
          entonces el otro usuario es follow.follower.
        - En 'following': current_user es quien sigue (follower_id = current_user_id),
          el otro usuario es follow.following.
        - En 'requests': depende del contexto, normalmente current_user (admin)
          recibe la solicitud, entonces el otro usuario es follow.follower.
        """
        if follow.follower_id == current_user_id:
            other_user = follow.following
        else:
            other_user = follow.follower

        # En este ejemplo, asumimos que si la solicitud está ACCEPTED, se considera que "isFollowing" es True.
        is_following = follow.status == "ACCEPTED"

        return cls(
            id=other_user.id,
            name=getattr(other_user, "name", None) or other_user.username,
            username=other_user.username,
            role=other_user.role,
            isFollowing=is_following,
        )
