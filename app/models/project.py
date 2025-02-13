from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.user import Admin, Client

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    location: Optional[str] = None
    images: Optional[str] = None
    admin_id: int = Field(foreign_key="admin.id")
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")

    admin: Admin = Relationship()
    client: Optional[Client] = Relationship()
