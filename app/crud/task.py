""" TASK related CRUD methods """
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import or_

from app.models.task import TaskCreate, TaskOut, Task, task_to_out
from app.models.user import UserRole, Worker, Admin

crud_id = "---------------------[Task CRUD]"

"""
Create a new task with the given task data.
"""
def create_task(*, session: Session, task_data: TaskCreate) -> TaskOut | HTTPException:
    # Usar or_ para combinar condiciones
    existing_task = session.exec(
        select(Task).where(
            or_(Task.title == task_data.title, Task.description == task_data.description)
        )
    ).first()

    print(f"{crud_id} Verifying if task already exists...")
    print(f"{crud_id} Existing task: ", existing_task)
    if existing_task:
        print(f"{crud_id} Task already exists.")
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La tarea ya existe")

    # Check for the assigned worker
    worker = session.exec(
        select(Worker).where(Worker.id == task_data.worker_id)
    ).first()
    print(f"{crud_id} Verifying if worker exists. Worker: ", worker)

    if not worker or worker.user.role != UserRole.WORKER:
        raise HTTPException(status_code=404, detail="Trabajador no válido o no existe")

    new_task = Task(
        title=task_data.title, description=task_data.description,
        worker_id=task_data.worker_id, due_date=task_data.due_date,
        project_id=task_data.project_id, admin_id=task_data.admin_id,
        status=task_data.status
    )
    if (task_data.due_date is not None and task_data.due_date < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de vencimiento no puede ser anterior a la fecha actual")

    if (task_data.due_date is not None):
        new_task.due_date = task_data.due_date

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return task_to_out(new_task)


def get_admin_by_user_id(session: Session, user_id: int) -> Admin | HTTPException:
    """
    Get the admin ID associated with a given user ID.
    """
    stmt = select(Admin).where(Admin.user_id == user_id)
    admin = session.exec(stmt).first()
    if admin:
        return admin
    raise HTTPException(status_code=404, detail="Admin not found")