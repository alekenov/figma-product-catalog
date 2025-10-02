"""
Inventory Presenters - Response formatting and data transformation

Consolidates response building logic for inventory checks and warehouse items.
Handles mapping between backend models and frontend expectations.
"""

from typing import List, Dict, Any
from models import (
    InventoryCheck, InventoryCheckItem, WarehouseItem,
    InventoryCheckRead, InventoryCheckItemRead
)


def build_inventory_check_item_read(item: InventoryCheckItem) -> InventoryCheckItemRead:
    """
    Build InventoryCheckItemRead from InventoryCheckItem.

    Args:
        item: InventoryCheckItem instance

    Returns:
        InventoryCheckItemRead instance
    """
    return InventoryCheckItemRead(
        id=item.id,
        inventory_check_id=item.inventory_check_id,
        warehouse_item_id=item.warehouse_item_id,
        warehouse_item_name=item.warehouse_item_name,
        current_quantity=item.current_quantity,
        actual_quantity=item.actual_quantity,
        difference=item.difference,
        created_at=item.created_at
    )


def build_inventory_check_read(
    check: InventoryCheck,
    items: List[InventoryCheckItem]
) -> InventoryCheckRead:
    """
    Build InventoryCheckRead from check and items.

    Args:
        check: InventoryCheck instance
        items: List of InventoryCheckItem instances

    Returns:
        InventoryCheckRead instance with items
    """
    return InventoryCheckRead(
        id=check.id,
        conducted_by=check.conducted_by,
        comment=check.comment,
        status=check.status,
        applied_at=check.applied_at,
        created_at=check.created_at,
        items=[build_inventory_check_item_read(item) for item in items]
    )


def build_warehouse_item_for_inventory(item: WarehouseItem) -> Dict[str, Any]:
    """
    Build warehouse item dictionary for inventory preparation.

    Args:
        item: WarehouseItem instance

    Returns:
        Dictionary with item data for inventory UI
    """
    return {
        "id": item.id,
        "name": item.name,
        "current_quantity": item.quantity,
        "image": item.image
    }


def build_warehouse_item_availability(
    warehouse_item_id: int,
    total_quantity: int,
    reserved_quantity: int,
    available_quantity: int
) -> Dict[str, Any]:
    """
    Build availability response for warehouse item.

    Args:
        warehouse_item_id: Warehouse item ID
        total_quantity: Total quantity in stock
        reserved_quantity: Quantity reserved for orders
        available_quantity: Available quantity (total - reserved)

    Returns:
        Dictionary with availability information
    """
    return {
        "warehouse_item_id": warehouse_item_id,
        "total_quantity": total_quantity,
        "reserved_quantity": reserved_quantity,
        "available_quantity": available_quantity
    }


def build_inventory_summary(
    overview: Dict[str, Any],
    items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build inventory summary response.

    Args:
        overview: Overview statistics dictionary
        items: List of item detail dictionaries

    Returns:
        Complete inventory summary
    """
    return {
        "overview": overview,
        "items": items
    }
