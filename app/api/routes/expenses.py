from fastapi import (APIRouter, Depends, HTTPException)
from fastapi.responses import JSONResponse
from app.api.deps import get_current_active_superuser
from app.models.expense import  ExpenseCreate, ExpenseUpdate
from app.models.response import Response
import app.crud.expense as crud_expense
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()

@router.post("/", response_model=Response,
            dependencies= [Depends(get_current_active_superuser)])
def create_expense(
        project_id: int,
        expense: ExpenseCreate,
        session: Session = Depends(get_session)
):
    """Añade un nuevo gasto al proyecto"""
    try:
        new_expense = crud_expense.create_project_expense(
            session=session,
            project_id=project_id,
            expense_data=expense
        )
        return Response(
            statusCode=200,
            data=new_expense,
            message="Expense created successfully"
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

@router.get("/{expense_id}", response_model=Response,
            dependencies=[Depends(get_current_active_superuser)])
def read_expense(
        project_id: int,
        expense_id: int,
        session: Session = Depends(get_session)
):
    try:
        """Obtiene un gasto específico del proyecto"""
        return Response(
            statusCode=200,
            data=crud_expense.get_project_expense(session, project_id, expense_id),
            message="Expense found"
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

@router.put("/{expense_id}", response_model=Response,
            dependencies=[Depends(get_current_active_superuser)]) # Solo admins pueden modificar
def update_expense(
        project_id: int,
        expense_id: int,
        expense: ExpenseUpdate,
        session: Session = Depends(get_session)
):
    try:
        """Actualiza un gasto existente"""
        return Response(
            statusCode=200,
            data=crud_expense.update_project_expense(
                session=session,
                project_id=project_id,
                expense_id=expense_id,
                expense_data=expense
            ), message="Expense updated successfully"
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

@router.delete("/{expense_id}", response_model=Response,
               dependencies=[Depends(get_current_active_superuser)] ) # Solo admins pueden eliminar
def delete_expense(
        project_id: int,
        expense_id: int,
        session: Session = Depends(get_session)
):
    try:
        """Elimina un gasto del proyecto"""
        crud_expense.delete_project_expense(session, project_id, expense_id)

        return Response(
            statusCode=204,
            data=None,
            message="Expense deleted successfully"
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