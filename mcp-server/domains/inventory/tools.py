"""
Inventory management tools for MCP server.
"""
from typing import List, Dict, Any, Optional
from core.api_client import api_client
from core.registry import ToolRegistry


@ToolRegistry.register(domain="inventory", requires_auth=True)
async def list_warehouse_items(
    token: str,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Get list of warehouse inventory items (admin only)."""
    params = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search

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
