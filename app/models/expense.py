# expense.py
from .deps import datetime, Field, Relationship, SQLModel, Optional, List, timezone
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ExpenseStatus(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    REJECTED = "Rejected"


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    expense_date: datetime = Field(alias="date")
    category: str  # Por ejemplo: "Materials", "Labor", "Equipment", "Other"
    description: str
    amount: float
    status: ExpenseStatus
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    project: Optional["Project"] = Relationship(back_populates="expenses")


class ExpenseOut(BaseModel):
    id: int
    date: datetime
    category: str
    description: str
    amount: float
    status: ExpenseStatus

    class Config:
        from_attributes = True