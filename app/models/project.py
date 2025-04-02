# project.py
from .deps import datetime, Field, Relationship, SQLModel, timezone
from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum

from .expense import ExpenseOut
from .user import Admin, Client, ClientSimpleOut  # Asegúrate de que Client se pueda importar sin circularidad
from .project_client import ProjectClient  # Importa la clase real


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
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    # Relaciones
    tasks: List["Task"] = Relationship(back_populates="project")
    expenses: List["Expense"] = Relationship(back_populates="project")
    admin: Optional[Admin] = Relationship(back_populates="projects")
    clients: List[Client] = Relationship(back_populates="projects", link_model=ProjectClient)


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    admin: str
    limitBudget: float
    currentSpent: float
    progress: Dict[str, int]
    location: str
    startDate: datetime
    endDate: datetime
    status: ProjectStatus
    expenses: List[ExpenseOut]
    expenseCategories: Dict[str, float]
    clients: List[ClientSimpleOut] = []  # Lista de clientes asignados

    class Config:
        from_attributes = True
