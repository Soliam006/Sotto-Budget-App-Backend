from fastapi import (APIRouter, HTTPException, Depends)
from fastapi.responses import JSONResponse

from app.api.deps import get_admin_or_worker_permissions, get_current_active_superuser
from app.models.response import Response
from app.models.task import TaskUpdate, TaskCreate
import app.crud.task as task_crud
from sqlmodel import Session
from app.core.database import get_session
from app.models.user import User

router = APIRouter()


@router.post("/{project_id}", response_model=Response,
             dependencies=[Depends(get_current_active_superuser)])
def create_task_for_project(
        project_id: int,
        task_data: TaskCreate,
        current_user: User = Depends(get_current_active_superuser),
        session: Session = Depends(get_session)
):
    try:
        new_task = task_crud.create_task_for_project(
            session=session, project_id=project_id,
            task_data=task_data, admin_id=task_crud.get_admin_by_user_id(session=session, user_id=current_user.id).id)

        return Response(
            statusCode=200,
            data=new_task,
            message="Task created successfully"
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )



@router.delete("/{project_id}/{task_id}",
               dependencies=[Depends(get_current_active_superuser)])
async def remove_task(
        project_id: int,
        task_id: int,
        session: Session = Depends(get_session),
):
    try:
        task_crud.delete_project_task(
            session=session,
            project_id=project_id,
            task_id=task_id
        )
        return Response(
            statusCode=200,
            data=None,
            message="Task deleted successfully"
        )

    # Controlar excepciones específicas
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )


@router.put("/{project_id}/{task_id}", response_model=Response,
                dependencies=[Depends(get_admin_or_worker_permissions)])
async def update_task(
        project_id: int,
        task_id: int,
        task_data: TaskUpdate,
        session: Session = Depends(get_session),
):
    """Actualiza una tarea específica en un proyecto"""
    try:
        updated_task =task_crud.update_existing_task(
            session=session,
            task_id=task_id,
            task_data=task_data,
            project_id=project_id  # Verifica que la tarea pertenezca al proyecto
        )
        return Response(
            statusCode=200,
            data=updated_task,
            message="Task updated successfully"
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "statusCode": e.status_code,
                "data": None,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "data": None,
                "message": str(e)
            }
        )