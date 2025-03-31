from .deps import *
from .user import Admin, Client


class ProjectClient(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    client_id: int = Field(foreign_key="client.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    
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
    # Relación many-to-many con Client a través de ProjectClient
    clients: List["Client"] = Relationship(back_populates="projects", link_model=ProjectClient)


