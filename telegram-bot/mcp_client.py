"""
MCP Client for calling Flower Shop API tools via MCP server.
Provides typed interface for all available MCP tools.
"""
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class MCPClient:
    """Client for interacting with MCP server over HTTP."""

    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool by name with given arguments.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Dictionary of tool arguments

        Returns:
            Tool execution result

        Raises:
            httpx.HTTPError: If request fails
        """
        response = await self.client.post(
            f"{self.mcp_server_url}/call-tool",
            json={
                "name": tool_name,
                "arguments": arguments
            }
        )
        response.raise_for_status()
        return response.json()

    # Product Tools
    async def list_products(
        self,
        shop_id: int,
        search: Optional[str] = None,
        product_type: Optional[str] = None,
        enabled_only: bool = True,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get list of products with filtering."""
        result = await self.call_tool("list_products", {
            "shop_id": shop_id,
            "search": search,
            "product_type": product_type,
            "enabled_only": enabled_only,
            "min_price": min_price,
            "max_price": max_price,
            "skip": skip,
            "limit": limit,
        })
        return result.get("content", [])

    async def get_product(
        self,
        product_id: int,
        shop_id: int
    ) -> Dict[str, Any]:
        """Get single product by ID."""
        result = await self.call_tool("get_product", {
            "product_id": product_id,
            "shop_id": shop_id,
        })
        return result.get("content", {})

    # Order Tools
    async def create_order(
        self,
        customer_name: str,
        customer_phone: str,
        delivery_address: str,
        delivery_date: str,
        delivery_time: str,
        shop_id: int,
        items: List[Dict[str, Any]],
        total_price: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new order.

        Args:
            customer_name: Customer full name
            customer_phone: Customer phone number
            delivery_address: Delivery address
            delivery_date: Delivery date (YYYY-MM-DD)
            delivery_time: Delivery time (HH:MM)
            shop_id: Shop ID
            items: List of order items [{"product_id": 1, "quantity": 2}]
            total_price: Total order price in smallest currency unit
            notes: Optional order notes

        Returns:
            Created order with ID
        """
        result = await self.call_tool("create_order", {
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "delivery_address": delivery_address,
            "delivery_date": delivery_date,
            "delivery_time": delivery_time,
            "shop_id": shop_id,
            "items": items,
            "total_price": total_price,
            "notes": notes,
        })
        return result.get("content", {})

    async def get_order(
        self,
        order_id: int,
        shop_id: int
    ) -> Dict[str, Any]:
        """Get order details by ID."""
        result = await self.call_tool("get_order", {
            "order_id": order_id,
            "shop_id": shop_id,
        })
        return result.get("content", {})

    async def track_order_by_phone(
        self,
        customer_phone: str,
        shop_id: int
    ) -> List[Dict[str, Any]]:
        """Track orders by customer phone number."""
        result = await self.call_tool("track_order_by_phone", {
            "customer_phone": customer_phone,
            "shop_id": shop_id,
        })
        return result.get("content", [])

    # Shop Settings Tools
    async def get_shop_settings(
        self,
        shop_id: int
    ) -> Dict[str, Any]:
        """Get shop settings and configuration."""
        result = await self.call_tool("get_shop_settings", {
            "shop_id": shop_id,
        })
        return result.get("content", {})

    async def get_working_hours(
        self,
        shop_id: int
    ) -> List[Dict[str, Any]]:
        """Get shop working hours schedule."""
        result = await self.call_tool("get_working_hours", {
            "shop_id": shop_id,
        })
        return result.get("content", [])


# Convenience function for creating client
def create_mcp_client(mcp_server_url: str) -> MCPClient:
    """Create and return MCP client instance."""
    return MCPClient(mcp_server_url)
