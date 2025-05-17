from typing import Any, Dict
from sqlalchemy import JSON, Tuple
from sqlmodel import Session
from app.models.project import Project
from .deps import SQLModel, datetime, Field, Relationship, Enum, Optional, List

class ActivityType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    EXPENSE_ADDED = "expense_added"
    EXPENSE_APPROVED = "expense_approved"
    EXPENSE_UPDATED = "expense_updated"
    EXPENSE_DELETED = "expense_deleted"
    # Se pueden añadir más tipos según crezca la app


class ClientActivity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    project_id: int = Field(foreign_key="project.id")
    
    task_id: Optional[int] = Field(foreign_key="task.id", default=None)
    expense_id: Optional[int] = Field(foreign_key="expense.id", default=None)
    
    activity_type: ActivityType
    title: str
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)  # Datos adicionales

    # Relaciones
    client: Optional["Client"] = Relationship(back_populates="activities")
    project: Optional["Project"] = Relationship(back_populates="activities")
    task: Optional["Task"] = Relationship(back_populates="activities")
    expense: Optional["Expense"] = Relationship(back_populates="activities")
    

class BasicInfo(SQLModel):
    id: int
    title: str

class ActivityOut(SQLModel):
    id: int
    activity_type: ActivityType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    project: BasicInfo
    task: Optional[BasicInfo] = None
    expense: Optional[BasicInfo] = None
    metadata: Dict[str, Any] = Field(default={})

    class Config:
        from_attributes = True


class ActivityService:
    def __init__(self, session: Session):
        self.session = session
    
    def log_activity(
        self,
        activity_type: ActivityType,
        project_id: int,
        client_ids: List[int],
        task_id: Optional[int] = None,
        expense_id: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> List[ClientActivity]:
        project = self.session.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")

        activities = []
        for client_id in client_ids:
            # Determinar título y mensaje según tipo
            title, message = self._generate_activity_content(
                activity_type, 
                project,
                metadata
            )
            
            activity = ClientActivity(
                client_id=client_id,
                project_id=project_id,
                task_id=task_id,
                expense_id=expense_id,
                activity_type=activity_type,
                title=title,
                message=message,
                metadata=metadata or {}
            )
            activities.append(activity)
        
        self.session.add_all(activities)
        self.session.commit()
        return activities
    
    def _generate_activity_content(
        self,
        activity_type: ActivityType,
        project: Project,
        metadata: dict
    ) -> Tuple[str, str]:
        # Implementa lógica para generar contenido dinámico
        if activity_type == ActivityType.TASK_CREATED:
            return (
                f"Nueva tarea en {project.title}",
                f"Se creó la tarea: {metadata.get('task_title')}"
            )
        elif activity_type == ActivityType.EXPENSE_ADDED:
            return (
                f"Nuevo gasto en {project.title}",
                f"Gasto registrado: {metadata.get('amount')}€ para {metadata.get('category')}"
            )
        elif activity_type == ActivityType.TASK_COMPLETED:
            return (
                f"Tarea completada en {project.title}",
                f"La tarea {metadata.get('task_title')} ha sido completada"
            )
        elif activity_type == ActivityType.EXPENSE_APPROVED:
            return (
                f"Gasto aprobado en {project.title}",
                f"El gasto de {metadata.get('amount')}€ ha sido aprobado"
            )
        elif activity_type == ActivityType.EXPENSE_UPDATED:
            return (
                f"Gasto actualizado en {project.title}",
                f"El gasto de {metadata.get('amount')}€ ha sido actualizado"
            )
        elif activity_type == ActivityType.EXPENSE_DELETED:
            return (
                f"Gasto eliminado en {project.title}",
                f"El gasto de {metadata.get('amount')}€ ha sido eliminado"
            )
        elif activity_type == ActivityType.TASK_DELETED:
            return (
                f"Tarea eliminada en {project.title}",
                f"La tarea {metadata.get('task_title')} ha sido eliminada"
            )
        else:
            return (
                f"Actividad en {project.title}",
                f"Se ha registrado una actividad de tipo {activity_type}"
            )
