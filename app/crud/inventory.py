from typing import Dict

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.crud.notification import send_inventory_notifications, notify_inventory_update, notify_inventory_deletion
from app.models.inventory import (InventoryItem, InventoryItemCreate, InventoryItemUpdate,
                                  InventoryCategory, InventoryStatus, InventoryBackend)
from app.models.project import Project


def get_inventory(
    session: Session,
    project_id: int = None,
) -> InventoryItem:
    """CRUD: Obtiene un inventario por su ID"""
    inventory = session.exec(
        select(InventoryItem)
        .where(InventoryItem.project_id == project_id)
    ).all()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return inventory


def create_inventory_item(
    session: Session,
    project_id: int,
    item_data: InventoryItemCreate
) -> InventoryItem:
    """CRUD: Crea un nuevo item de inventario"""
    # Verificar que el proyecto existe
    project = session.exec(
        select(Project)
        .where(Project.id == project_id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verificar que el item no exista
    existing_item = session.exec(
        select(InventoryItem)
        .where(InventoryItem.project_id == project_id)
        .where(InventoryItem.name == item_data.name)
    ).first()

    if existing_item:
        raise HTTPException(status_code=409, detail="Item already exists in this project")

    # Crear el nuevo item de inventario
    new_item = InventoryItem( **item_data.model_dump (exclude_unset=True) )

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    # Send notifications
    send_inventory_notifications(
        session=session,
        project_id=project_id,
        inventory_item=new_item
    )

    return new_item


def update_inventory_item(
    session: Session,
    project_id: int,
    item_id: int,
    item_data: InventoryItemUpdate
) -> InventoryItem:
    """CRUD: Actualiza un item de inventario"""
    # Verificar que el proyecto existe
    project = session.exec(
        select(Project)
        .where(Project.id == project_id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verificar que el item existe
    existing_item = session.exec(
        select(InventoryItem)
        .where(InventoryItem.id == item_id)
        .where(InventoryItem.project_id == project_id)
    ).first()

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found in this project")

    # Copy the old item data
    old_item_data = InventoryItem(
        id=existing_item.id,
        name=existing_item.name,
        category=existing_item.category,
        total=existing_item.total,
        used=existing_item.used,
        remaining=existing_item.remaining,
        unit=existing_item.unit,
        unit_cost=existing_item.unit_cost,
        supplier=existing_item.supplier,
        status=existing_item.status,
        project_id=project_id
    )

    # Actualizar el item de inventario
    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(existing_item, key, value)

    session.add(existing_item)
    session.commit()
    session.refresh(existing_item)

    # Send notifications
    notify_inventory_update(
        session=session,
        inventory_item=existing_item,
        update_data={
            k: {"old": getattr(old_item_data, k), "new": v}
            for k, v in item_data.model_dump(exclude_unset=True).items()
            if getattr(old_item_data, k) != v
        }
    )

    return existing_item

def update_inventories_in_project(
        session: Session,
        project_id: int,
        inventories_data: list[InventoryBackend]
):
    """Actualiza los items de inventario en un proyecto"""
    for inventory_data in inventories_data:
        if inventory_data.updated:
            update_inventory_item(
                session=session,
                project_id=project_id,
                item_id=inventory_data.id,
                item_data=InventoryItemUpdate.model_validate(inventory_data)
            )
        elif inventory_data.created:
            create_inventory_item(
                session=session,
                project_id=project_id,
                item_data=InventoryItemCreate.model_validate(inventory_data)
            )
        else:
            delete_inventory_item(
                session=session,
                project_id=project_id,
                item_id=inventory_data.id
            )


def delete_inventory_item(
    session: Session,
    project_id: int,
    item_id: int
) -> InventoryItem:
    """CRUD: Elimina un item de inventario"""
    # Verificar que el proyecto existe
    project = session.exec(
        select(Project)
        .where(Project.id == project_id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verificar que el item existe
    existing_item = session.exec(
        select(InventoryItem)
        .where(InventoryItem.id == item_id)
        .where(InventoryItem.project_id == project_id)
    ).first()

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found in this project")


    try:
        copy_important_data = {
            "name": existing_item.name,
            "unit": existing_item.unit,
            "unit_cost": existing_item.unit_cost,
            "total": existing_item.total,
            "used": existing_item.used
        }
        session.delete(existing_item)
        session.commit()
        notify_inventory_deletion(
            session=session,
            inventory_data=copy_important_data,
            project_id=project_id
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el item de inventario")

    return existing_item