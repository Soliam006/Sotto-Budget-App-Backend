from typing import Dict

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.crud.expense import expense_to_out
from app.crud.task import update_tasks_in_project
from app.models.expense import ExpenseStatus
from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectOut, team_member_to_out
from app.models.project_client import ProjectClient
from app.models.project_expense import ProjectExpenseLink
from app.models.project_team import ProjectTeamLink
from app.models.task import TaskStatus, task_to_out
from app.models.user import Admin, Client, Worker, team_out, TeamOut, ClientSimpleOut, WorkerRead, User, UserRole


def get_project_id(*, session: Session, project_id: int) -> Project | None:
    # Consulta el proyecto con el ID proporcionado, incluyendo las relaciones de equipo y tareas
    project = session.exec(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.team),  # Carga los miembros del equipo relacionados
            selectinload(Project.tasks)  # Carga las tareas relacionadas
        )
    ).first()

    # Devuelve el proyecto encontrado o None si no existe
    return project


def create_project(*, session: Session, project_data: ProjectCreate, admin_id: int) -> Project:
    # Verifica si ya existe un proyecto con el mismo título
    existing_project = session.exec(
        select(Project).where(Project.title == project_data.title and Project.admin_id == admin_id)
    ).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="Project with this title already exists")

    # Verifica que el administrador asignado exista
    admin = session.exec(
        select(Admin).where(Admin.id == admin_id)
    ).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not valid or does not exist")

    try:
        # Crea un nuevo proyecto con los datos proporcionados
        new_project = Project(
            **project_data.model_dump(exclude_unset=True),  # Excluye campos no establecidos
            admin_id=admin_id
        )
        session.add(new_project)  # Agrega el proyecto a la sesión
        session.commit()  # Guarda los cambios en la base de datos
        session.refresh(new_project)  # Refresca el objeto para obtener los datos actualizados

        # 3. Asociar clients al proyecto (usando ProjectClient)
        if project_data.clients_ids:
            for user_id in project_data.clients_ids:
                client = session.exec( select(Client).where(Client.user_id == user_id) ).first()
                session.add(ProjectClient(project_id=new_project.id, client_id=client.id))
            session.commit()

        session.refresh(new_project)  # Refresca el objeto para obtener los datos actualizados

        return new_project
    except ValidationError as e:
        session.rollback()  # Revierte los cambios en caso de error
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        session.rollback()  # Revierte los cambios en caso de error inesperado
        raise HTTPException(status_code=500, detail=str(e))

def add_client_to_project( 
        session: Session,
        project_id: int,
        client_id: int
) -> ProjectClient:
    
    # Verifica si el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Verifica que el cliente exista
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Verifica si el cliente ya está asignado al proyecto
    existing_link = session.exec(
        select(ProjectClient)
        .where(ProjectClient.project_id == project_id)
        .where(ProjectClient.client_id == client_id)
    ).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="Client already in project")

    # Crea la relación entre el proyecto y el cliente
    new_link = ProjectClient(
        project_id=project_id,
        client_id=client_id
    )

    session.add(new_link)  # Agrega la relación a la sesión
    session.commit()  # Guarda los cambios en la base de datos
    session.refresh(new_link)  # Refresca el objeto para obtener los datos actualizados

    return new_link




def update_project(*, session: Session, project_id: int, project_data: ProjectUpdate) -> Project:
    # Busca el proyecto por ID
    project = session.exec(select(Project).where(Project.id == project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Actualiza los campos del proyecto con los datos proporcionados
    for key, value in project_data.model_dump(exclude_unset=True).items():
        if hasattr(project, key):
            setattr(project, key, value)

    # Actualiza la fecha de modificación
    project.updated_at = datetime.now(timezone.utc)

    try:
        session.add(project)  # Agrega el proyecto actualizado a la sesión
        session.commit()  # Guarda los cambios en la base de datos
        session.refresh(project)  # Refresca el objeto para obtener los datos actualizados

        # Verficar los cambios de TASKS
        if project_data.tasks_backend:
            update_tasks_in_project(
                session=session,
                project_id=project_id,
                tasks_data=project_data.tasks_backend,
                admin_id=project.admin_id
            )

        return project
    except ValidationError as e:
        session.rollback()  # Revierte los cambios en caso de error
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        session.rollback()  # Revierte los cambios en caso de error inesperado
        raise HTTPException(status_code=500, detail=str(e))



def add_worker_to_project(session: Session, project_id: int, worker_id: int, role: str = "Team Member") -> TeamOut:
    # Verifica si el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    # Verifica que el trabajador exista
    worker = session.get(Worker, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Verifica si el trabajador ya está asignado al proyecto
    existing_link = session.exec(
        select(ProjectTeamLink)
        .where(ProjectTeamLink.project_id == project_id)
        .where(ProjectTeamLink.worker_id == worker_id)
    ).first()

    if existing_link:
        raise HTTPException( status_code=400, detail="Worker already in project team")


    try:
    # Si el trabajador no tiene especialidad, se asigna el rol proporcionado como su especialidad
        if not worker.specialty:
            worker.specialty = role
            assigned_role = role
        else:
            assigned_role = worker.specialty

        # Crea la relación entre el proyecto y el trabajador
        new_link = ProjectTeamLink(
            project_id=project_id,
            worker_id=worker_id,
            role=assigned_role
        )

        session.add(new_link)  # Agrega la relación a la sesión
        session.commit()  # Guarda los cambios en la base de datos
        session.refresh(new_link)  # Refresca el objeto para obtener los datos actualizados
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding worker to project: {str(e)}")
    
    # Devuelve los datos del equipo actualizado
    return team_out(worker, new_link)


def remove_worker_from_project(
        session: Session,
        project_id: int,
        worker_id: int
) -> None:
    link = session.exec(
        select(ProjectTeamLink)
        .where(ProjectTeamLink.project_id == project_id)
        .where(ProjectTeamLink.worker_id == worker_id)
    ).first()

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Worker not found in project team"
        )

    session.delete(link)
    session.commit()


def delete_project(session, project_id):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Eliminar el proyecto
    session.delete(project)
    session.commit()


def get_projects(session: Session, user_id: int) -> list[ProjectOut]:
    user = session.exec(
        select(User).where(User.id == user_id).options(
            selectinload(User.admin_profile),
            selectinload(User.client_profile),
            selectinload(User.worker_profile)
        )
    ).first()

    if user.role == UserRole.ADMIN:
        projects = session.exec(
            select(Project.id).where(Project.admin_id == user.admin_profile.id)
        ).all()

    elif user.role == UserRole.CLIENT:
        # Si el usuario es un cliente, obtenemos los proyectos asociados a él
        projects = session.exec(
            select(Project.id)
            .join(ProjectClient)
            .where(ProjectClient.client_id == user.client_profile.id)
        ).all()

    else:
        # Si el usuario es un trabajador, obtenemos los proyectos asociados a él
        projects = session.exec(
            select(Project.id)
            .join(ProjectTeamLink)
            .where(ProjectTeamLink.worker_id == user.id)
        ).all()

    if not projects:
        return []

    return [get_project_details(session=session, project_id=ids) for ids in projects]


def get_project_details(session: Session, project_id: int) -> ProjectOut:
    project = get_project_id(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    print(f"------------!!!!!!!!!!Project {project.id} found, fetching details")
    current_spent = sum(exp.amount for exp in project.expenses if exp.status == ExpenseStatus.APPROVED)

    done_count = sum(1 for t in project.tasks if t.status == TaskStatus.DONE)
    in_progress_count = sum(1 for t in project.tasks if t.status == TaskStatus.IN_PROGRESS)
    todo_count = sum(1 for t in project.tasks if t.status == TaskStatus.TODO)
    progress = {
        "done": done_count,
        "inProgress": in_progress_count,
        "todo": todo_count,
    }

    expense_categories: Dict[str, float] = {}
    for exp in project.expenses:
        expense_categories[exp.category] = expense_categories.get(exp.category, 0) + exp.amount

    expenses_out = [expense_to_out(expense=exp,
                                   link=session.exec(select( ProjectExpenseLink)
                                                     .where(ProjectExpenseLink.project_id == project.id).
                                                     where(ProjectExpenseLink.expense_id == exp.id)).first())
                    for exp in project.expenses]

    admin_name = "Unknown"
    if project.admin and project.admin.user:
        admin_name = project.admin.user.name

    clients_out = []
    if project.clients:
        for client in project.clients:
            if client.user:
                clients_out.append(ClientSimpleOut(
                    id=client.id,
                    name=client.user.name,
                    username=client.user.username,
                ))

    return ProjectOut(
        id=project.id, title=project.title, description=project.description, inventory=project.inventory_items,
        admin=admin_name, limit_budget=project.limit_budget, currentSpent=current_spent,
        progress=progress, location=project.location, start_date=project.start_date, end_date=project.end_date,
        status=project.status, expenses=expenses_out, expenseCategories=expense_categories,
        clients=clients_out, tasks=[task_to_out(t) for t in project.tasks], team=[WorkerRead.from_worker(w) for w in project.team]
    )
