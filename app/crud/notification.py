from typing import List
from sqlmodel import Session, select

from app.models.expense import Expense, ExpenseCreate
from app.models.project_client import ProjectClient
from app.models.project_expense import ProjectExpenseLink
from app.models.task import Task
from app.models.user import  Client
from app.models.notifications import ActivityService, ActivityType, ClientActivity

def send_task_notifications(
    session: Session,
    task: Task,
    project_id: int
) -> List[ClientActivity]:
    
    # Obtener clientes del proyecto
    client_ids = session.exec(
        select(Client.id)
        .join(ProjectClient)
        .where(ProjectClient.project_id == project_id)
    ).all()
    
    # Registrar actividad
    activities = ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_CREATED,
        project_id=project_id,
        client_ids=client_ids,
        task_id=task.id,
        metadata={
            "task_title": task.title,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assignee": task.worker.name if task.worker else None
        }
    )
    
    return activities


def send_expense_notifications(
    session: Session,
    expense: Expense,
    project_id: int
) -> List[ClientActivity]:
    
    client_ids = session.exec(
        select(Client.id)
        .join(ProjectClient)
        .where(ProjectClient.project_id == project_id)
    ).all()
    
    activities = ActivityService(session).log_activity(
        activity_type=ActivityType.EXPENSE_ADDED,
        project_id=project_id,
        client_ids=client_ids,
        expense_id=expense.id,
        metadata={
            "amount": expense.amount,
            "category": expense.category,
            "status": expense.status
        }
    )
    
    return activities


def get_client_activities(
    session: Session,
    client_id: int,
    is_read: bool = None,
    activity_type: ActivityType = None
) -> List[ClientActivity]:
    
    query = select(ClientActivity).where(ClientActivity.client_id == client_id)
    
    if is_read is not None:
        query = query.where(ClientActivity.is_read == is_read)
    
    if activity_type is not None:
        query = query.where(ClientActivity.activity_type == activity_type)
    
    activities = session.exec(query).all()
    
    return activities


def get_project_client_ids(session: Session, project_id: int) -> List[int]:
    """Obtiene IDs de clientes asociados a un proyecto"""
    return session.exec(
        select(Client.id)
        .join(ProjectClient)
        .where(ProjectClient.project_id == project_id)
    ).all()

def notify_task_deletion(session: Session, project_id: int, task_data: dict):
    """Notifica sobre eliminación de tarea"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_DELETED,
        project_id=project_id,
        client_ids=get_project_client_ids(session, project_id),
        metadata={
            "deleted_task": task_data
        }
    )

def notify_task_update(session: Session, task: Task, changes: dict):
    """Notifica sobre cambios en una tarea"""
    ActivityService(session).log_activity(
        activity_type=ActivityType.TASK_UPDATED,
        project_id=task.project_id,
        client_ids=get_project_client_ids(session, task.project_id),
        task_id=task.id,
        metadata={
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
        client_ids=get_project_client_ids(session, expense.project_id),
        expense_id=expense.id,
        metadata={
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
        client_ids=get_project_client_ids(session, project_id),
        metadata={
            "deleted_expense": expense_data
        }
    )