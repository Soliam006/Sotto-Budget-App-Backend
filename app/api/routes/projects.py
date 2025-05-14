from typing import Dict

from fastapi import (APIRouter, Depends, HTTPException)
from fastapi.responses import JSONResponse
from app.api.deps import get_current_user, get_current_active_superuser
from app.models.expense import ExpenseStatus, ExpenseOut
from app.models.project import ProjectOut, ProjectCreate, ProjectUpdate, Project, team_member_to_out
from app.models.response import Response
from app.models.task import TaskStatus, TaskCreate, task_to_out
from app.models.user import User, ClientSimpleOut
import app.crud.project as crud
import app.crud.task as task_crud
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter()


# -------------------------------- GETTERS --------------------------------
@router.get("/{project_id}", response_model=Response, dependencies=[Depends(get_current_user)])
async def get_project(project_id: int,
                      session: Session = Depends(get_session)):

    project = crud.get_project_id(session=session, project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=404,
            content={
                "statusCode": 404,
                "data": None,
                "message": "Project not found"
            }
        )

    # Calcular currentSpent: suma de gastos aprobados
    current_spent = sum(exp.amount for exp in project.expenses if exp.status == ExpenseStatus.APPROVED)

    # Calcular progress: contar tareas según su estado
    done_count = sum(1 for t in project.tasks if t.status == TaskStatus.DONE)
    in_progress_count = sum(1 for t in project.tasks if t.status == TaskStatus.IN_PROGRESS)
    todo_count = sum(1 for t in project.tasks if t.status == TaskStatus.TODO)
    progress = {
        "done": done_count,
        "inProgress": in_progress_count,
        "todo": todo_count,
    }

    # Agrupar gastos por categoría
    expense_categories: Dict[str, float] = {}
    for exp in project.expenses:
        expense_categories[exp.category] = expense_categories.get(exp.category, 0) + exp.amount

    # Preparar la lista de gastos para la respuesta
    expenses_out = [ExpenseOut.model_validate(exp) for exp in project.expenses]

    # Obtener el nombre del Admin (suponiendo que admin.user.name existe)
    admin_name = "Unknown"
    if project.admin and project.admin.user:
        admin_name = project.admin.user.name

    # Convertir la relación many-to-many de clientes a un listado sencillo para la respuesta
    clients_out = []
    if project.clients:
        for client in project.clients:
            # Suponiendo que en el modelo Client, la información básica (name, username) se obtiene
            # a través de la relación con User.
            if client.user:
                clients_out.append(ClientSimpleOut(
                    id=client.id,
                    name=client.user.name,
                    username=client.user.username,
                ))

    return Response(statusCode=200,
                    data=ProjectOut(
                        id=project.id, title=project.title, description=project.description,
                        admin=admin_name, limitBudget=project.limit_budget, currentSpent=current_spent,
                        progress=progress, location=project.location, startDate=project.start_date, endDate=project.end_date,
                        status=project.status, expenses=expenses_out, expenseCategories=expense_categories,
                        clients=clients_out, tasks=[task_to_out(t) for t in project.tasks], team=[team_member_to_out(w) for w in project.team]
                    ),
                    message="Project found")



# --------------------------------- POST ---------------------------------
@router.post("/create", response_model=Response,
             dependencies=[Depends(get_current_active_superuser)])
async def create_project(
        project: ProjectCreate,
        session: Session = Depends(get_session)
):
    try:
        new_project = crud.create_project(
            session=session,
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

    return Response(statusCode=200, data=new_project, message="Project created successfully")


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

