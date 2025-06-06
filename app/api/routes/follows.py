from fastapi import (APIRouter, HTTPException, Depends, Form)
from starlette.responses import JSONResponse

from app.api.deps import get_current_user, get_worker_client_permission, get_client_permission, \
    get_current_active_superuser
from app.models.response import Response
from app.models.user import User, FollowOut
import app.crud.follow as follow_crud
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()

# -------------------------------- GETTERS --------------------------------


@router.get("/follows_user", response_model=Response)
def get_follow_lists(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    try:
        # Followers: usuarios que siguen al current user (seguidores)
        followers = follow_crud.get_followers(session=session, user_id=current_user.id)

        # Following: usuarios a los que current user está siguiendo
        following = follow_crud.get_following(session=session, user_id=current_user.id)

        # Requests: solicitudes pendientes recibidas por current user (para admin, por ejemplo)
        requests = follow_crud.get_follow_requests(session=session, user_id=current_user.id)

        followers_list = [FollowOut.from_follow(f, current_user_id=current_user.id) for f in followers]
        following_list = [FollowOut.from_follow(f, current_user_id=current_user.id) for f in following]
        requests_list = [FollowOut.from_follow(f, current_user_id=current_user.id) for f in requests]
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    return Response(statusCode=200,
                    data={
                        "followers": followers_list,
                        "following": following_list,
                        "requests": requests_list,
                    }, message="Follows found")


@router.get("/workers", response_model=Response)
def get_workers(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_superuser)
):
    try:
        workers = follow_crud.get_workers_follows(session=session, user_id=current_user.id)

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "statusCode": e.status_code,
            "data": None,
            "message": e.detail
        })
    except Exception as e:
        return  JSONResponse(status_code=400, content={
            "statusCode": 400,
            "data": None,
            "message": str(e)
        })

    return Response(statusCode=200, data=workers, message="Workers found")

@router.get("/follows_status", response_model=Response)
def get_follow_status(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_worker_client_permission)
):
    try:
        follow_status = follow_crud.get_follows_bd_relationship(session=session, user_id=current_user.id)

    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    return Response(statusCode=200, data=follow_status, message="Follow status found")



@router.post("/{user_id}", response_model=Response)
def follow_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_worker_client_permission)):
    if user_id == current_user.id:
        return Response(statusCode=400, data=None, message="You can't follow yourself")

    try:
        result = follow_crud.follow_user(session=session, follower_id=current_user.id, following_id=user_id)
    except Exception as e:
        return Response(statusCode=500, data=None, message=str(e))

    if result is None:
        return Response(statusCode=400, data=None, message="Error sending follow request")
    return Response(statusCode=200, data=result, message="Request Send")


@router.post("/accept_follow/{user_id}", response_model=Response)
def accept_follow_request(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    print(f"Accepting follow request from user {user_id} for current user {current_user.name}")

    try:
        follower = follow_crud.accept_follow_request(session=session, follower_id=user_id, following_id=current_user.id)
        if follower is None:
            return Response(statusCode=404, data=None, message="Follow request not found")

    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    return Response(statusCode=200, data=follower, message="Follow request accepted")


@router.post("/reject_follow/{user_id}", response_model=Response)
def reject_follow_request(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    try:
        follow_crud.reject_follow_request(session=session, follower_id=user_id, following_id=current_user.id)

        return Response(statusCode=200, data=None, message="Follow request rejected")

    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    return Response(statusCode=200, data=follow_out, message="Follow request rejected")


@router.delete("/unfollow/{user_id}", response_model=Response)
def unfollow_user(user_id: int, session: Session = Depends(get_session),
                  current_user: User = Depends(get_current_user)):
    try:
        result = follow_crud.unfollow_user(session=session, follower_id=current_user.id, following_id=user_id)
    except HTTPException as e:
        return Response(statusCode=e.status_code, data=None, message=e.detail)
    except Exception as e:
        return Response(statusCode=400, data=None, message=str(e))

    if result is None:
        return Response(statusCode=400, data=None, message="Error unfollowing user")
    return Response(statusCode=200, data=result, message="User unfollowed")
