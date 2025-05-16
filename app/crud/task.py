""" TASK related CRUD methods """
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from sqlalchemy import or_, and_

from app.models.project import Project
from app.models.task import TaskCreate, TaskOut, Task, task_to_out, TaskUpdate
from app.models.user import UserRole, Worker, Admin

crud_id = "---------------------[Task CRUD]"

def create_task_for_project(
        session: Session,
        project_id: int,
        task_data: TaskCreate,
        admin_id: int
) -> TaskOut:
    """CRUD: Crea una tarea asociada a un proyecto"""
    # Verificar proyecto existente
    project = session.exec(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.team),  # Carga los miembros del equipo relacionados
            selectinload(Project.tasks)  # Carga las tareas relacionadas
        )
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    existing_task = next(
        (t for t in project.tasks if t.title == task_data.title or
         (t.start_date == task_data.start_date and t.due_date == task_data.due_date)),
        None
    )

    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task with this title already exists in this project"
        )

    # Verificar worker
    worker = session.get(Worker, task_data.worker_id)
    if not worker or worker.user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found or invalid"
        )
    # Validar que el worker pertenezca al proyecto y esté en su team
    team = project.team
    if not any(member.worker_id == task_data.worker_id for member in team):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker is not part of the project team"
        )


    # Validar fecha
    if task_data.due_date and task_data.due_date < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date cannot be in the past"
        )

    # Crear tarea
    new_task = Task(
        **task_data.model_dump(exclude_unset=True),
        project_id=project_id,
        admin_id=admin_id
    )

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


def update_existing_task(
        session: Session,
        task_id: int,
        task_data: TaskUpdate,
        project_id: int = None  # Opcional para verificar pertenencia al proyecto
) -> TaskOut:
    """Actualiza una tarea existente con validación de proyecto"""
    # Obtener la tarea
    query = select(Task).where(Task.id == task_id)
    if project_id:
        query = query.where(Task.project_id == project_id)

    task = session.exec(query).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found" + (f" in project {project_id}" if project_id else "")
        )

    # Validar worker si se está actualizando
    if task_data.worker_id is not None:
        worker = session.get(Worker, task_data.worker_id)
        if not worker or worker.user.role != UserRole.WORKER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid worker ID"
            )

    # Validar fecha
    if task_data.due_date and task_data.due_date < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Due date cannot be in the past"
        )

    # Actualizar solo los campos proporcionados
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)

    return task_to_out(task)


def delete_project_task(
        session: Session,
        project_id: int,
        task_id: int
) -> None:
    """CRUD: Elimina una tarea de un proyecto"""
    task = session.exec(
        select(Task)
        .where(Task.id == task_id)
        .where(Task.project_id == project_id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project"
        )

    session.delete(task)
    session.commit()