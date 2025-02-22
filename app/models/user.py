from .deps import *

class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CLIENT = "client"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password: str  # Hashed password
    role: UserRole
    language_preference: str = "es"

    admin_profile: Optional["Admin"] = Relationship(back_populates="user")
    worker_profile: Optional["Worker"] = Relationship(back_populates="user")
    client_profile: Optional["Client"] = Relationship(back_populates="user")


class UserBase(SQLModel):
    name: str
    email: str
    role: UserRole
    language_preference: str = "es"

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str]

class UserOut(UserBase):
    id: int


class UsersOut(SQLModel):
    users: List[UserOut]


class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="admin_profile")

class Worker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="worker_profile")

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="client_profile")


class UserResponse(SQLModel):
    statusCode: int
    data: Optional[User]
    message: str

