from fastapi import (APIRouter, HTTPException, Depends)
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user, get_current_active_superuser
from app.models.response import Response
from app.models.inventory import InventoryItemCreate, InventoryItemUpdate
import app.crud.inventory as crud
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()

# -------------------------------- GETTERS --------------------------------
@router.get("/{project_id}", response_model=Response, dependencies=[Depends(get_current_user)])
async def get_inventory(project_id: int,
                         session: Session = Depends(get_session)):
    try:
        """Obtiene el inventario del proyecto"""
        inventory = crud.get_inventory(session=session, project_id=project_id)

        return Response(statusCode=200, data=inventory, message="Inventory found")

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


# -------------------------------- POSTERS --------------------------------
@router.post("/", response_model=Response, dependencies=[Depends(get_current_active_superuser)])
async def create_inventory_item(
        item_data: InventoryItemCreate,
        session: Session = Depends(get_session)
):
    """Añade un nuevo item al inventario del proyecto"""
    try:
        new_item = crud.create_inventory_item(
            session=session,
            project_id=item_data.project_id,
            item_data=item_data
        )
        return Response(
            statusCode=200,
            data=new_item,
            message="Inventory item created successfully"
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


# -------------------------------- PUTTERS --------------------------------
@router.put("/{item_id}", response_model=Response, dependencies=[Depends(get_current_active_superuser)])
async def update_inventory_item(
        project_id: int,
        item_id: int,
        item_data: InventoryItemUpdate,
        session: Session = Depends(get_session)
):
    """Actualiza un item del inventario del proyecto"""
    try:
        updated_item = crud.update_inventory_item(
            session=session,
            project_id=project_id,
            item_id=item_id,
            item_data=item_data
        )
        return Response(
            statusCode=200,
            data=updated_item,
            message="Inventory item updated successfully"
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


# -------------------------------- DELETERS --------------------------------
@router.delete("/{item_id}", response_model=Response, dependencies=[Depends(get_current_active_superuser)])
async def delete_inventory_item(
        project_id: int,
        item_id: int,
        session: Session = Depends(get_session)
):
    """Elimina un item del inventario del proyecto"""
    try:
        crud.delete_inventory_item(
            session=session,
            project_id=project_id,
            item_id=item_id
        )
        return Response(statusCode=204, data=None, message="Inventory item deleted successfully")

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