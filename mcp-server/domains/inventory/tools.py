"""
Inventory management tools for MCP server.
"""
from typing import List, Dict, Any, Optional
from core.api_client import api_client
from core.registry import ToolRegistry
from core.utils import merge_required_optional


@ToolRegistry.register(domain="inventory", requires_auth=True)
async def list_warehouse_items(
    token: str,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Get list of warehouse inventory items (admin only)."""
    params = merge_required_optional(
        {"skip": skip, "limit": limit},
        {"search": search},
    )
    return await api_client.get("/warehouse", token=token, params=params)


@ToolRegistry.register(domain="inventory", requires_auth=True)
async def add_warehouse_stock(
    token: str,
    warehouse_item_id: int,
    quantity: int,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Add stock to warehouse item (admin only)."""
    data = {
        "warehouse_item_id": warehouse_item_id,
        "operation_type": "delivery",
        "quantity_change": quantity,
        "description": notes or "Поставка через MCP",
    }

    return await api_client.post(
        f"/warehouse/{warehouse_item_id}/delivery",
        json_data=data,
        token=token
    )


# ===== Warehouse Operations =====

@ToolRegistry.register(domain="inventory", requires_auth=True)
async def record_warehouse_operation(
    token: str,
    warehouse_item_id: int,
    quantity: int,
    operation_type: str,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Record warehouse stock movement operation (admin only).

    Tracks all types of inventory changes for audit trail and reporting.
    Routes to different backend endpoints based on operation type.

    Args:
        token: Admin JWT token
        warehouse_item_id: ID of warehouse item
        quantity: Quantity change (positive for IN, negative for OUT/WRITE_OFF)
        operation_type: Type of operation:
            - "IN" - Stock arrival/delivery
            - "OUT" - Stock usage/consumption (sale)
            - "WRITE_OFF" - Stock write-off/damage
        notes: Optional operation notes/description

    Returns:
        Created operation record with ID and timestamp

    Example:
        # Record delivery (stock arrival)
        await record_warehouse_operation(
            token=admin_token,
            warehouse_item_id=5,  # Roses
            quantity=50,
            operation_type="IN",
            notes="Delivery from supplier"
        )

        # Record sale (used 10 roses for bouquet)
        await record_warehouse_operation(
            token=admin_token,
            warehouse_item_id=5,
            quantity=-10,
            operation_type="OUT",
            notes="Sold in order #123"
        )

        # Record writeoff (damaged goods)
        await record_warehouse_operation(
            token=admin_token,
            warehouse_item_id=8,
            quantity=-3,
            operation_type="WRITE_OFF",
            notes="Damaged tulips"
        )
    """
    # Map operation_type to backend endpoint
    endpoint_map = {
        "IN": "delivery",
        "OUT": "sale",
        "WRITE_OFF": "writeoff",
    }

    endpoint = endpoint_map.get(operation_type)
    if not endpoint:
        raise ValueError(
            f"Unsupported operation_type: {operation_type}. "
            f"Supported types: {list(endpoint_map.keys())}"
        )

    # Build request data according to backend schema
    data = {
        "quantity_change": quantity,
        "description": notes or (
            "Операция через MCP" if operation_type != "WRITE_OFF" else "Списание"
        ),
    }

    # Add reason field for writeoff
    if operation_type == "WRITE_OFF" and notes:
        data["reason"] = notes

    return await api_client.post(
        f"/warehouse/{warehouse_item_id}/{endpoint}",
        json_data=data,
        token=token
    )


@ToolRegistry.register(domain="inventory", requires_auth=True)
async def get_warehouse_history(
    token: str,
    warehouse_item_id: int,
    operation_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get warehouse operations history for a specific item (admin only).

    Provides audit trail of all inventory movements for a warehouse item.

    Args:
        token: Admin JWT token
        warehouse_item_id: ID of warehouse item (required)
        operation_type: Filter by type (DELIVERY/SALE/WRITEOFF/PRICE_CHANGE/INVENTORY) (optional)
        skip: Pagination offset (default: 0)
        limit: Max results per page (default: 50, max: 100)

    Returns:
        List of operation records with details, user, timestamp

    Example:
        # Get all operations for roses
        await get_warehouse_history(
            token=admin_token,
            warehouse_item_id=5
        )

        # Get only writeoff operations for tulips
        await get_warehouse_history(
            token=admin_token,
            warehouse_item_id=8,
            operation_type="WRITEOFF"
        )
    """
    params = {"skip": skip, "limit": limit}

    if operation_type:
        params["operation_type"] = operation_type

    return await api_client.get(
        f"/warehouse/{warehouse_item_id}/operations",
        token=token,
        params=params
    )


# ===== Inventory Checks =====

@ToolRegistry.register(domain="inventory", requires_auth=True)
async def create_inventory_check(
    token: str,
    conducted_by: str,
    items: List[dict],
    comment: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create new inventory check with all items (admin only).

    Creates a complete inventory audit session with physical count verification.
    All items must be provided at creation - items cannot be added later.

    Args:
        token: Admin JWT token
        conducted_by: Name of person conducting the inventory (required)
        items: List of items to check (required). Each item must have:
            - warehouse_item_id (int): ID of warehouse item
            - actual_quantity (int): Physically counted quantity
        comment: Optional check notes (e.g., "Monthly inventory", "Annual audit")

    Returns:
        Created inventory check with ID, timestamp, and items with variance calculations

    Example:
        # Create monthly inventory check for roses and tulips
        result = await create_inventory_check(
            token=admin_token,
            conducted_by="Ivan Petrov",
            items=[
                {"warehouse_item_id": 5, "actual_quantity": 48},  # Roses: found 48
                {"warehouse_item_id": 8, "actual_quantity": 30}   # Tulips: found 30
            ],
            comment="Ежемесячная инвентаризация - Январь 2025"
        )
        check_id = result["id"]
        # Result will include variance calculations (actual - expected)
    """
    data = {
        "conducted_by": conducted_by,
        "items": items,
    }

    if comment:
        data["comment"] = comment

    return await api_client.post(
        "/inventory/",
        json_data=data,
        token=token
    )


@ToolRegistry.register(domain="inventory", requires_auth=True)
async def list_inventory_checks(
    token: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Get list of inventory checks (admin only).

    Returns all inventory audit sessions with summary statistics.

    Args:
        token: Admin JWT token
        skip: Pagination offset (default: 0)
        limit: Max results per page (default: 20)

    Returns:
        List of inventory checks with status and item counts

    Example:
        # Get recent inventory checks
        checks = await list_inventory_checks(
            token=admin_token,
            limit=10
        )
    """
    params = {"skip": skip, "limit": limit}

    return await api_client.get(
        "/inventory/",
        token=token,
        params=params
    )
