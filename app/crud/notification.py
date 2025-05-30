from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.expense import Expense
from app.models.project import Project
from app.models.project_client import ProjectClient
from app.models.inventory import InventoryItem
from app.models.task import Task
from app.models.user import Client, Worker, Admin
from app.models.notifications import ActivityService, ActivityType, Activity

def send_task_notifications(
    session: Session,
    task: Task,
    project_id: int
) -> List[Activity]:
    
    # Registrar actividad
    activity = ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_CREATED,
        project_id=project_id,
        task_id=task.id,
        metadatas={
            "task_title": task.title,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assignee": task.worker.user.username if task.worker else None
        }
    )
    
    return activity


def send_expense_notifications(
    session: Session,
    expense: Expense,
    project_id: int
) -> List[Activity]:
    
    
    activity = ActivityService(session).log_activity(
        activity_type=ActivityType.EXPENSE_ADDED,
        project_id=project_id,
        expense_id=expense.id,
        metadatas={
            "amount": expense.amount,
            "category": expense.category,
            "status": expense.status
        }
    )
    
    return activity


def send_inventory_notifications(
    session: Session,
    project_id: int,
    inventory_item: InventoryItem
) -> Activity:
    activity = ActivityService(session).log_activity(
        activity_type=ActivityType.INVENTORY_ADDED,
        project_id=project_id,
        metadatas={
            "item_name": inventory_item.name,
            "quantity": inventory_item.total,
            "unit": inventory_item.unit,
            "unit_cost": inventory_item.unit_cost
        }
    )

    return activity


def get_client_activities(
    session: Session,
    client_id: int,
    is_read: bool = None,
    activity_type: ActivityType = None
) -> List[Activity]:
    
    """Obtiene actividades de un cliente específico"""
    # Verificar que el cliente existe
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )
    # Buscar Proyectos asociados al cliente
    projects = session.exec(
        select(ProjectClient.project_id)
        .where(ProjectClient.client_id == client_id)
    ).all()
    if not projects:
        raise HTTPException(
            status_code=404,
            detail="No projects found for this client"
        )
    # Filtrar actividades por cliente y tipo
    activities = session.exec(
        select(Activity)
        .where(Activity.project_id.in_(projects))
        .options(
            selectinload(Activity.project),
            selectinload(Activity.task),
            selectinload(Activity.expense)
        )
    ).all()

    # Filtrar actividades por estado de lectura y tipo
    if is_read is not None:
        activities = [activity for activity in activities if activity.is_read == is_read]
    if activity_type is not None:
        activities = [activity for activity in activities if activity.activity_type == activity_type]
    if not activities:
        raise HTTPException(
            status_code=404,
            detail="No activities found for this client"
        )
    return activities


def notify_task_deletion(session: Session, project_id: int, task_data: dict):
    """Notifica sobre eliminación de tarea"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_DELETED,
        project_id=project_id,
        metadatas={
            "deleted_task": task_data
        }
    )

def notify_task_update(session: Session, task: Task, update_data: dict):
    """Notifica sobre cambios en una tarea"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_UPDATED,
        project_id=task.project_id,
        task_id=task.id,
        metadatas={
            "changes": update_data,
            "new_status": task.status,
            "new_due_date": task.due_date.isoformat() if task.due_date else None
        }
    )


def notify_expense_update(session: Session, expense: Expense, update_data: dict):

    """Notifica sobre cambios en un gasto"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.EXPENSE_UPDATED,
        project_id=expense.project_id,
        expense_id=expense.id,
        metadatas={
                "changes": update_data,
                "new_status": expense.status
            }
    )

def notify_inventory_update(session: Session, inventory_item: InventoryItem, update_data: dict):
    """Notifica sobre cambios en un item de inventario"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.INVENTORY_UPDATED,
        project_id=inventory_item.project_id,
        metadatas={
            "changes": update_data
        }
    )

def notify_expense_deletion(session: Session, project_id: int, expense_data: dict):
    """Notifica sobre eliminación de gasto"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.EXPENSE_DELETED,
        project_id=project_id,
        metadatas={
            "deleted_expense": expense_data
        }
    )


def notify_inventory_deletion(session: Session, inventory_data: dict, project_id: int):
    """Notifica sobre eliminación de item de inventario"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.INVENTORY_DELETED,
        project_id=project_id,
        metadatas={
            "deleted_item": inventory_data
        }
    )

def get_user_activities(session: Session, user_id: int) -> List[Activity]:
    """Retrieve activities associated with a user (Client or Admin)."""
    # Determine if the user is a Client or Admin
    user = session.exec(select(Client).where(Client.user_id == user_id)).first()
    is_client = True if user else False

    if not user:
        user = session.exec(select(Admin).where(Admin.user_id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

    # Retrieve projects associated with the user
    if is_client:
        project_ids = session.exec(
            select(ProjectClient.project_id)
            .where(ProjectClient.client_id == user.id)
        ).all()
    else:
        project_ids = session.exec(
            select(Project.id)
            .where(Project.admin_id == user.id)
        ).all()

    if not project_ids:
        raise HTTPException(
            status_code=404,
            detail="No projects found for this user"
        )

    # Retrieve activities for the associated projects
    activities = session.exec(
        select(Activity)
        .where(Activity.project_id.in_([id_ for id_ in project_ids]))
    ).all()

    return activities
