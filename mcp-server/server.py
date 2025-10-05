"""
Flower Shop MCP Server

Provides tools for interacting with the Figma Product Catalog backend API.
Includes products, orders, auth, inventory, and shop management operations.
"""

import httpx
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8014/api/v1")
DEFAULT_SHOP_ID = int(os.getenv("DEFAULT_SHOP_ID", "8"))

# Create MCP server instance
mcp = FastMCP(
    name="Flower Shop API",
    instructions="""
    This server provides access to a multi-tenant flower shop management system.

    Main capabilities:
    - Product catalog management (CRUD operations)
    - Order management and tracking
    - Authentication and user management
    - Inventory and warehouse operations
    - Shop settings and configuration

    All authenticated operations require a valid JWT token obtained via login.
    Multi-tenancy is enforced via shop_id in JWT tokens.
    """,
)


# ===== Helper Functions =====

async def make_request(
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Make HTTP request to backend API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path (e.g., "/products")
        token: JWT token for authenticated requests
        json_data: JSON body for POST/PUT requests
        params: Query parameters

    Returns:
        JSON response as dictionary

    Raises:
        Exception: If request fails
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            params=params,
        )

        if response.status_code >= 400:
            raise Exception(
                f"API request failed: {response.status_code} - {response.text}"
            )

        return response.json()


# ===== Authentication Tools =====

@mcp.tool()
async def login(phone: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user and get access token.

    Args:
        phone: User phone number (e.g., "77015211545")
        password: User password

    Returns:
        Dictionary with access_token, token_type, and user info

    Example:
        login(phone="77015211545", password="securepass123")
    """
    result = await make_request(
        method="POST",
        endpoint="/auth/login",
        json_data={"phone": phone, "password": password},
    )
    return result


@mcp.tool()
async def get_current_user(token: str) -> Dict[str, Any]:
    """
    Get current authenticated user information.

    Args:
        token: JWT access token from login

    Returns:
        User information including id, phone, role, shop_id
    """
    result = await make_request(
        method="GET",
        endpoint="/auth/me",
        token=token,
    )
    return result


# ===== Product Tools =====

@mcp.tool()
async def list_products(
    shop_id: Optional[int] = None,
    search: Optional[str] = None,
    product_type: Optional[str] = None,
    enabled_only: bool = True,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Get list of products with filtering.

    Args:
        shop_id: Filter by shop ID (required for public access)
        search: Search in product names
        product_type: Filter by type (ready, custom, gift)
        enabled_only: Show only enabled products
        min_price: Minimum price in tenge
        max_price: Maximum price in tenge
        skip: Number of products to skip (pagination)
        limit: Number of products to return (max 100)

    Returns:
        List of products with details

    Example:
        list_products(shop_id=8, search="роза", enabled_only=True, limit=10)
    """
    params = {
        "skip": skip,
        "limit": limit,
        "enabled_only": enabled_only,
    }

    if shop_id:
        params["shop_id"] = shop_id
    if search:
        params["search"] = search
    if product_type:
        params["type"] = product_type
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price

    result = await make_request(
        method="GET",
        endpoint="/products",
        params=params,
    )
    return result


@mcp.tool()
async def get_product(product_id: int, shop_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.

    Args:
        product_id: Product ID
        shop_id: Shop ID (required for public access)

    Returns:
        Product details including availability and stats
    """
    params = {}
    if shop_id:
        params["shop_id"] = shop_id

    result = await make_request(
        method="GET",
        endpoint=f"/products/{product_id}",
        params=params,
    )
    return result


@mcp.tool()
async def create_product(
    token: str,
    name: str,
    type: str,
    price: int,
    description: Optional[str] = None,
    enabled: bool = True,
) -> Dict[str, Any]:
    """
    Create a new product (admin only).

    Args:
        token: JWT access token
        name: Product name
        type: Product type (ready, custom, gift)
        price: Price in tenge
        description: Product description
        enabled: Whether product is enabled

    Returns:
        Created product details
    """
    data = {
        "name": name,
        "type": type,
        "price": price,
        "enabled": enabled,
    }

    if description:
        data["description"] = description

    result = await make_request(
        method="POST",
        endpoint="/products/admin",
        token=token,
        json_data=data,
    )
    return result


@mcp.tool()
async def update_product(
    token: str,
    product_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update an existing product (admin only).

    Args:
        token: JWT access token
        product_id: Product ID to update
        name: New product name
        price: New price in tenge
        description: New description
        enabled: New enabled status

    Returns:
        Updated product details
    """
    data = {}

    if name is not None:
        data["name"] = name
    if price is not None:
        data["price"] = price
    if description is not None:
        data["description"] = description
    if enabled is not None:
        data["enabled"] = enabled

    result = await make_request(
        method="PUT",
        endpoint=f"/products/admin/{product_id}",
        token=token,
        json_data=data,
    )
    return result


# ===== Order Tools =====

@mcp.tool()
async def list_orders(
    token: str,
    status: Optional[str] = None,
    customer_phone: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Get list of orders with filtering (admin only).

    Args:
        token: JWT access token
        status: Filter by order status (new, paid, confirmed, processing, ready, delivered, cancelled)
        customer_phone: Filter by customer phone
        search: Search in customer name or order number
        skip: Number of orders to skip
        limit: Number of orders to return

    Returns:
        List of orders with details
    """
    params = {
        "skip": skip,
        "limit": limit,
    }

    if status:
        params["status"] = status
    if customer_phone:
        params["customer_phone"] = customer_phone
    if search:
        params["search"] = search

    result = await make_request(
        method="GET",
        endpoint="/orders",
        token=token,
        params=params,
    )
    return result


@mcp.tool()
async def get_order(token: str, order_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific order (admin only).

    Args:
        token: JWT access token
        order_id: Order ID

    Returns:
        Order details including items, history, and photos
    """
    result = await make_request(
        method="GET",
        endpoint=f"/orders/{order_id}",
        token=token,
    )
    return result


@mcp.tool()
async def create_order(
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
    Create a new order (public endpoint).

    Args:
        customer_name: Customer full name
        customer_phone: Customer phone number
        delivery_address: Delivery address
        delivery_date: Delivery date (YYYY-MM-DD)
        delivery_time: Delivery time (HH:MM)
        shop_id: Shop ID
        items: List of order items [{"product_id": int, "quantity": int, "price": int}]
        total_price: Total order price in tenge
        notes: Additional notes

    Returns:
        Created order with tracking information

    Example:
        create_order(
            customer_name="Иван Иванов",
            customer_phone="77011234567",
            delivery_address="ул. Абая 1",
            delivery_date="2025-10-10",
            delivery_time="14:00",
            shop_id=8,
            items=[{"product_id": 1, "quantity": 2, "price": 5000}],
            total_price=10000
        )
    """
    data = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "delivery_address": delivery_address,
        "delivery_date": delivery_date,
        "delivery_time": delivery_time,
        "shop_id": shop_id,
        "items": items,
        "total_price": total_price,
    }

    if notes:
        data["notes"] = notes

    result = await make_request(
        method="POST",
        endpoint="/orders",
        json_data=data,
    )
    return result


@mcp.tool()
async def update_order_status(
    token: str,
    order_id: int,
    status: str,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update order status (admin only).

    Args:
        token: JWT access token
        order_id: Order ID
        status: New status (new, paid, confirmed, processing, ready, delivered, cancelled)
        notes: Optional notes about status change

    Returns:
        Updated order details
    """
    data = {"status": status}
    if notes:
        data["notes"] = notes

    result = await make_request(
        method="PATCH",
        endpoint=f"/orders/{order_id}/status",
        token=token,
        json_data=data,
    )
    return result


@mcp.tool()
async def track_order(tracking_id: str) -> Dict[str, Any]:
    """
    Track order status by tracking ID (public endpoint).

    Args:
        tracking_id: Order tracking ID from order creation

    Returns:
        Order status and basic information
    """
    result = await make_request(
        method="GET",
        endpoint=f"/orders/track/{tracking_id}",
    )
    return result


# ===== Inventory Tools =====

@mcp.tool()
async def list_warehouse_items(
    token: str,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get list of warehouse inventory items (admin only).

    Args:
        token: JWT access token
        search: Search in item names
        skip: Number of items to skip
        limit: Number of items to return

    Returns:
        List of warehouse items with quantities
    """
    params = {
        "skip": skip,
        "limit": limit,
    }

    if search:
        params["search"] = search

    result = await make_request(
        method="GET",
        endpoint="/warehouse",
        token=token,
        params=params,
    )
    return result


@mcp.tool()
async def add_warehouse_stock(
    token: str,
    warehouse_item_id: int,
    quantity: int,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add stock to warehouse item (admin only).

    Args:
        token: JWT access token
        warehouse_item_id: Warehouse item ID
        quantity: Quantity to add
        notes: Optional notes about the operation

    Returns:
        Operation details and updated quantity
    """
    data = {
        "warehouse_item_id": warehouse_item_id,
        "quantity": quantity,
        "operation_type": "in",
    }

    if notes:
        data["notes"] = notes

    result = await make_request(
        method="POST",
        endpoint="/warehouse/operations",
        token=token,
        json_data=data,
    )
    return result


# ===== Shop Tools =====

@mcp.tool()
async def get_shop_settings(token: str) -> Dict[str, Any]:
    """
    Get shop settings and configuration (admin only).

    Args:
        token: JWT access token

    Returns:
        Shop settings including name, description, contact info, working hours
    """
    result = await make_request(
        method="GET",
        endpoint="/shop/settings",
        token=token,
    )
    return result


@mcp.tool()
async def update_shop_settings(
    token: str,
    shop_name: Optional[str] = None,
    description: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update shop settings (admin only).

    Args:
        token: JWT access token
        shop_name: Shop name
        description: Shop description
        phone: Contact phone
        email: Contact email
        address: Shop address

    Returns:
        Updated shop settings
    """
    data = {}

    if shop_name is not None:
        data["shop_name"] = shop_name
    if description is not None:
        data["description"] = description
    if phone is not None:
        data["phone"] = phone
    if email is not None:
        data["email"] = email
    if address is not None:
        data["address"] = address

    result = await make_request(
        method="PUT",
        endpoint="/shop/settings",
        token=token,
        json_data=data,
    )
    return result


# ===== Main Entry Point =====

# Note: When using `fastmcp run server.py --transport streamable-http`,
# the mcp object is auto-discovered and run by fastmcp CLI.
# No need for manual mcp.run() call.

if __name__ == "__main__":
    # For stdio mode (e.g., Claude Code CLI integration)
    mcp.run()
