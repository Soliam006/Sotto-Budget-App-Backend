from .deps import *

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
    created_at: datetime = Field(default_factory=datetime.utcnow)

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


class UserOut(UserBase):
    """ Para devolver datos de un usuario en las respuestas,
        incluye su ID y los campos base. """
    id: int
    # created_at, si quieres exponerlo también:
    # created_at: Optional[datetime] = None


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


class Worker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    is_deleted: bool = Field(default=False)
    user: User = Relationship(back_populates="worker_profile")


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    budget_limit: Optional[float] = None
    is_deleted: bool = Field(default=False)
    user: User = Relationship(back_populates="client_profile")
    availabilities: List["ClientAvailability"] = Relationship(back_populates="client")


class ClientAvailability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))
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
