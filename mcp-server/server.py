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
        product_type: Filter by type. Valid values: "flowers", "sweets", "fruits", "gifts". Leave empty for all types.
        enabled_only: Show only enabled products
        min_price: Minimum price in tenge
        max_price: Maximum price in tenge
        skip: Number of products to skip (pagination)
        limit: Number of products to return (max 100)

    Returns:
        List of products with details

    Example:
        list_products(shop_id=8, search="роза", product_type="flowers", min_price=10000, max_price=20000, limit=10)
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
        endpoint="/products/",
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
        endpoint="/products/",
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
        endpoint=f"/products/{product_id}",
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
    telegram_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new order (public endpoint for Telegram bot).

    Args:
        customer_name: Customer full name
        customer_phone: Customer phone number
        delivery_address: Delivery address
        delivery_date: Delivery date. Supports natural language: "сегодня", "завтра", "послезавтра", "через N дней" or date format YYYY-MM-DD
        delivery_time: Delivery time. Supports natural language: "утром" (10:00), "днем" (14:00), "вечером" (18:00), "как можно скорее" (nearest available) or time format HH:MM
        shop_id: Shop ID
        items: List of order items [{"product_id": int, "quantity": int}]
        total_price: Total order price in tiyins (1 tenge = 100 tiyins)
        notes: Additional notes
        telegram_user_id: Telegram user ID for bot orders

    Returns:
        Created order with tracking information

    Example:
        create_order(
            customer_name="Иван Иванов",
            customer_phone="77011234567",
            delivery_address="ул. Абая 1",
            delivery_date="завтра",
            delivery_time="днем",
            shop_id=1,
            items=[{"product_id": 1, "quantity": 2}],
            total_price=1000000,
            telegram_user_id="626599"
        )
    """
    from datetime import datetime, timedelta

    # Parse natural language date
    today = datetime.now().date()
    if delivery_date.lower() in ["сегодня", "today"]:
        parsed_date = today
    elif delivery_date.lower() in ["завтра", "tomorrow"]:
        parsed_date = today + timedelta(days=1)
    elif delivery_date.lower() in ["послезавтра", "day after tomorrow"]:
        parsed_date = today + timedelta(days=2)
    elif delivery_date.lower().startswith("через "):
        # Parse "через 2 дня", "через 3 дня"
        try:
            days = int(delivery_date.split()[1])
            parsed_date = today + timedelta(days=days)
        except:
            parsed_date = today
    else:
        # Assume YYYY-MM-DD format
        try:
            parsed_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
        except:
            parsed_date = today

    # Parse natural language time
    if delivery_time.lower() in ["утром", "утро", "morning"]:
        parsed_time = "10:00"
    elif delivery_time.lower() in ["днем", "день", "afternoon"]:
        parsed_time = "14:00"
    elif delivery_time.lower() in ["вечером", "вечер", "evening"]:
        parsed_time = "18:00"
    elif delivery_time.lower() in ["как можно скорее", "asap", "скорее", "срочно"]:
        current_hour = datetime.now().hour
        if current_hour < 12:
            parsed_time = "12:00"
        elif current_hour < 16:
            parsed_time = "16:00"
        else:
            parsed_time = "18:00"
    else:
        # Assume HH:MM format
        parsed_time = delivery_time

    # Combine date and time into ISO datetime for backend
    delivery_datetime = f"{parsed_date.strftime('%Y-%m-%d')}T{parsed_time}:00"

    # Debug: Log the parsed datetime
    print(f"📅 Parsed natural language: '{delivery_date}' '{delivery_time}' → {delivery_datetime}")

    # Format data to match backend OrderCreateWithItems schema
    data = {
        "customerName": customer_name,
        "phone": customer_phone,
        "delivery_address": delivery_address,
        "delivery_date": delivery_datetime,
        "scheduled_time": parsed_time,  # Send parsed time (HH:MM format) instead of natural language
        "items": items,
        "notes": notes or "",
        "telegram_user_id": telegram_user_id,
        "check_availability": False,  # Skip availability check for AI orders
        # Backend calculates subtotal/total from items
    }

    # Use public endpoint with shop_id as query parameter
    result = await make_request(
        method="POST",
        endpoint="/orders/public/create",
        params={"shop_id": shop_id},
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
async def update_order(
    tracking_id: str,
    delivery_address: Optional[str] = None,
    delivery_date: Optional[str] = None,
    delivery_time: Optional[str] = None,
    delivery_notes: Optional[str] = None,
    notes: Optional[str] = None,
    recipient_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update order details by tracking ID (customer-facing).
    Allows customers to modify delivery address, time, recipient, and add notes.

    Args:
        tracking_id: Order tracking ID from order creation
        delivery_address: New delivery address
        delivery_date: New delivery date (supports "сегодня", "завтра", "послезавтра", "через N дней" or YYYY-MM-DD)
        delivery_time: New delivery time (supports "утром" (10:00), "днем" (14:00), "вечером" (18:00), "как можно скорее" or HH:MM)
        delivery_notes: Additional delivery instructions (e.g., "Домофон не работает, позвоните заранее")
        notes: Order notes or special requests
        recipient_name: Recipient name if different from customer

    Returns:
        Updated order with full details

    Example:
        update_order(
            tracking_id="903757396",
            delivery_address="улица Сатпаева, дом 90А, квартира 5",
            delivery_notes="Домофон не работает, позвоните заранее"
        )
    """
    # Build update data with only provided fields
    data = {}
    if delivery_address is not None:
        data["delivery_address"] = delivery_address
    if delivery_date is not None:
        data["delivery_date"] = delivery_date
    if delivery_time is not None:
        data["scheduled_time"] = delivery_time
    if delivery_notes is not None:
        data["delivery_notes"] = delivery_notes
    if notes is not None:
        data["notes"] = notes
    if recipient_name is not None:
        data["recipient_name"] = recipient_name

    # Use public endpoint with tracking ID
    result = await make_request(
        method="PUT",
        endpoint=f"/orders/by-tracking/{tracking_id}",
        params={"changed_by": "customer"},
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


@mcp.tool()
async def track_order_by_phone(
    customer_phone: str,
    shop_id: int
) -> str:
    """
    Track orders by customer phone number.

    Note: This requires authentication. For public tracking, ask customer for their tracking ID
    and use track_order() instead.

    Args:
        customer_phone: Customer phone number to search for
        shop_id: Shop ID

    Returns:
        Error message directing to use tracking ID instead
    """
    return (
        "Для отслеживания заказов, пожалуйста, используйте ваш ID отслеживания (tracking ID), "
        "который вы получили при создании заказа. Отслеживание по номеру телефона требует авторизации."
    )


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
        "operation_type": "delivery",  # WarehouseOperationType.DELIVERY
        "quantity_change": quantity,
        "description": notes or "Поставка через MCP",
    }

    result = await make_request(
        method="POST",
        endpoint=f"/warehouse/{warehouse_item_id}/delivery",
        token=token,
        json_data=data,
    )
    return result


# ===== Shop Tools =====

@mcp.tool()
async def get_shop_settings(shop_id: int) -> Dict[str, Any]:
    """
    Get public shop settings and configuration.

    Args:
        shop_id: Shop ID

    Returns:
        Shop settings including name, description, contact info, working hours
    """
    result = await make_request(
        method="GET",
        endpoint="/shop/settings/public",
        params={"shop_id": shop_id}
    )
    return result


@mcp.tool()
async def get_working_hours(shop_id: int) -> Dict[str, Any]:
    """
    Get shop working hours schedule.

    Args:
        shop_id: Shop ID

    Returns:
        Working hours for weekdays and weekends
    """
    # Get full shop settings which include working hours
    shop = await make_request(
        method="GET",
        endpoint="/shop/settings/public",
        params={"shop_id": shop_id}
    )

    # Extract working hours information
    return {
        "weekday_start": shop.get("weekday_start"),
        "weekday_end": shop.get("weekday_end"),
        "weekday_closed": shop.get("weekday_closed", False),
        "weekend_start": shop.get("weekend_start"),
        "weekend_end": shop.get("weekend_end"),
        "weekend_closed": shop.get("weekend_closed", False),
    }


# ===== Telegram Client Tools =====

@mcp.tool()
async def get_telegram_client(telegram_user_id: str, shop_id: int) -> Optional[Dict[str, Any]]:
    """
    Get telegram client by telegram_user_id and shop_id.
    Used to check if telegram user is already registered.

    Args:
        telegram_user_id: Telegram user ID (as string)
        shop_id: Shop ID

    Returns:
        Client data if found, None if not found

    Example:
        get_telegram_client(telegram_user_id="123456789", shop_id=8)
    """
    result = await make_request(
        method="GET",
        endpoint="/telegram/client",
        params={
            "telegram_user_id": telegram_user_id,
            "shop_id": shop_id
        }
    )
    return result


@mcp.tool()
async def register_telegram_client(
    telegram_user_id: str,
    phone: str,
    customer_name: str,
    shop_id: int,
    telegram_username: Optional[str] = None,
    telegram_first_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Register or update a telegram client with contact information.
    Links Telegram user ID with phone number for bot authorization.

    Args:
        telegram_user_id: Telegram user ID (as string)
        phone: Phone number from Telegram contact
        customer_name: Customer name
        shop_id: Shop ID
        telegram_username: Telegram @username (optional)
        telegram_first_name: Telegram first name (optional)

    Returns:
        Created or updated client data

    Example:
        register_telegram_client(
            telegram_user_id="123456789",
            phone="+77015211545",
            customer_name="John Doe",
            shop_id=8,
            telegram_username="johndoe",
            telegram_first_name="John"
        )
    """
    result = await make_request(
        method="POST",
        endpoint="/telegram/client/register",
        json_data={
            "telegram_user_id": telegram_user_id,
            "phone": phone,
            "customer_name": customer_name,
            "shop_id": shop_id,
            "telegram_username": telegram_username,
            "telegram_first_name": telegram_first_name
        }
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
