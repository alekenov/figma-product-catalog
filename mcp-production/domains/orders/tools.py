"""Order management tools for Production API."""

import sys
sys.path.append('../../mcp-shared')

from client import CvetyProductionClient
from mcp_shared.schemas.orders import OrderResponse, OrderStatusUpdate
from mcp_shared.enums import OrderStatus
from mcp_shared.utils.logging import get_logger

logger = get_logger(__name__)


async def list_orders_production(
    status: str | None = None,
    customer_phone: str | None = None,
    limit: int = 20
) -> dict:
    """
    List orders from cvety.kz production API.

    Args:
        status: Filter by status ('assembled', 'in-transit', 'delivered', etc.)
        customer_phone: Filter by customer phone number
        limit: Maximum number of orders to return

    Returns:
        {
            "success": true,
            "data": [OrderResponse...],
            "total": 50
        }

    Example:
        # Get orders in transit
        await list_orders_production(status="in-transit", limit=10)
    """
    client = CvetyProductionClient()

    params = {"limit": limit}

    if status:
        params["status"] = status

    if customer_phone:
        params["customer_phone"] = customer_phone

    logger.info(f"Listing orders from Production: {params}")

    response = await client.get("/orders", params=params)

    return {
        "success": response.get("success", False),
        "data": response.get("data", []),
        "total": len(response.get("data", []))
    }


async def get_order_details_production(order_id: int) -> dict:
    """
    Get detailed information about a specific order.

    Args:
        order_id: Order ID

    Returns:
        {
            "success": true,
            "data": {OrderResponse}
        }

    Example:
        await get_order_details_production(order_id=123891)
    """
    client = CvetyProductionClient()

    logger.info(f"Getting order {order_id} details from Production")

    response = await client.get(f"/orders/detail/{order_id}")

    return {
        "success": response.get("success", False),
        "data": response.get("data", {})
    }


async def update_order_status_production(
    order_id: int,
    new_status: str,
    notes: str | None = None
) -> dict:
    """
    Update order status on Production API.

    Valid status transitions:
    - assembled → in-transit, cancelled
    - in-transit → delivered, cancelled

    Args:
        order_id: Order ID
        new_status: New status ('in-transit', 'delivered', 'cancelled')
        notes: Optional notes about the status change

    Returns:
        {
            "success": true,
            "data": {
                "old_status": "assembled",
                "new_status": "in-transit"
            }
        }

    Example:
        # Mark order as in transit
        await update_order_status_production(
            order_id=123891,
            new_status="in-transit",
            notes="Курьер выехал"
        )
    """
    client = CvetyProductionClient()

    # Validate status transition (optional check)
    # valid_transitions = OrderStatus.get_valid_transitions(current_status)

    payload = {
        "id": order_id,
        "status": new_status
    }

    if notes:
        payload["notes"] = notes

    logger.info(f"Updating order {order_id} status to '{new_status}' on Production")

    response = await client.post("/update-order-status", json_data=payload)

    return {
        "success": response.get("status", False),
        "data": response.get("data", {}),
        "timestamp": response.get("timestamp")
    }
