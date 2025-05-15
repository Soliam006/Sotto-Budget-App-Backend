from typing import Dict

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from datetime import datetime, timezone

from starlette import status

from app.models.expense import ExpenseStatus, ExpenseCreate, Expense, ExpenseUpdate, ExpenseOut
from app.models.project import Project
from app.models.project_expense import ProjectExpenseLink


def create_project_expense(
        session: Session,
        project_id: int,
        expense_data: ExpenseCreate):
    # Verificar que el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Crear el gasto primero
    expense = Expense(
        **expense_data.model_dump(exclude_unset=True),
        project_id=project_id
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)

    # Crear la relación
    link = ProjectExpenseLink(
        project_id=project_id,
        expense_id=expense.id,
        approved_by=expense_data.approved_by,
        notes=expense_data.notes
    )
    session.add(link)
    session.commit()

    return expense

def expense_to_out(expense: Expense)-> ExpenseOut:
    expense_dict = expense.model_dump()
    if expense.projects and len(expense.projects) > 0:
        link = expense.projects[0]
        expense_dict["project_info"] = {
            "approved_by": link.approved_by,
            "notes": link.notes,
            "created_at": link.created_at
        }
    return ExpenseOut(**expense_dict)

def get_project_expense(
        session: Session,
        project_id: int,
        expense_id: int
) -> Expense:
    # Verificar que el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    # Verificar que el gasto existe en el proyecto
    expense = session.exec(
        select(Expense)
        .where(Expense.id == expense_id)
        .where(Expense.project_id == project_id)
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found in this project"
        )
    return expense

def update_project_expense(
        session: Session,
        project_id: int,
        expense_id: int,
        expense_data: ExpenseUpdate
) -> Expense:
    expense = get_project_expense(session, project_id, expense_id)

    update_data = expense_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    expense.updated_at = datetime.now(timezone.utc)
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense

def delete_project_expense(
        session: Session,
        project_id: int,
        expense_id: int
) -> None:
    expense = get_project_expense(session, project_id, expense_id)
    session.delete(expense)
    session.commit()