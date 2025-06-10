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

class AvailabilityWorker(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    AVAILABLE = "Available"
    BUSY = "Busy"

class FollowStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

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
    budget_limit: Optional[float] = None  # Solo para CLIENTES
    # Solo para WORKERS
    skills: Optional[List[str]] = None
    availability: Optional[AvailabilityWorker] = None  # Disponibilidad del trabajador
    availabilities: Optional[List["ClientAvailabilityOut"]] = None  # Disponibilidad del cliente


class Follow(SQLModel, table=True):
    follower_id: int = Field(foreign_key="user.id", primary_key=True)
    following_id: int = Field(foreign_key="user.id", primary_key=True)
    status: FollowStatus = Field(default=FollowStatus.PENDING, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    follower: Optional[User] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "User.id==Follow.follower_id"}
    )
    following: Optional[User] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "User.id==Follow.following_id"}
    )


class FollowUpdate(SQLModel):
    status: FollowStatus = Field(default=FollowStatus.PENDING)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime
    followers: List[FollowOut] = []
    following: List[FollowOut] = []
    requests: List[FollowOut] = []
    client: Optional["ClientOut"] = None
    worker: Optional["WorkerRead"] = None
    admin: Optional["AdminOut"] = None


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
    specialty: Optional[str] = Field(default=None)
    skills: List["WorkerSkill"] = Relationship(back_populates="worker")
    availability: Optional[AvailabilityWorker] = Field(default=None, description="Disponibilidad del trabajador")

    user: "User" = Relationship(back_populates="worker_profile")
    tasks: List["Task"] = Relationship(back_populates="worker")

    projects: List["Project"] = Relationship(
        back_populates="team",
        link_model=ProjectTeamLink
    )

class WorkerSkill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    worker_id: int = Field(foreign_key="worker.id")
    worker: Worker = Relationship(back_populates="skills")

class WorkerTeamAdd(SQLModel):
    worker_id: int
    specialty: Optional[str] = None
    skills: Optional[List[str]] = None
    availability: Optional[AvailabilityWorker] = None

class WorkerRead(SQLModel):
    id: int
    name: str  # Esto vendría del modelo User asociado
    role: str  # Esto sería el campo specialty
    phone: str  # Teléfono del trabajador
    skills: List[str]
    availability: Optional[str] = None  # Disponibilidad del trabajador
    contact: Optional[str] = None  # Email
    projects: List[str] = []  # Lista de nombres de proyectos
    tasksCompleted: int # Conteo de tareas completadas
    tasksInProgress: int  # Conteo de tareas en progreso
    efficiency: int # Porcentaje de eficiencia

    @classmethod
    def from_worker(cls, worker: Worker) -> "WorkerRead":
        """Convierte un objeto Worker a WorkerRead"""
        return cls(
            id=worker.id,
            name=worker.user.name,
            role=worker.specialty if worker.specialty else "N/A",
            phone=worker.user.phone,
            skills=[skill.name for skill in worker.skills],
            availability=worker.availability if worker.availability else None,
            contact=worker.user.email,  # Asumiendo que quieres el email como contacto
            projects=[project.title for project in worker.projects],  # Lista de títulos de proyectos
            tasksCompleted=sum(task.status == "done" for task in worker.tasks),
            tasksInProgress=sum(task.status == "in_progress" for task in worker.tasks),
            efficiency=(
                sum(task.status == "done" for task in worker.tasks) * 100 // len(worker.tasks)
                if worker.tasks else 0
            )
        )

class WorkerDataBackend(WorkerRead):
    created:bool
    updated:bool
    deleted:bool

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

class ClientAvailabilityOut(SQLModel):
    id: int
    start_date: datetime
    end_date: datetime
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
        from_attributes = True


class ClientOut(BaseModel):
    client_id: int
    budget_limit: Optional[float]
    availabilities : Optional[List[ClientAvailabilityOut]] = []


class AdminOut(BaseModel):
    admin_id: int
    workers: List[WorkerRead] = []


class WorkerOut(UserOut):
    worker_id: int

class TeamOut(SQLModel):
    id: int
    name: str
    role: str
    avatar: Optional[str] = None

def team_out(worker: Worker, project_team: ProjectTeamLink) -> TeamOut:
    """Convierte un Worker y su relación en un objeto de salida"""
    return TeamOut(
        id=worker.id,
        name=worker.user.name,
        role=project_team.role
    )

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class LoginForm(SQLModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
