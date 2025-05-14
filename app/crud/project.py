from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.models.user import Admin


def get_project_id(*, session: Session, project_id: int) -> Project | None:
    project = session.exec(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.team),
            selectinload(Project.tasks))
    ).first()

    return project

def create_project(*, session: Session, project_data: ProjectCreate) -> Project:
    existing_project = session.exec(
        select(Project).where(Project.title == project_data.title)
    ).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="Project with this title already exists")


    # Check for the assigned admin
    admin = session.exec(
        select(Admin).where(Admin.id == project_data.admin_id)
    ).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not valid or does not exist")

    try:
        new_project = Project.model_validate(project_data)
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        return new_project

    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def update_project(*, session: Session, project_id: int, project_data: ProjectUpdate) -> Project:
    project = session.exec(select(Project).where(Project.id == project_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Actualizar los campos del proyecto
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    # Actualizar la fecha de modificación
    project.updated_at = datetime.now(timezone.utc)

    try:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project
    except ValidationError as e:
        session.rollback()
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

