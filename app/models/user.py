# user.py
from .deps import datetime, Field, Relationship, SQLModel, Enum, Optional, List, timezone
from typing import List, Optional
from pydantic import BaseModel

from .project_team import ProjectTeamLink
from .project_client import ProjectClient


class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CLIENT = "client"


class UserBase(SQLModel):
    """ Campos comunes para los esquemas de lectura/salida. """
    name: str
    username: str
    email: str
    role: UserRole
    language_preference: str = "es"
    phone: str
    location: Optional[str] = None
    description: Optional[str] = None


class UserRegister(SQLModel):
    """ Campos para el registro de un usuario.
        Puedes marcar algunos como opcionales si deseas. """
    name: str
    username: str
    email: str
    password: str
    role: UserRole = UserRole.CLIENT
    language_preference: str = "es"
    phone: str
    location: Optional[str] = None
    description: Optional[str] = None


# -------------------------------
# Modelo principal de User (Tabla)
# -------------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Credenciales y rol
    name: str
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str  # Hashed password
    role: UserRole
    language_preference: str = "es"

    # Campos de contacto / localización
    phone: str
    location: Optional[str] = None
    description: Optional[str] = None

    # Control de Soft Delete y timestamps
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones con sub-modelos de rol
    admin_profile: Optional["Admin"] = Relationship(back_populates="user")
    worker_profile: Optional["Worker"] = Relationship(back_populates="user")
    client_profile: Optional["Client"] = Relationship(back_populates="user")


class UserUpdate(SQLModel):
    """ Campos que se pueden actualizar en un usuario existente. """
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    language_preference: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


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


class UserOut(UserBase):
    """ Para devolver datos de un usuario en las respuestas,
        incluye su ID y los campos base. """
    id: int
    # created_at, si quieres exponerlo también:
    created_at: datetime
    followers: List[FollowOut] = []
    following: List[FollowOut] = []
    requests: List[FollowOut] = []


class UsersOut(SQLModel):
    """ Para devolver una lista de usuarios """
    users: List[UserOut]


# -------------------------------
# Sub-tablas de rol (Admin, Worker, Client)
# -------------------------------
class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    is_deleted: bool = Field(default=False)
    user: User = Relationship(back_populates="admin_profile")
    projects: List["Project"] = Relationship(back_populates="admin")


class Worker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    is_deleted: bool = Field(default=False)
    specialty: Optional[str] = None
    user: User = Relationship(back_populates="worker_profile")
    tasks: List["Task"] = Relationship(back_populates="worker")

    # Relación con proyectos
    projects: List["Project"] = Relationship(
        back_populates="team",
        link_model=ProjectTeamLink
    )


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    budget_limit: Optional[float] = None
    is_deleted: bool = Field(default=False)
    user: "User" = Relationship(back_populates="client_profile")
    availabilities: List["ClientAvailability"] = Relationship(back_populates="client")

    # Relación many-to-many con Project usando la clase real
    projects: List["Project"] = Relationship(back_populates="clients", link_model=ProjectClient)


class ClientAvailability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    client: Client = Relationship(back_populates="availabilities")


# -------------------------------
# Otros Schemas / Token / Login
# -------------------------------
class UserInDB(UserBase):
    id: int
    password: str


class UserResponse(SQLModel):
    statusCode: int
    data: Optional[User]
    message: str


class ClientSimpleOut(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        orm_mode = True


class ClientOut(UserOut):
    client_id: int
    budget_limit: Optional[float]


class AdminOut(UserOut):
    admin_id: int


class WorkerOut(UserOut):
    worker_id: int


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class LoginForm(SQLModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
