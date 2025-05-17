from fastapi import (APIRouter, Depends, HTTPException)
from fastapi.responses import JSONResponse
from app.api.deps import get_current_user, get_current_active_superuser
from app.models.project import ProjectCreate, ProjectUpdate
from app.models.response import Response
from app.models.user import User
import app.crud.project as crud
import app.crud.task as task_crud
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()


# -------------------------------- GETTERS --------------------------------
@router.get("/{project_id}", response_model=Response, dependencies=[Depends(get_current_user)])
async def get_project(project_id: int,
                      session: Session = Depends(get_session)):
    try:
        project = crud.get_project_details(session=session, project_id=project_id)

        return Response(statusCode=200, data=project, message="Project found")

    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "statusCode": http_exc.status_code,
                "data": None,
                "message": http_exc.detail
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


@router.get("/", response_model=Response, dependencies=[Depends(get_current_user)])
async def get_projects(current_user: User = Depends(get_current_user),
                       session: Session = Depends(get_session)):
    try:
        projects = crud.get_projects(session=session,
                                     admin_id=task_crud.get_admin_by_user_id(
                                                        session=session,
                                                        user_id=current_user.id).id)

        return Response(statusCode=200, data=projects, message="Projects found")

    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "statusCode": http_exc.status_code,
                "data": None,
                "message": http_exc.detail
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


# --------------------------------- POST ---------------------------------
@router.post("/create", response_model=Response)
async def create_project(
        project: ProjectCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_superuser)
):
    try:
        new_project = crud.create_project(
            session=session,
            project_data=project,
            admin_id=task_crud.get_admin_by_user_id(session=session, user_id=current_user.id).id
        )
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "statusCode": http_exc.status_code,
                "data": None,
                "message": http_exc.detail
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

    return Response(statusCode=200, data=new_project, message="Project created successfully")


@router.post("/add_client/{project_id}", response_model=Response,
            dependencies=[Depends(get_current_active_superuser)])
async def add_client_to_project(
        project_id: int,
        client_id: int,
        session: Session = Depends(get_session)
):
    try:
        updated_project = crud.add_client_to_project(
            session=session,
            project_id=project_id,
            client_id=client_id
        )
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "statusCode": http_exc.status_code,
                "data": None,
                "message": http_exc.detail
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

    return Response(statusCode=200, data=updated_project, message="Client added to project successfully")


# --------------------------------- PUT ---------------------------------

@router.put("/{project_id}", response_model=Response,
            dependencies=[Depends(get_current_active_superuser)])
async def update_project(
        project_id: int,
        project: ProjectUpdate,
        session: Session = Depends(get_session)
):
    try:
        updated_project = crud.update_project(
            session=session,
            project_id=project_id,
            project_data=project
        )
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "statusCode": http_exc.status_code,
                "data": None,
                "message": http_exc.detail
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

    return Response(statusCode=200, data=updated_project, message="Project updated successfully")

# --------------------------------- DELETE --------------------------------
@router.delete("/{project_id}", response_model=Response,
               dependencies=[Depends(get_current_active_superuser)])
async def delete_project(
        project_id: int,
        session: Session = Depends(get_session)
):
    try:
        crud.delete_project(
            session=session,
            project_id=project_id
        )
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "statusCode": http_exc.status_code,
                "data": None,
                "message": http_exc.detail
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

    return Response(statusCode=200, data=None, message="Project deleted successfully")