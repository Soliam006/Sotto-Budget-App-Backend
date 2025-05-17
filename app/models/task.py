# task.py
from .deps import datetime, Field, Relationship, SQLModel, timezone
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    DONE = "done"
    IN_PROGRESS = "in_progress"
    TODO = "todo"


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    admin_id: int = Field(foreign_key="admin.id")
    worker_id: int = Field(foreign_key="worker.id")
    title: str
    description: Optional[str] = None
    status: TaskStatus
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = Field(default=None)

    # Relaciones
    project: Optional["Project"] = Relationship(back_populates="tasks")
    worker: Optional["Worker"] = Relationship(back_populates="tasks")
    time_entries: List["TaskTimeEntry"] = Relationship(back_populates="task")
    activities: List["ClientActivity"] = Relationship(back_populates="task")


class TaskTimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    time_in: datetime = Field()
    time_out: Optional[datetime] = Field(default=None)  # Puede ser None si aún está en curso
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    task: Optional[Task] = Relationship(back_populates="time_entries")


class TaskCreate(SQLModel):
    title: str = Field(..., min_length=5, schema_extra={"example": "App móvil"})
    description: Optional[str] = Field(None, max_length=500, schema_extra={"example":"Crear formulario de login con validación"} )
    worker_id: int = Field(..., schema_extra={"example":1})
    due_date: Optional[datetime] = Field(
        None,
        schema_extra={"example":"2023-12-31T23:59:59Z"}
    )
    # project_id y admin_id NO van aquí (se asignan automáticamente)
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        schema_extra={"example":"todo"}
    )

    # Config adicional para OpenAPI
    class Config:
        json_schema_extra = {
            "description": "Datos necesarios para crear una nueva tarea"
        }


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        schema_extra={"example": "Nuevo título de tarea"}
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        schema_extra={"example": "Nueva descripción detallada"}
    )
    worker_id: Optional[int] = Field(
        None,
        schema_extra={"example": 5}
    )
    due_date: Optional[datetime] = Field(
        None,
        schema_extra={"example": "2023-12-31T23:59:59Z"}
    )
    status: Optional[TaskStatus] = Field(
        None,
        schema_extra={"example": "in_progress"}
    )


class TaskOut(SQLModel):
    id: int
    title: str
    description: Optional[str] = None
    assignee: str
    worker_id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = Field(default=None)

    class Config:
        from_attributes = True


def task_to_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        assignee = f"{task.worker.user.name}"
        if task.worker and task.worker.user else "Unassigned",
        worker_id=task.worker_id,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        due_date=task.due_date
    )