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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    project: Optional["Project"] = Relationship(back_populates="expenses")
    activities: List["Activity"] = Relationship(back_populates="expense")


class ExpenseCreate(SQLModel):
    expense_date: datetime = Field(alias="date")
    category: str
    description: str
    amount: float = Field(..., gt=0)
    status: ExpenseStatus = ExpenseStatus.PENDING
    approved_by: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=500)

    class Config:
        validate_by_name = True


class ExpenseUpdate(SQLModel):
    expense_date: Optional[datetime] = Field(None, alias="date")
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    status: Optional[ExpenseStatus] = None
    approved_by: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=500)

    class Config:
        validate_by_name = True


class ExpenseOut(BaseModel):
    id: int
    expense_date: datetime
    category: str
    description: str
    amount: float
    status: ExpenseStatus
    updated_at: datetime
    project_info: Optional[dict] = None

    class Config:
        from_attributes = True