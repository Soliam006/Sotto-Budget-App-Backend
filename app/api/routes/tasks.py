from fastapi import (APIRouter, HTTPException, Depends, Form)

from app.api.deps import get_current_user, get_current_active_superuser
from app.models.response import Response
from app.models.task import TaskCreate
from app.models.user import User, FollowOut
import app.crud.task as task_crud
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()

# -------------------------------- POST --------------------------------
@router.post("/create_task", response_model=Response,
             dependencies=[Depends(get_current_active_superuser)])
def create_task(
        title: str = Form(...),
        description: str = Form(...),
        project_id: int = Form(...),
        worker_id: int = Form(...),
        current_user: User = Depends(get_current_active_superuser),
        session: Session = Depends(get_session)
):
    admin = task_crud.get_admin_by_user_id(session=session, user_id=current_user.id)
    try:
        task_data = TaskCreate(
            title=       title,
            description= description,
            project_id=  project_id,
            admin_id=    admin.id,
            worker_id =  worker_id,
        )

        new_task = task_crud.create_task(session=session,task_data=task_data)


    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    return Response(statusCode=200, data=new_task, message="Task created successfully")