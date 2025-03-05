from .deps import *

class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CLIENT = "client"

class UserBase(SQLModel):
    username: str
    email: str
    role: UserRole
    language_preference: str = "es"

class UserRegister(SQLModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.CLIENT
    language_preference: str = "es"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str  # Hashed password
    role: UserRole
    language_preference: str = "es"
    is_deleted: bool = Field(default=False)

    admin_profile: Optional["Admin"] = Relationship(back_populates="user")
    worker_profile: Optional["Worker"] = Relationship(back_populates="user")
    client_profile: Optional["Client"] = Relationship(back_populates="user")

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    language_preference: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int

class UsersOut(SQLModel):
    users: List[UserOut]

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