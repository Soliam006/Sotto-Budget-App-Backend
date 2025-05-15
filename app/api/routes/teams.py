from fastapi import (APIRouter, HTTPException, Depends)
from fastapi.responses import JSONResponse

from app.api.deps import get_admin_or_worker_permissions, get_current_active_superuser
from app.models.response import Response
from sqlmodel import Session
from app.core.database import get_session
from app.models.user import User, WorkerTeamAdd
import app.crud.project as crud_project

router = APIRouter()


@router.post(
    "/{project_id}",
    response_model=Response, dependencies=[Depends(get_current_active_superuser)]
)
def add_team_member(
        project_id: int,
        worker_data: WorkerTeamAdd,
        session: Session = Depends(get_session)
):
    """Añade un worker al equipo del proyecto"""
    try:
        team_out = crud_project.add_worker_to_project(
            session=session,
            project_id=project_id,
            worker_id=worker_data.worker_id,
            role=worker_data.specialty
        )

        return Response(
            status_code=200,
            data=team_out,
            message="Worker added to project successfully"
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

@router.delete("/{project_id}/{worker_id}",
                response_model=Response,
                dependencies=[Depends(get_current_active_superuser)])
def remove_team_member(
        project_id: int,
        worker_id: int,
        session: Session = Depends(get_session)
):
    """Elimina un worker del equipo del proyecto"""
    try:
        crud_project.remove_worker_from_project(
            session=session,
            project_id=project_id,
            worker_id=worker_id
        )
        return Response(status_code=204, data=None, message="Worker removed from project successfully")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, str(e))