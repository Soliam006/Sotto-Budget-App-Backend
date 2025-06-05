# project.py
from .deps import datetime, Field, Relationship, SQLModel, timezone
from pydantic import BaseModel, model_validator
from typing import Optional, List, Dict
from enum import Enum

from .expense import ExpenseOut
from .project_expense import ProjectExpenseLink
from .project_team import ProjectTeamLink
from .task import TaskOut
from .user import Admin, Client, ClientSimpleOut, Worker, WorkerRead
from .project_client import ProjectClient
from .inventory import InventoryItem


class ProjectStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    admin_id: int = Field(foreign_key="admin.id")
    limit_budget: float
    location: str
    start_date: datetime
    end_date: datetime
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones
    tasks: List["Task"] = Relationship( back_populates="project")
    admin: Optional[Admin] = Relationship( back_populates="projects")
    expenses: List["Expense"] = Relationship( back_populates="project", link_model=ProjectExpenseLink)
    clients: List[Client] = Relationship( back_populates="projects", link_model=ProjectClient)
    team: List[Worker] = Relationship( back_populates="projects", link_model=ProjectTeamLink)
    activities: List["Activity"] = Relationship(back_populates="project")

    # Relación con inventario
    inventory_items: List["InventoryItem"] = Relationship(back_populates="project")


class ProjectCreate(SQLModel):
    title: str = Field(..., min_length=5, schema_extra= {"example":"App móvil"})
    description: str = Field(..., schema_extra= {"example":"Desarrollo de aplicación iOS/Android"})
    limit_budget: float = Field(..., gt=0, schema_extra= {"example":50000.0})
    location: str = Field(..., schema_extra= {"example":"Madrid, España"})
    start_date: datetime = Field(..., schema_extra= {"example":"2023-01-01T00:00:00Z"})
    end_date: datetime = Field(..., schema_extra= {"example":"2023-12-31T23:59:59Z"})
    # admin_id NO va aquí (se obtiene del usuario autenticado)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    clients_ids: Optional[List[int]] = Field(default=None, description="Lista de IDs de Users asignados al proyecto")

    # Validación personalizada para fechas
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("La fecha de fin debe ser posterior a la de inicio")
        return self

class ProjectUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=5)
    description: Optional[str] = Field(None)
    limit_budget: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    status: Optional[ProjectStatus] = Field(None)

    # Validación condicional de fechas
    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("La fecha de fin debe ser posterior a la de inicio")
        return self


class TeamMemberOut(SQLModel):
    id: int
    name: str
    role: str  # Rol específico en este proyecto
    avatar_url: Optional[str]

def team_member_to_out(member: Worker) -> TeamMemberOut:
    return TeamMemberOut(
        id=member.id,
        name=member.user.name if member.user else "Unknown",
        role=member.specialty if member.specialty else "Team Member",
        avatar_url=None
    )

class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    admin: str
    limit_budget: float
    currentSpent: float
    progress: Dict[str, int]
    location: str
    start_date: datetime
    end_date: datetime
    status: ProjectStatus
    expenses: List[ExpenseOut]
    expenseCategories: Dict[str, float]
    clients: List[ClientSimpleOut] = []  # Lista de clientes asignados
    tasks: List[TaskOut] = []  # Añade esta línea
    team: List[WorkerRead] = []
    inventory: List[InventoryItem] = []

    class Config:
        from_attributes = True
