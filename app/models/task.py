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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = Field(default=None)

    # Relaciones
    project: Optional["Project"] = Relationship(back_populates="tasks")
    worker: Optional["Worker"] = Relationship(back_populates="tasks")
    time_entries: List["TaskTimeEntry"] = Relationship(back_populates="task")


class TaskTimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    time_in: datetime = Field()
    time_out: Optional[datetime] = Field(default=None)  # Puede ser None si aún está en curso
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    task: Optional[Task] = Relationship(back_populates="time_entries")


class TaskCreate (SQLModel):
    title: str
    description: Optional[str] = None
    worker_id: int
    due_date: Optional[datetime] = Field(default=None)
    project_id: int
    admin_id: int
    status: TaskStatus = TaskStatus.TODO


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    worker_id: Optional[int] = None
    due_date: Optional[datetime] = Field(default=None)
    status: Optional[TaskStatus] = None


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