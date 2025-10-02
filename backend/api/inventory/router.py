"""
Inventory Router - Thin route handlers

All route handlers follow the pattern:
1. Validate input
2. Call helpers for data loading
3. Call service for business logic
4. Call presenters for response formatting
5. Return response
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import (
    InventoryCheck, InventoryCheckCreate, InventoryCheckRead,
    InventoryCheckItem, WarehouseItem, WarehouseOperation, WarehouseOperationType,
    OrderItemRequest
)
from services.inventory_service import InventoryService, InsufficientStockError, ReservationError
from auth_utils import get_current_user_shop_id

from . import helpers
from . import presenters

router = APIRouter()


# ===== Inventory Checks =====

@router.get("/", response_model=List[InventoryCheckRead])
async def get_inventory_checks(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    skip: int = 0,
    limit: int = 100
):
    """Get list of inventory checks"""
    checks = await helpers.get_inventory_checks(session, shop_id=shop_id, skip=skip, limit=limit)

    # Load items for each check and build responses
    result_checks = []
    for check in checks:
        items = await helpers.load_inventory_check_items(session, check.id)
        result_checks.append(presenters.build_inventory_check_read(check, items))

    return result_checks


@router.post("/", response_model=InventoryCheckRead)
async def create_inventory_check(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    inventory_data: InventoryCheckCreate
):
    """Create a new inventory check"""
    # Create the inventory check with shop_id
    inventory_check = InventoryCheck(
        shop_id=shop_id,
        conducted_by=inventory_data.conducted_by,
        comment=inventory_data.comment,
        status="pending"
    )
    session.add(inventory_check)
    await session.flush()  # Get the ID without committing

    # Create inventory check items
    for item_data in inventory_data.items:
        # Get warehouse item (verify belongs to shop)
        warehouse_item = await helpers.get_warehouse_item_by_id(
            session, item_data["warehouse_item_id"], shop_id=shop_id, raise_if_not_found=True
        )

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

    # Load items for response
    items = await helpers.load_inventory_check_items(session, inventory_check.id)
    return presenters.build_inventory_check_read(inventory_check, items)


# ===== Specific Routes (must come BEFORE dynamic /{check_id}) =====

@router.get("/prepare/items", response_model=List[dict])
async def get_warehouse_items_for_inventory(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Get all warehouse items for inventory preparation"""
    items = await helpers.get_warehouse_items(session, shop_id=shop_id, order_by_name=True)
    return [presenters.build_warehouse_item_for_inventory(item) for item in items]


@router.get("/summary", response_model=dict)
async def get_inventory_summary(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """
    Get comprehensive inventory summary with reservations.

    Returns overview statistics and detailed item information.
    """
    return await InventoryService.get_inventory_summary(session, shop_id=shop_id)


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
        return presenters.build_warehouse_item_availability(
            warehouse_item_id, total_qty, reserved_qty, available_qty
        )
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


# ===== Dynamic Routes (must come AFTER specific routes) =====

@router.get("/{check_id}", response_model=InventoryCheckRead)
async def get_inventory_check(
    *,
    session: AsyncSession = Depends(get_session),
    check_id: int
):
    """Get a specific inventory check"""
    check, items = await helpers.load_inventory_check_with_items(session, check_id)
    return presenters.build_inventory_check_read(check, items)


@router.post("/{check_id}/apply")
async def apply_inventory_check(
    *,
    session: AsyncSession = Depends(get_session),
    check_id: int
):
    """Apply inventory check - update warehouse quantities"""
    # Get inventory check
    check = await helpers.get_inventory_check_by_id(session, check_id, raise_if_not_found=True)

    if check.status == "applied":
        raise HTTPException(status_code=400, detail="Inventory check already applied")

    # Get all items for this check
    check_items = await helpers.load_inventory_check_items(session, check_id)

    # Apply changes to warehouse
    for check_item in check_items:
        if check_item.difference != 0:
            # Get warehouse item
            warehouse_item = await helpers.get_warehouse_item_by_id(
                session, check_item.warehouse_item_id, raise_if_not_found=False
            )
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
