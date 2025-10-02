"""
Inventory Helpers - Reusable data loading utilities

Consolidates database queries for inventory checks, warehouse items, and operations.
Provides clean interfaces for loading inventory data with relations.
"""

from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from fastapi import HTTPException

from models import (
    InventoryCheck, InventoryCheckItem, WarehouseItem, WarehouseOperation
)


async def get_inventory_checks(
    session: AsyncSession,
    shop_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[InventoryCheck]:
    """
    Get list of inventory checks, ordered by creation date.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy
        skip: Number of checks to skip (pagination)
        limit: Maximum number of checks to return

    Returns:
        List of InventoryCheck instances
    """
    query = select(InventoryCheck)

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(InventoryCheck.shop_id == shop_id)

    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(desc(InventoryCheck.created_at))
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_inventory_check_by_id(
    session: AsyncSession,
    check_id: int,
    raise_if_not_found: bool = True
) -> Optional[InventoryCheck]:
    """
    Get inventory check by ID.

    Args:
        session: Database session
        check_id: Inventory check ID
        raise_if_not_found: Raise HTTPException if not found

    Returns:
        InventoryCheck instance or None

    Raises:
        HTTPException: If check not found and raise_if_not_found=True
    """
    check = await session.get(InventoryCheck, check_id)
    if not check and raise_if_not_found:
        raise HTTPException(status_code=404, detail="Inventory check not found")
    return check


async def load_inventory_check_items(
    session: AsyncSession,
    check_id: int
) -> List[InventoryCheckItem]:
    """
    Load all items for an inventory check.

    Args:
        session: Database session
        check_id: Inventory check ID

    Returns:
        List of InventoryCheckItem instances
    """
    query = select(InventoryCheckItem).where(
        InventoryCheckItem.inventory_check_id == check_id
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def load_inventory_check_with_items(
    session: AsyncSession,
    check_id: int
) -> Tuple[InventoryCheck, List[InventoryCheckItem]]:
    """
    Load inventory check with all its items.

    Args:
        session: Database session
        check_id: Inventory check ID

    Returns:
        Tuple of (InventoryCheck, List[InventoryCheckItem])

    Raises:
        HTTPException: If check not found
    """
    check = await get_inventory_check_by_id(session, check_id, raise_if_not_found=True)
    items = await load_inventory_check_items(session, check_id)
    return check, items


async def get_warehouse_items(
    session: AsyncSession,
    shop_id: Optional[int] = None,
    order_by_name: bool = True
) -> List[WarehouseItem]:
    """
    Get all warehouse items.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy
        order_by_name: Order results by name

    Returns:
        List of WarehouseItem instances
    """
    query = select(WarehouseItem)

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(WarehouseItem.shop_id == shop_id)

    if order_by_name:
        query = query.order_by(WarehouseItem.name)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_warehouse_item_by_id(
    session: AsyncSession,
    warehouse_item_id: int,
    shop_id: Optional[int] = None,
    raise_if_not_found: bool = True
) -> Optional[WarehouseItem]:
    """
    Get warehouse item by ID.

    Args:
        session: Database session
        warehouse_item_id: Warehouse item ID
        shop_id: Verify item belongs to shop_id for multi-tenancy
        raise_if_not_found: Raise HTTPException if not found

    Returns:
        WarehouseItem instance or None

    Raises:
        HTTPException: If item not found, doesn't belong to shop, and raise_if_not_found=True
    """
    item = await session.get(WarehouseItem, warehouse_item_id)

    if not item:
        if raise_if_not_found:
            raise HTTPException(status_code=404, detail=f"Warehouse item {warehouse_item_id} not found")
        return None

    # Verify item belongs to shop if shop_id provided
    if shop_id is not None and item.shop_id != shop_id:
        if raise_if_not_found:
            raise HTTPException(status_code=403, detail="Warehouse item does not belong to your shop")
        return None

    return item


async def get_warehouse_operations(
    session: AsyncSession,
    warehouse_item_id: Optional[int] = None,
    limit: int = 100
) -> List[WarehouseOperation]:
    """
    Get warehouse operations, optionally filtered by warehouse item.

    Args:
        session: Database session
        warehouse_item_id: Filter by warehouse item ID (optional)
        limit: Maximum number of operations to return

    Returns:
        List of WarehouseOperation instances
    """
    query = select(WarehouseOperation).order_by(desc(WarehouseOperation.created_at))

    if warehouse_item_id:
        query = query.where(WarehouseOperation.warehouse_item_id == warehouse_item_id)

    query = query.limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())
