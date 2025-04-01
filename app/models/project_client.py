# project_client.py
from .deps import datetime, Field, SQLModel, timezone


class ProjectClient(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    client_id: int = Field(foreign_key="client.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
