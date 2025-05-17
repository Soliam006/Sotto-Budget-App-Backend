from typing import List
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.expense import Expense
from app.models.project_client import ProjectClient
from app.models.project_expense import ProjectExpenseLink
from app.models.task import Task
from app.models.user import  Client
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

def notify_task_update(session: Session, task: Task, changes: dict):
    """Notifica sobre cambios en una tarea"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_UPDATED,
        project_id=task.project_id,
        task_id=task.id,
        metadatas={
            "changes": changes,
            "new_status": task.status,
            "new_due_date": task.due_date.isoformat() if task.due_date else None
        }
    )

def notify_expense_update(session: Session, expense: Expense, update_data: dict, original_expense: Expense, original_link: ProjectExpenseLink = None,
                          link: ProjectExpenseLink = None):
    """Notifica sobre cambios en un gasto"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.EXPENSE_UPDATED,
        project_id=expense.project_id,
        expense_id=expense.id,
        metadatas={
                "changes": {
                    k: {
                        "old": getattr(original_expense if hasattr(expense, k) else original_link, k),
                        "new": v
                    }
                    for k, v in update_data.items()
                    if hasattr(expense, k) or (link and hasattr(link, k))
                },
                "new_status": expense.status
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