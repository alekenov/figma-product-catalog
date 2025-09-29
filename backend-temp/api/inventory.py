from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from database import get_session
from models import (
    InventoryCheck, InventoryCheckCreate, InventoryCheckRead,
    InventoryCheckItem, InventoryCheckItemCreate, InventoryCheckItemRead,
    WarehouseItem, WarehouseOperation, WarehouseOperationType,
    OrderItemRequest, ProductAvailability, AvailabilityResponse
)
from services.inventory_service import InventoryService, InsufficientStockError, ReservationError

router = APIRouter()


@router.get("/", response_model=List[InventoryCheckRead])
async def get_inventory_checks(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """Get list of inventory checks"""

    query = select(InventoryCheck).offset(skip).limit(limit).order_by(desc(InventoryCheck.created_at))
    result = await session.execute(query)
    checks = result.scalars().all()

    # Load items for each check and create response objects
    result_checks = []
    for check in checks:
        items_result = await session.execute(
            select(InventoryCheckItem)
            .where(InventoryCheckItem.inventory_check_id == check.id)
        )
        items = items_result.scalars().all()

        result_checks.append(InventoryCheckRead(
            id=check.id,
            conducted_by=check.conducted_by,
            comment=check.comment,
            status=check.status,
            applied_at=check.applied_at,
            created_at=check.created_at,
            items=[InventoryCheckItemRead(
                id=item.id,
                inventory_check_id=item.inventory_check_id,
                warehouse_item_id=item.warehouse_item_id,
                warehouse_item_name=item.warehouse_item_name,
                current_quantity=item.current_quantity,
                actual_quantity=item.actual_quantity,
                difference=item.difference,
                created_at=item.created_at
            ) for item in items]
        ))

    return result_checks


@router.post("/", response_model=InventoryCheckRead)
async def create_inventory_check(
    *,
    session: AsyncSession = Depends(get_session),
    inventory_data: InventoryCheckCreate
):
    """Create a new inventory check"""

    # Create the inventory check
    inventory_check = InventoryCheck(
        conducted_by=inventory_data.conducted_by,
        comment=inventory_data.comment,
        status="pending"
    )
    session.add(inventory_check)
    await session.flush()  # Get the ID without committing

    # Create inventory check items
    for item_data in inventory_data.items:
        # Get warehouse item
        warehouse_item = await session.get(WarehouseItem, item_data["warehouse_item_id"])
        if not warehouse_item:
            raise HTTPException(status_code=404, detail=f"Warehouse item {item_data['warehouse_item_id']} not found")

        # Calculate difference
        actual_quantity = item_data["actual_quantity"]
        difference = actual_quantity - warehouse_item.quantity

        # Create inventory check item
        check_item = InventoryCheckItem(
            inventory_check_id=inventory_check.id,
            warehouse_item_id=warehouse_item.id,
            warehouse_item_name=warehouse_item.name,
            current_quantity=warehouse_item.quantity,
            actual_quantity=actual_quantity,
            difference=difference
        )
        session.add(check_item)

    await session.commit()
    await session.refresh(inventory_check)

    # Load items
    items_result = await session.execute(
        select(InventoryCheckItem)
        .where(InventoryCheckItem.inventory_check_id == inventory_check.id)
    )
    items = items_result.scalars().all()

    # Create response manually to avoid relationship issues
    return InventoryCheckRead(
        id=inventory_check.id,
        conducted_by=inventory_check.conducted_by,
        comment=inventory_check.comment,
        status=inventory_check.status,
        applied_at=inventory_check.applied_at,
        created_at=inventory_check.created_at,
        items=[InventoryCheckItemRead(
            id=item.id,
            inventory_check_id=item.inventory_check_id,
            warehouse_item_id=item.warehouse_item_id,
            warehouse_item_name=item.warehouse_item_name,
            current_quantity=item.current_quantity,
            actual_quantity=item.actual_quantity,
            difference=item.difference,
            created_at=item.created_at
        ) for item in items]
    )


@router.get("/{check_id}", response_model=InventoryCheckRead)
async def get_inventory_check(
    *,
    session: AsyncSession = Depends(get_session),
    check_id: int
):
    """Get a specific inventory check"""

    check = await session.get(InventoryCheck, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")

    # Load items
    items_result = await session.execute(
        select(InventoryCheckItem)
        .where(InventoryCheckItem.inventory_check_id == check_id)
    )
    items = items_result.scalars().all()

    return InventoryCheckRead(
        id=check.id,
        conducted_by=check.conducted_by,
        comment=check.comment,
        status=check.status,
        applied_at=check.applied_at,
        created_at=check.created_at,
        items=[InventoryCheckItemRead(
            id=item.id,
            inventory_check_id=item.inventory_check_id,
            warehouse_item_id=item.warehouse_item_id,
            warehouse_item_name=item.warehouse_item_name,
            current_quantity=item.current_quantity,
            actual_quantity=item.actual_quantity,
            difference=item.difference,
            created_at=item.created_at
        ) for item in items]
    )


@router.post("/{check_id}/apply")
async def apply_inventory_check(
    *,
    session: AsyncSession = Depends(get_session),
    check_id: int
):
    """Apply inventory check - update warehouse quantities"""

    # Get inventory check
    check = await session.get(InventoryCheck, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")

    if check.status == "applied":
        raise HTTPException(status_code=400, detail="Inventory check already applied")

    # Get all items for this check
    items_result = await session.execute(
        select(InventoryCheckItem)
        .where(InventoryCheckItem.inventory_check_id == check_id)
    )
    check_items = items_result.scalars().all()

    # Apply changes to warehouse
    for check_item in check_items:
        if check_item.difference != 0:
            # Get warehouse item
            warehouse_item = await session.get(WarehouseItem, check_item.warehouse_item_id)
            if not warehouse_item:
                continue

            # Update quantity
            old_quantity = warehouse_item.quantity
            warehouse_item.quantity = check_item.actual_quantity

            # Create operation record
            description = f"Инвентаризация: было {old_quantity} шт, стало {check_item.actual_quantity} шт"
            if check_item.difference > 0:
                description += f" (излишки: +{check_item.difference} шт)"
            else:
                description += f" (недостача: {check_item.difference} шт)"

            if check.comment:
                description += f". Комментарий: {check.comment}"

            description += f". Проводил: {check.conducted_by}"

            operation = WarehouseOperation(
                warehouse_item_id=warehouse_item.id,
                operation_type=WarehouseOperationType.INVENTORY,
                quantity_change=check_item.difference,
                balance_after=warehouse_item.quantity,
                description=description
            )
            session.add(operation)

    # Update inventory check status
    check.status = "applied"
    check.applied_at = datetime.now()

    await session.commit()

    return {"message": "Inventory check applied successfully", "check_id": check_id}


@router.get("/prepare/items", response_model=List[dict])
async def get_warehouse_items_for_inventory(
    *,
    session: AsyncSession = Depends(get_session)
):
    """Get all warehouse items for inventory preparation"""

    query = select(WarehouseItem).order_by(WarehouseItem.name)
    result = await session.execute(query)
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "current_quantity": item.quantity,
            "image": item.image
        }
        for item in items
    ]


# ===============================
# Inventory Service Integration
# ===============================

@router.get("/summary", response_model=dict)
async def get_inventory_summary(
    *,
    session: AsyncSession = Depends(get_session)
):
    """
    Get comprehensive inventory summary with reservations.

    Returns overview statistics and detailed item information.
    """
    return await InventoryService.get_inventory_summary(session)


@router.get("/warehouse-items/{warehouse_item_id}/available", response_model=dict)
async def get_warehouse_item_availability(
    *,
    session: AsyncSession = Depends(get_session),
    warehouse_item_id: int
):
    """
    Get available quantity for a warehouse item considering reservations.

    Returns total, reserved, and available quantities.
    """
    try:
        total_qty, reserved_qty, available_qty = await InventoryService.calculate_available_quantity(
            session, warehouse_item_id
        )
        return {
            "warehouse_item_id": warehouse_item_id,
            "total_quantity": total_qty,
            "reserved_quantity": reserved_qty,
            "available_quantity": available_qty
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cleanup-expired-reservations", response_model=dict)
async def cleanup_expired_reservations(
    *,
    session: AsyncSession = Depends(get_session),
    max_age_hours: int = 72,
    dry_run: bool = True
):
    """
    Clean up expired reservations based on order age and status.

    This maintenance endpoint helps prevent inventory from being locked
    indefinitely by abandoned orders.
    """
    try:
        stats = await InventoryService.cleanup_expired_reservations(
            session, max_age_hours, dry_run
        )
        return {
            "message": "Cleanup completed" if not dry_run else "Cleanup simulation completed",
            "dry_run": dry_run,
            "max_age_hours": max_age_hours,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup reservations: {str(e)}")


@router.post("/validate-order-items", response_model=dict)
async def validate_order_items_stock(
    *,
    session: AsyncSession = Depends(get_session),
    order_items: List[OrderItemRequest]
):
    """
    Validate that all order items have sufficient stock.

    Returns validation errors if any items have insufficient stock.
    """
    errors = await InventoryService.validate_order_items_stock(session, order_items)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "items_checked": len(order_items)
    }