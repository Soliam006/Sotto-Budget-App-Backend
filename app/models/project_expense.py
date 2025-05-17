from typing import Optional

from .deps import  Field,  SQLModel, datetime, timezone


class ProjectExpenseLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    expense_id: int = Field(foreign_key="expense.id", primary_key=True)
    approved_by: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=500)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))