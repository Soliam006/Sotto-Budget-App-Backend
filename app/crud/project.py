from fastapi import HTTPException, status
from typing import Any
from sqlmodel import Session, select

from app.models.project import Project


def get_project_id(*, session: Session, project_id: int) -> Project | None:
    project = session.exec(select(Project).where(Project.id == project_id)).first()
    return project
