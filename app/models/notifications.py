from typing import Any, Dict, Tuple
from sqlalchemy import JSON
from sqlalchemy import JSON
from sqlmodel import Session
from app.models.project import Project
from .deps import SQLModel, datetime, timezone, Field, Relationship, Enum, Optional, List

class ActivityType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    EXPENSE_ADDED = "expense_added"
    EXPENSE_APPROVED = "expense_approved"
    EXPENSE_UPDATED = "expense_updated"
    EXPENSE_DELETED = "expense_deleted"
    INVENTORY_ADDED = "inventory_added"
    INVENTORY_UPDATED = "inventory_updated"
    INVENTORY_DELETED = "inventory_deleted"
    # Se pueden añadir más tipos según crezca la app


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    
    task_id: Optional[int] = Field(foreign_key="task.id", default=None)
    expense_id: Optional[int] = Field(foreign_key="expense.id", default=None)
    
    activity_type: ActivityType
    title_project: str = Field(default="")
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadatas: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)  # Datos adicionales

    # Relaciones
    project: Optional["Project"] = Relationship(back_populates="activities")
    task: Optional["Task"] = Relationship(back_populates="activities")
    expense: Optional["Expense"] = Relationship(back_populates="activities")
    

class BasicInfo(SQLModel):
    id: int
    title: str

class ActivityOut(SQLModel):
    id: int
    activity_type: ActivityType
    title_project: str
    is_read: bool
    created_at: datetime
    project: BasicInfo
    task: Optional[BasicInfo] = None
    expense: Optional[BasicInfo] = None
    metadatas: Dict[str, Any] = Field(default={})

    class Config:
        from_attributes = True


class ActivityService:
    def __init__(self, session: Session):
        self.session = session
    
    def log_activity(
        self,
        activity_type: ActivityType,
        project_id: int,
        task_id: Optional[int] = None,
        expense_id: Optional[int] = None,
        metadatas: Optional[dict] = None
    ) -> Activity:
        project = self.session.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")
        
        activity = Activity(
            project_id=project_id,
            task_id=task_id,
            expense_id=expense_id,
            activity_type=activity_type,
            title_project=project.title,
            metadatas=metadatas or {}
        )
        
        self.session.add(activity)
        self.session.commit()
        return activity
