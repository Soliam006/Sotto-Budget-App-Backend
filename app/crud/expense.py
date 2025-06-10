from typing import Dict

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from datetime import datetime, timezone

from starlette import status

from app.crud.notification import notify_expense_deletion, notify_expense_update, send_expense_notifications
from app.models.expense import ExpenseCreate, Expense, ExpenseUpdate, ExpenseOut, ExpenseBackend
from app.models.project import Project
from app.models.project_expense import ProjectExpenseLink


def create_project_expense(
        session: Session,
        project_id: int,
        expense_data: ExpenseCreate) -> ExpenseOut:
    """CRUD: Crea un gasto asociado a un proyecto"""
    # Verificar que el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    try:
        # Crear el gasto primero
        expense = Expense(
            **expense_data.model_dump(exclude_unset=True),
            project_id=project_id
        )
        session.add(expense)
        session.commit() # Guardar los cambios en la base de datos

        # Crear la relación
        link = ProjectExpenseLink(
            project_id=project_id,
            expense_id=expense.id,
            approved_by=expense_data.approved_by,
            notes=expense_data.notes
        )
        session.add(link)
        session.commit() # Guardar los cambios en la base de datos
        session.refresh(expense) # Refrescar el objeto para obtener los datos actualizados
        session.refresh(link) # Refrescar el objeto

        if link:
            send_expense_notifications(
                session=session,
                project_id=project_id,
                expense=expense,
            )

    except Exception as e:
        session.rollback() # Revierte los cambios en caso de error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating expense, {e}")
    
    return expense_to_out(expense=expense, link=link)

def expense_to_out(expense: Expense, link: ProjectExpenseLink) -> ExpenseOut:
    """
    Combines Expense and ProjectExpenseLink data into an ExpenseOut schema.
    """
    expense_dict = {
        "id": expense.id,
        "title": expense.title,
        "expense_date": expense.expense_date,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "status": expense.status,
        "created_at": expense.created_at,
        "updated_at": expense.updated_at,
        "project_info": {
            "approved_by": getattr(link, "approved_by", None),
            "notes": getattr(link, "notes", None),
            "updated_at": getattr(link, "updated_at", None)
        }
    }
    return ExpenseOut(**expense_dict)

def get_project_expense(
        session: Session,
        project_id: int,
        expense_id: int
) -> ExpenseOut:
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found in this project")

    # Verificar Link
    link = session.exec(
        select(ProjectExpenseLink)
        .where(ProjectExpenseLink.project_id == project_id)
        .where(ProjectExpenseLink.expense_id == expense_id)
    ).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not linked to this project")

    return expense_to_out( expense=expense, link=link)

def update_project_expense(
        session: Session,
        project_id: int,
        expense_id: int,
        expense_data: ExpenseUpdate
) -> ExpenseOut:
    # Verificar que el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    expense = session.exec(
        select(Expense)
        .where(Expense.id == expense_id)
        .where(Expense.project_id == project_id)
    ).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    link = session.exec( select(ProjectExpenseLink)
        .where(ProjectExpenseLink.project_id == project_id)
        .where(ProjectExpenseLink.expense_id == expense_id)
    ).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not linked to this project")

    update_data = expense_data.model_dump(exclude_unset=True)
    original_expense = Expense(
        id=expense.id,
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        status=expense.status,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )
    original_link = ProjectExpenseLink(
        project_id=link.project_id,
        expense_id=link.expense_id,
        approved_by=link.approved_by,
        notes=link.notes,
        updated_at=link.updated_at
    )

    # Verificar que el gasto no esté aprobado
    info_updated = False
    for key, value in update_data.items():
        if hasattr(expense, key):
            setattr(expense, key, value)
        elif hasattr(link, key):
            setattr(link, key, value)
            info_updated = True

    expense.updated_at = datetime.now(timezone.utc)


    if link and info_updated:
        link.updated_at = datetime.now(timezone.utc)
        session.add(link)

    session.add(expense)
    session.commit()
    session.refresh(expense)
    if link:
        session.refresh(link)

    # Verificar si ha habido cambios
    changes = {}
    for k, v in update_data.items():
        if hasattr(expense, k): # Verificar si el atributo pertenece a Expense
            old = getattr(original_expense, k, None)
            if old != v:
                changes[k] = {"old": old, "new": v}
        elif hasattr(link, k): # Verificar si el atributo pertenece a ProjectExpenseLink
            old = getattr(original_link, k, None)
            if old != v:
                changes[k] = {"old": old, "new": v}

    # Si ha habido cambios, notificar
    if changes:
        notify_expense_update( session=session, expense=expense, update_data=changes)

    return expense_to_out(expense=expense, link=link)

def update_expenses_in_project(
        session: Session,
        project_id: int,
        expenses_data: list[ExpenseBackend]
):
    """Actualiza múltiples gastos en un proyecto"""
    for expense_data in expenses_data:
        # Revisar Booleanos que indican si es una actualización o creación
        if expense_data.updated:
            # Actualizar gasto existente
            update_project_expense(
                session=session,
                project_id=project_id,
                expense_id=expense_data.id,
                expense_data=ExpenseUpdate.model_validate(expense_data)
            )
        elif expense_data.created:
            # Crear nuevo gasto
            create_project_expense(
                session=session,
                project_id=project_id,
                expense_data=ExpenseCreate.model_validate(expense_data)
            )
        else:
            # Eliminar gasto existente
            delete_project_expense(
                session=session,
                project_id=project_id,
                expense_id=expense_data.id
            )

def delete_project_expense(
        session: Session,
        project_id: int,
        expense_id: int
):
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found in this project")

    # Eliminar la relación entre el proyecto y el gasto
    link = session.exec( select(ProjectExpenseLink)
        .where(ProjectExpenseLink.project_id == project_id)
        .where(ProjectExpenseLink.expense_id == expense_id)
    ).first()
    # Guardar datos antes de borrar
    expense_data = {
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category
    }
    
    session.delete(expense)
    if link:
        session.delete(link)
    session.commit()
    
    # Notificar eliminación
    notify_expense_deletion(
        session=session,
        project_id=project_id,
        expense_data=expense_data
    )