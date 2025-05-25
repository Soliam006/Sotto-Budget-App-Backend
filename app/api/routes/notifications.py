from typing import List, Optional
from fastapi import (APIRouter, Depends, HTTPException)
from fastapi.responses import JSONResponse
from app.api.deps import get_current_user, get_current_active_superuser
from app.models.notifications import ActivityOut, ActivityType
from app.models.project import ProjectCreate, ProjectUpdate
from app.models.response import Response
from app.models.user import User
import app.crud.project as crud
import app.crud.notification as notification_crud
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()


@router.get("/{client_id}", response_model=Response, dependencies=[Depends(get_current_user)])
def get_client_activities(
    client_id: int,
    is_read: Optional[bool] = None,
    activity_type: Optional[ActivityType] = None,
    session: Session = Depends(get_session)
):
    """Get activities for a specific client."""
    try:
        activities = notification_crud.get_client_activities(
            session=session,
            client_id=client_id,
            is_read=is_read,
            activity_type=activity_type
        )

        if not activities:
            return Response(statusCode=404, data=None, message="No activities found for this client")
        
        return Response(
            statusCode=200,
            data=activities,
            message="Activities found"
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


@router.get("/", response_model=Response, dependencies=[Depends(get_current_user)])
def get_user_activities(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get activities for the current user."""
    try:
        activities = notification_crud.get_user_activities(
            session=session,
            user_id=current_user.id
        )

        if not activities:
            return Response(statusCode=404, data=None, message="No activities found for this user")

        return Response(
            statusCode=200,
            data=activities,
            message="Activities found"
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