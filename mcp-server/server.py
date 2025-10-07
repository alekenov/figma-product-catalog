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
    delivery_date: str,
    delivery_time: str,
    shop_id: int,
    items: List[Dict[str, Any]],
    total_price: int,
    delivery_type: str = "delivery",
    delivery_address: Optional[str] = None,
    pickup_address: Optional[str] = None,
    notes: Optional[str] = None,
    telegram_user_id: Optional[str] = None,
    recipient_name: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    sender_phone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new order (public endpoint for Telegram bot).

    Args:
        customer_name: Customer full name (person ordering/paying)
        customer_phone: Customer phone number (person ordering/paying)
        delivery_date: Delivery date. Supports natural language: "сегодня", "завтра", "послезавтра", "через N дней" or date format YYYY-MM-DD
        delivery_time: Delivery time. Supports natural language: "утром" (10:00), "днем" (14:00), "вечером" (18:00), "как можно скорее" (nearest available) or time format HH:MM
        shop_id: Shop ID
        items: List of order items [{"product_id": int, "quantity": int}]
        total_price: Total order price in tiyins (1 tenge = 100 tiyins)
        delivery_type: "delivery" for home delivery or "pickup" for customer pickup (default: "delivery")
        delivery_address: Delivery address (required only if delivery_type="delivery")
        pickup_address: Pickup location address (optional, auto-fetched from shop settings if not provided for pickup orders)
        notes: Additional notes
        telegram_user_id: Telegram user ID for bot orders
        recipient_name: Recipient name (person receiving flowers). If not specified, same as customer_name. Not used for pickup orders.
        recipient_phone: Recipient phone (person receiving flowers). If not specified, same as customer_phone. Not used for pickup orders.
        sender_phone: Sender phone (duplicate of customer_phone for clarity)

    Returns:
        Created order with tracking information

    Example (Delivery):
        create_order(
            customer_name="Иван Иванов",
            customer_phone="77011234567",
            delivery_type="delivery",
            delivery_address="ул. Абая 1",
            delivery_date="завтра",
            delivery_time="днем",
            shop_id=1,
            items=[{"product_id": 1, "quantity": 2}],
            total_price=1000000,
            telegram_user_id="626599",
            recipient_name="Мария Петрова",
            recipient_phone="77022223333"
        )

    Example (Pickup):
        create_order(
            customer_name="Иван Иванов",
            customer_phone="77011234567",
            delivery_type="pickup",
            delivery_date="сегодня",
            delivery_time="18:00",
            shop_id=1,
            items=[{"product_id": 1, "quantity": 1}],
            total_price=500000,
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

    # === DELIVERY TYPE VALIDATION ===
    if delivery_type == "pickup":
        print(f"🏪 Pickup order - skipping delivery validation")

        # For pickup, use provided pickup_address or get from shop settings
        if not pickup_address:
            try:
                shop_settings = await get_shop_settings(shop_id=shop_id)
                pickup_address = shop_settings.get("pickup_address") or shop_settings.get("address")
                print(f"📍 Fetched pickup address from shop settings: {pickup_address}")
            except Exception as e:
                print(f"⚠️ Could not fetch shop pickup address: {e}")
                pickup_address = "Адрес магазина (уточните у менеджера)"

        final_address = pickup_address

    elif delivery_type == "delivery":
        if not delivery_address:
            return {
                "error": "missing_delivery_address",
                "message": "Для доставки необходимо указать адрес доставки"
            }

        final_address = delivery_address

        # === DELIVERY VALIDATION ===
        # Extract product IDs for feasibility check
        product_ids_str = ",".join(str(item["product_id"]) for item in items)

        # Check if requested delivery time is feasible
        try:
            feasibility = await check_delivery_feasibility(
                shop_id=shop_id,
                delivery_date=parsed_date.strftime('%Y-%m-%d'),
                product_ids=product_ids_str
            )

            if not feasibility.get("is_feasible", False):
                # Delivery at requested time is impossible
                earliest = feasibility.get("earliest_delivery", "")
                reason = feasibility.get("reason", "Доставка в указанное время невозможна")

                print(f"❌ Delivery validation failed: {reason}")
                print(f"✅ Earliest possible: {earliest}")

                # Return error with suggestion
                return {
                    "error": "delivery_time_impossible",
                    "message": f"{reason}. Ближайшее доступное время: {earliest}",
                    "requested_time": delivery_datetime,
                    "earliest_available": earliest,
                    "suggestion": "Пожалуйста, выберите другое время или используйте предложенное."
                }

            print(f"✅ Delivery validation passed for {delivery_datetime}")

        except Exception as e:
            # Log validation error but don't block order (backward compatibility)
            print(f"⚠️ Delivery validation error (non-blocking): {e}")

    else:
        return {
            "error": "invalid_delivery_type",
            "message": f"Неверный тип доставки: {delivery_type}. Допустимые значения: 'delivery' или 'pickup'"
        }

    # Ensure phone numbers are strings (AI may pass integers)
    customer_phone = str(customer_phone) if customer_phone else customer_phone
    if recipient_phone is not None:
        recipient_phone = str(recipient_phone)
    if sender_phone is not None:
        sender_phone = str(sender_phone)

    # Format data to match backend OrderCreateWithItems schema
    data = {
        "customerName": customer_name,
        "phone": customer_phone,
        "delivery_address": final_address,  # Use final_address (either delivery or pickup address)
        "delivery_date": delivery_datetime,
        "scheduled_time": parsed_time,  # Send parsed time (HH:MM format) instead of natural language
        "items": items,
        "notes": notes or "",
        "telegram_user_id": telegram_user_id,
        "check_availability": False,  # Skip availability check for AI orders
        # Backend calculates subtotal/total from items
        # Phase 3: Recipient fields (person receiving flowers)
        "recipient_name": recipient_name,
        "recipient_phone": recipient_phone,
        "sender_phone": sender_phone or customer_phone,
        # Pickup support
        "delivery_type": delivery_type,
        "pickup_address": pickup_address if delivery_type == "pickup" else None,
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
    from datetime import datetime, timedelta

    # Build update data with only provided fields
    data = {}
    if delivery_address is not None:
        data["delivery_address"] = delivery_address

    # Parse natural language date if provided
    if delivery_date is not None:
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

        # Format as ISO datetime (backend expects datetime, not date)
        delivery_datetime = f"{parsed_date.strftime('%Y-%m-%d')}T00:00:00"
        data["delivery_date"] = delivery_datetime
        print(f"📅 Parsed natural language date: '{delivery_date}' → {delivery_datetime}")

    # Parse natural language time if provided
    if delivery_time is not None:
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

        data["scheduled_time"] = parsed_time
        print(f"⏰ Parsed natural language time: '{delivery_time}' → {parsed_time}")

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
        endpoint=f"/orders/by-tracking/{tracking_id}/status",
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


# ===== PHASE 1: Enhanced Product Discovery Tools =====

@mcp.tool()
async def check_product_availability(
    product_id: int,
    quantity: int = 1,
    shop_id: int = DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """
    Check if a product is available in the requested quantity.

    This tool checks real-time warehouse inventory to determine if
    the product can be fulfilled. It considers product recipes and
    required warehouse items.

    Args:
        product_id: Product ID to check
        quantity: Requested quantity (default: 1)
        shop_id: Shop ID for multi-tenancy (default: from env)

    Returns:
        {
            "available": true/false,
            "product_id": 123,
            "quantity_requested": 5,
            "quantity_available": 10,
            "can_fulfill": true,
            "missing_items": []  # List of missing warehouse items if can't fulfill
        }

    Example:
        check_product_availability(product_id=123, quantity=5, shop_id=8)
    """
    result = await make_request(
        method="GET",
        endpoint=f"/products/{product_id}/availability",
        params={"quantity": quantity}
    )
    return result


@mcp.tool()
async def preview_order_cost(
    shop_id: int,
    items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate total order cost before placing the order.

    This tool calculates subtotal, delivery cost, and total without
    creating an actual order. Useful for showing customers the final
    price before they commit.

    Args:
        shop_id: Shop ID for delivery settings
        items: List of order items, each with:
            - product_id: int
            - quantity: int
            Example: [{"product_id": 123, "quantity": 2}]

    Returns:
        {
            "subtotal": 15000,  # Products total
            "delivery_cost": 1000,  # Delivery fee
            "free_delivery_threshold": 20000,  # Free delivery if order exceeds this
            "free_delivery_applied": false,
            "total": 16000,  # Final amount
            "available": true  # Can fulfill all items
        }

    Example:
        preview_order_cost(
            shop_id=8,
            items=[{"product_id": 123, "quantity": 2}]
        )
    """
    result = await make_request(
        method="POST",
        endpoint="/orders/public/preview",
        params={"shop_id": shop_id},
        json_data={"items": items}
    )
    return result


@mcp.tool()
async def get_bestsellers(
    shop_id: int = DEFAULT_SHOP_ID,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get bestselling products sorted by order count.

    Returns most popular products based on actual order history.
    Great for recommending proven hits to customers.

    Args:
        shop_id: Shop ID (default: from env)
        limit: Maximum number of products (default: 10)

    Returns:
        List of products with full details (name, price, description, image, etc.)
        Sorted by popularity (most ordered first)

    Example:
        get_bestsellers(shop_id=8, limit=5)
    """
    result = await make_request(
        method="GET",
        endpoint="/products/public/bestsellers",
        params={"limit": limit}
    )
    return result


@mcp.tool()
async def get_featured_products(
    shop_id: int = DEFAULT_SHOP_ID,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get featured/curated products recommended by the shop.

    Returns products marked as featured (is_featured=True).
    These are hand-picked recommendations by shop owners.

    Args:
        shop_id: Shop ID (default: from env)
        limit: Maximum number of products (default: 10)

    Returns:
        List of featured products with full details

    Example:
        get_featured_products(shop_id=8, limit=5)
    """
    result = await make_request(
        method="GET",
        endpoint="/products/public/featured",
        params={"skip": 0, "limit": limit}
    )
    return result


@mcp.tool()
async def get_faq(
    shop_id: int = DEFAULT_SHOP_ID,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get Frequently Asked Questions for the shop.

    Returns common questions and answers. Useful for handling
    customer inquiries without escalation.

    Args:
        shop_id: Shop ID (default: from env)
        category: Optional category filter (e.g., "delivery", "payment")

    Returns:
        List of FAQs with question, answer, and category:
        [
            {
                "id": 1,
                "question": "Do you deliver on weekends?",
                "answer": "Yes, we deliver 7 days a week",
                "category": "delivery",
                "enabled": true
            }
        ]

    Example:
        get_faq(shop_id=8, category="delivery")
    """
    params = {}
    if category:
        params["category"] = category

    result = await make_request(
        method="GET",
        endpoint="/content/faqs",
        params=params
    )
    return result


@mcp.tool()
async def get_reviews(
    shop_id: int = DEFAULT_SHOP_ID,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get company reviews with ratings and statistics.

    Returns customer reviews with aggregate stats (average rating,
    total count, rating breakdown). Great for building trust.

    Args:
        shop_id: Shop ID (default: from env)
        limit: Maximum number of reviews (default: 10)

    Returns:
        {
            "reviews": [
                {
                    "id": 1,
                    "author_name": "Айгуль",
                    "rating": 5,
                    "comment": "Отличный сервис!",
                    "created_at": "2025-01-15T10:00:00"
                }
            ],
            "stats": {
                "total_count": 127,
                "average_rating": 4.8,
                "rating_breakdown": {
                    "5": 100,
                    "4": 20,
                    "3": 5,
                    "2": 1,
                    "1": 1
                }
            }
        }

    Example:
        get_reviews(shop_id=8, limit=5)
    """
    result = await make_request(
        method="GET",
        endpoint="/reviews/company",
        params={"limit": limit, "offset": 0}
    )
    return result


# ===== Phase 2: Client Profile & Smart Search =====

@mcp.tool()
async def get_client_profile(
    telegram_user_id: str,
    shop_id: int = DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """
    Get client profile with order history and saved addresses.
    Use for repeat customers to auto-fill addresses and suggest reorders.

    Example:
        profile = await get_client_profile("123456789", shop_id=8)
        # Returns: {client, statistics, recent_orders, saved_addresses}
    """
    result = await make_request(
        method="GET",
        endpoint=f"/clients/telegram/{telegram_user_id}/profile",
        params={"shop_id": shop_id}
    )
    return result


@mcp.tool()
async def search_products_smart(
    shop_id: int = DEFAULT_SHOP_ID,
    query: Optional[str] = None,
    budget: Optional[int] = None,
    occasion: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Smart product search with budget and occasion filtering.

    Args:
        query: Search text (e.g., "розы", "тюльпаны")
        budget: Max price in tenge (e.g., 15000)
        occasion: "birthday", "wedding", "funeral", "romantic", etc.

    Example:
        products = await search_products_smart(
            query="розы", budget=15000, occasion="birthday"
        )
    """
    result = await make_request(
        method="GET",
        endpoint="/products/public/smart-search",
        params={
            "shop_id": shop_id,
            "query": query,
            "budget": budget,
            "occasion": occasion,
            "limit": limit
        }
    )
    return result


@mcp.tool()
async def save_client_address(
    telegram_user_id: str,
    name: str,
    address: str,
    phone: str,
    shop_id: int = DEFAULT_SHOP_ID,
    is_default: bool = False
) -> Dict[str, Any]:
    """
    Save client address for future orders.

    Args:
        name: Address nickname (e.g., "Мадине", "Домой", "Офис")
        address: Full delivery address
        phone: Recipient phone
        is_default: Set as default address

    Example:
        result = await save_client_address(
            telegram_user_id="123",
            name="Мадине",
            address="ул. Абая 10",
            phone="+77771234567"
        )
    """
    result = await make_request(
        method="POST",
        endpoint=f"/clients/telegram/{telegram_user_id}/addresses",
        params={"shop_id": shop_id},
        json_data={
            "name": name,
            "address": address,
            "phone": phone,
            "is_default": is_default
        }
    )
    return result


@mcp.tool()
async def cancel_order(
    order_id: int,
    reason: str,
    shop_id: int = DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """
    Cancel an order. Only NEW/PENDING orders can be cancelled.

    Args:
        order_id: Order ID to cancel
        reason: "changed_mind", "wrong_product", "delivery_time", "duplicate", "other"

    Example:
        result = await cancel_order(order_id=12345, reason="changed_mind")
    """
    result = await make_request(
        method="POST",
        endpoint=f"/orders/{order_id}/cancel",
        params={"shop_id": shop_id, "reason": reason}
    )
    return result


# ============================================================================
# PHASE 3: DELIVERY LOGISTICS TOOLS (3 tools)
# ============================================================================

@mcp.tool()
async def get_delivery_slots(
    shop_id: int = DEFAULT_SHOP_ID,
    date: str = "",
    product_ids: Optional[str] = None
) -> Dict[str, Any]:
    """
    📅 SHOW CUSTOMER available delivery windows - builds trust & transparency!

    Returns 2-hour delivery slots (9:00-11:00, 11:00-13:00, etc.) showing which times are free.
    Use this BEFORE confirming order to let customer choose preferred time.

    Better UX flow:
    1. Customer: "Хочу доставку сегодня"
    2. You: Call this to show available slots
    3. Customer chooses from: "14:00-16:00 ✅" or "16:00-18:00 ✅"
    4. You: Create order with chosen time

    Accounts for:
    - Shop working hours (9:00 - 21:00)
    - Bouquet preparation time (30 min base + 10 min/product)
    - Delivery travel time (60 min)
    - Current time (no past slots)

    Args:
        shop_id: Shop ID (default: 8)
        date: Delivery date in YYYY-MM-DD format (e.g., "2025-01-15")
        product_ids: Comma-separated product IDs (e.g., "1,5,10")

    Returns:
        List of slots: [{"start_time": "14:00", "end_time": "16:00", "available": true}, ...]

    Example - Show customer today's options:
        slots = await get_delivery_slots(shop_id=8, date="2025-01-15", product_ids="1,5")
        # Agent: "Свободны слоты: 14:00-16:00, 16:00-18:00, 18:00-20:00"
    """
    result = await make_request(
        method="GET",
        endpoint="/delivery/slots",
        params={"shop_id": shop_id, "date": date, "product_ids": product_ids}
    )
    return result


@mcp.tool()
async def validate_delivery_time(
    shop_id: int = DEFAULT_SHOP_ID,
    delivery_time: str = "",
    product_ids: Optional[str] = None
) -> Dict[str, Any]:
    """
    ✅ Validate customer's EXACT requested delivery time before confirming.

    Customer says: "Доставьте к 18:00"
    You: Call this to verify 18:00 is actually possible (not too early/late/past).

    Checks 3 critical constraints:
    1. Not in the past (considering prep time)
    2. Within shop hours (9:00 - 21:00)
    3. Enough time for prep + delivery

    Returns alternatives if requested time impossible.

    Use when:
    - Customer specifies EXACT time ("к 15:00", "at 3pm")
    - Before confirming order with specific time
    - To avoid promising impossible delivery

    Args:
        shop_id: Shop ID (default: 8)
        delivery_time: Exact requested time in ISO format (e.g., "2025-01-15T14:00:00")
        product_ids: Comma-separated product IDs (e.g., "1,5,10")

    Returns:
        {
            "is_valid": bool,  # Can we deliver at this exact time?
            "delivery_time": str,  # The requested time
            "reason": str,  # Why not valid (if false)
            "alternative_slots": [...]  # Suggested alternatives (if false)
        }

    Example - Customer wants 18:00:
        result = await validate_delivery_time(
            shop_id=8,
            delivery_time="2025-01-15T18:00:00",
            product_ids="1,5"
        )
        # Response: {"is_valid": true} → Confirm order
        # Or: {"is_valid": false, "reason": "Too early", "alternative_slots": [...]}
    """
    result = await make_request(
        method="POST",
        endpoint="/delivery/validate",
        params={
            "shop_id": shop_id,
            "delivery_time": delivery_time,
            "product_ids": product_ids
        }
    )
    return result


@mcp.tool()
async def check_delivery_feasibility(
    shop_id: int = DEFAULT_SHOP_ID,
    delivery_date: str = "",
    product_ids: Optional[str] = None
) -> Dict[str, Any]:
    """
    🚨 USE THIS FIRST when customer asks for URGENT or ASAP delivery!

    Checks if delivery is feasible on requested date considering:
    - Current time (can't deliver in the past)
    - Shop working hours (closed times)
    - Bouquet preparation time (30 min base + 10 min per product)

    ⚡ Perfect for "как можно скорее", "срочно", "сегодня ASAP" requests.
    Returns earliest possible delivery time to show customer realistic options.

    Args:
        shop_id: Shop ID (default: 8)
        delivery_date: Desired delivery date in YYYY-MM-DD format (e.g., "2025-01-15")
        product_ids: Comma-separated product IDs (e.g., "1,5,10")

    Returns:
        {
            "is_feasible": bool,  # Can we deliver on this date?
            "earliest_delivery": str,  # ISO datetime of earliest possible time
            "reason": str  # Explanation if not feasible
        }

    Example - Customer wants ASAP delivery:
        result = await check_delivery_feasibility(
            shop_id=8,
            delivery_date="2025-01-15",
            product_ids="1,5"
        )
        # Response: {"is_feasible": true, "earliest_delivery": "2025-01-15T14:30:00"}
    """
    result = await make_request(
        method="GET",
        endpoint="/delivery/feasibility",
        params={
            "shop_id": shop_id,
            "delivery_date": delivery_date,
            "product_ids": product_ids
        }
    )
    return result


# ===== Main Entry Point =====

# Note: When using `fastmcp run server.py --transport streamable-http`,
# the mcp object is auto-discovered and run by fastmcp CLI.
# No need for manual mcp.run() call.

if __name__ == "__main__":
    # For stdio mode (e.g., Claude Code CLI integration)
    mcp.run()
