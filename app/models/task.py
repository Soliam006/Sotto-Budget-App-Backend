# task.py
from .deps import datetime, Field, Relationship, SQLModel, Optional, List, timezone
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
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    # Relaciones
    project: Optional["Project"] = Relationship(back_populates="tasks")
    worker: Optional["Worker"] = Relationship(back_populates="tasks")
    time_entries: List["TaskTimeEntry"] = Relationship(back_populates="task")


class TaskTimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    time_in: datetime = Field()
    time_out: Optional[datetime] = Field(default=None)  # Puede ser None si aún está en curso
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    task: Optional[Task] = Relationship(back_populates="time_entries")
