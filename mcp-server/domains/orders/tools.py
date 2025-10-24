"""
Order management tools for MCP server.
Uses backend API for delivery parsing (centralized logic).
"""
from typing import List, Dict, Any, Optional
from core.api_client import api_client
from core.registry import ToolRegistry
from core.config import Config
from core.utils import merge_required_optional, drop_none
from .delivery import DeliveryValidator, format_delivery_error
import logging

logger = logging.getLogger(__name__)

# Initialize validator
validator = DeliveryValidator(api_client)


async def parse_delivery_datetime(date_str: str, time_str: str) -> Dict[str, Any]:
    """
    Parse natural language delivery date/time using backend API.

    Args:
        date_str: Natural language date (e.g., "завтра", "сегодня", "2025-01-15")
        time_str: Natural language time (e.g., "утром", "днем", "18:00")

    Returns:
        Parsed delivery data with iso_datetime, date, time fields

    Example:
        >>> await parse_delivery_datetime("завтра", "днем")
        {"iso_datetime": "2025-01-16T14:00:00", "date": "2025-01-16", "time": "14:00"}
    """
    try:
        result = await api_client.post(
            endpoint="/delivery/parse",
            json_data={
                "date_str": date_str,
                "time_str": time_str
            }
        )
        logger.debug(f"📅 Backend parsed '{date_str}' '{time_str}' → {result['iso_datetime']}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to parse delivery datetime via API: {e}")
        # Fallback: return a reasonable default (today at 14:00)
        from datetime import datetime
        fallback_dt = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        return {
            "iso_datetime": fallback_dt.isoformat(),
            "date": fallback_dt.strftime('%Y-%m-%d'),
            "time": "14:00",
            "original_date": date_str,
            "original_time": time_str
        }


# Order Management Tools

@ToolRegistry.register(domain="orders", requires_auth=True)
async def list_orders(
    token: str,
    status: Optional[str] = None,
    customer_phone: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get list of orders with filtering (admin only)."""
    params = merge_required_optional(
        {"skip": skip, "limit": limit},
        {
            "status": status,
            "customer_phone": customer_phone,
            "search": search,
        },
    )

    return await api_client.get("/orders", token=token, params=params)


@ToolRegistry.register(domain="orders", requires_auth=True)
async def get_order(token: str, order_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific order (admin only)."""
    return await api_client.get(f"/orders/{order_id}", token=token)


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
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
    Uses backend API for natural language date/time parsing.
    """
    # Parse natural language delivery date/time via backend API
    parsed = await parse_delivery_datetime(delivery_date, delivery_time)

    # Delivery type validation
    if delivery_type == "pickup":
        logger.info("🏪 Pickup order - skipping delivery validation")
        if not pickup_address:
            shop_settings = await api_client.get(
                "/shop/settings/public",
                params={"shop_id": shop_id}
            )
            pickup_address = shop_settings.get("pickup_address") or shop_settings.get("address")
        final_address = pickup_address

    elif delivery_type == "delivery":
        if not delivery_address:
            return {
                "error": "missing_delivery_address",
                "message": "Для доставки необходимо указать адрес доставки"
            }
        final_address = delivery_address

        # Validate delivery feasibility
        product_ids_str = ",".join(str(item["product_id"]) for item in items)
        try:
            feasibility = await validator.validate_feasibility(
                shop_id=shop_id,
                delivery_datetime=parsed["iso_datetime"],
                product_ids=product_ids_str
            )

            if not feasibility.get("feasible", False):
                logger.error(f"❌ Delivery validation failed: {feasibility.get('reason')}")
                return format_delivery_error(feasibility, parsed["iso_datetime"])

            logger.info(f"✅ Delivery validation passed for {parsed['iso_datetime']}")

        except Exception as e:
            logger.warning(f"⚠️ Delivery validation error (non-blocking): {e}")

    else:
        return {
            "error": "invalid_delivery_type",
            "message": f"Неверный тип доставки: {delivery_type}"
        }

    # Format data for backend
    data = drop_none({
        "customerName": customer_name,
        "phone": str(customer_phone),
        "delivery_address": final_address,
        "delivery_date": parsed["iso_datetime"],
        "scheduled_time": parsed["time"],
        "items": items,
        "notes": notes or "",
        "telegram_user_id": telegram_user_id,
        "check_availability": False,
        "recipient_name": recipient_name,
        "recipient_phone": str(recipient_phone) if recipient_phone else None,
        "sender_phone": sender_phone or str(customer_phone),
        "delivery_type": delivery_type,
        "pickup_address": pickup_address if delivery_type == "pickup" else None,
    })

    return await api_client.post(
        "/orders/public/create",
        json_data=data,
        params={"shop_id": shop_id}
    )


@ToolRegistry.register(domain="orders", requires_auth=True)
async def update_order_status(
    token: str,
    order_id: int,
    status: str,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Update order status (admin only)."""
    data = drop_none({"status": status, "notes": notes})
    return await api_client.patch(
        f"/orders/{order_id}/status",
        json_data=data,
        token=token
    )


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
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
    Uses backend API for natural language parsing.
    """
    data = {}

    if delivery_address is not None:
        data["delivery_address"] = delivery_address

    # Parse natural language date/time if provided
    if delivery_date is not None or delivery_time is not None:
        # If only one is provided, use current date/time for the other
        date_str = delivery_date if delivery_date is not None else "сегодня"
        time_str = delivery_time if delivery_time is not None else "днем"

        parsed = await parse_delivery_datetime(date_str, time_str)

        if delivery_date is not None:
            data["delivery_date"] = parsed["iso_datetime"]
            logger.debug(f"📅 Parsed date: '{delivery_date}' → {data['delivery_date']}")

        if delivery_time is not None:
            data["scheduled_time"] = parsed["time"]
            logger.debug(f"⏰ Parsed time: '{delivery_time}' → {parsed['time']}")

    if delivery_notes is not None:
        data["delivery_notes"] = delivery_notes
    if notes is not None:
        data["notes"] = notes
    if recipient_name is not None:
        data["recipient_name"] = recipient_name

    return await api_client.put(
        f"/orders/by-tracking/{tracking_id}",
        json_data=drop_none(data),
        params={"changed_by": "customer"}
    )


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
async def track_order(tracking_id: str) -> Dict[str, Any]:
    """Track order status by tracking ID (public endpoint)."""
    return await api_client.get(f"/orders/by-tracking/{tracking_id}/status")


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
async def track_order_by_phone(customer_phone: str, shop_id: int) -> str:
    """
    Track orders by customer phone number.
    Note: Directs users to use tracking ID instead.
    """
    return (
        "Для отслеживания заказов, пожалуйста, используйте ваш ID отслеживания (tracking ID), "
        "который вы получили при создании заказа."
    )


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
async def preview_order_cost(
    shop_id: int,
    items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate total order cost before placing the order."""
    return await api_client.post(
        "/orders/public/preview",
        json_data=items,  # Send list directly, not wrapped in object
        params={"shop_id": shop_id}
    )


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
async def cancel_order(
    order_id: int,
    reason: str,
    shop_id: int = Config.DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """Cancel an order. Only NEW/PENDING orders can be cancelled."""
    return await api_client.post(
        f"/orders/{order_id}/cancel",
        params={"shop_id": shop_id, "reason": reason}
    )


@ToolRegistry.register(domain="orders", requires_auth=False, is_public=True)
async def sync_order_to_production(
    order_data: Optional[Dict[str, Any]] = None,
    tracking_id: Optional[str] = None,
    shop_id: int = Config.DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """
    Sync Railway order to Production Bitrix system.
    Accepts full order data directly or fetches by tracking_id.

    Args:
        order_data: Full order object (if available, skips fetch)
        tracking_id: Railway order tracking ID (used if order_data not provided)
        shop_id: Shop ID (default: 8)

    Returns:
        Production API response with order_id, account_number, xml_id

    Example:
        >>> # Option 1: Pass order data directly (fastest, for telegram bot)
        >>> await sync_order_to_production(order_data=created_order, shop_id=8)

        >>> # Option 2: Fetch by tracking_id (fallback)
        >>> await sync_order_to_production(tracking_id="123456789", shop_id=8)
    """
    import httpx

    # 1. Get order data (either passed directly or fetch by tracking_id)
    if order_data:
        order = order_data
        logger.info(f"🔄 Syncing order (order_id={order.get('id')}) to Production Bitrix...")
    elif tracking_id:
        logger.info(f"🔄 Syncing order tracking_id={tracking_id} to Production Bitrix...")
        logger.warning("⚠️ Fetching by tracking_id not fully supported yet - use order_data parameter instead")
        return {
            "status": False,
            "error": "tracking_fetch_not_implemented",
            "message": "Please pass full order_data directly. Fetching by tracking_id requires admin endpoint."
        }
    else:
        logger.error("❌ Must provide either order_data or tracking_id")
        return {
            "status": False,
            "error": "missing_parameters",
            "message": "Must provide either order_data or tracking_id parameter"
        }

    # 2. Build Production API payload
    delivery_type = order.get("delivery_type", "delivery")
    is_pickup = delivery_type == "pickup"

    # Build items list and calculate total if not provided
    items_list = []
    total_calculated = 0
    for item in order.get("items", []):
        # Railway backend returns 'product_price', fallback to 'price' or nested product.price
        item_price = item.get("product_price", item.get("price", item.get("product", {}).get("price", 0)))
        item_qty = item.get("quantity", 1)
        items_list.append({
            "product_id": item.get("product_id"),
            "quantity": item_qty,
            "price": item_price,
            "name": item.get("product_name", item.get("name", item.get("product", {}).get("name", "")))
        })
        total_calculated += item_price * item_qty

    # Use order total_price if available, otherwise use calculated total
    total_price = order.get("total_price") or total_calculated or 0

    payload = {
        "railway_order_id": str(order.get("id")),
        "customer_phone": order.get("phone"),
        "pickup": "Y" if is_pickup else "N",
        "items": items_list,
        "total_price": total_price
    }

    # Add delivery-specific fields
    if not is_pickup:
        payload["recipient_name"] = order.get("recipient_name")
        payload["recipient_phone"] = order.get("recipient_phone")
        payload["delivery_address"] = order.get("delivery_address")
        payload["delivery_date"] = order.get("delivery_date", "").split("T")[0]  # Extract date part
        payload["delivery_time"] = order.get("scheduled_time", "")

    # Add optional fields
    if order.get("notes"):
        payload["notes"] = order["notes"]
    if order.get("customer_name"):
        payload["customer_name"] = order["customer_name"]

    logger.debug(f"📦 Production payload: {payload}")

    # 3. Send to Production API
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.post(
                "https://cvety.kz/api/v2/orders/create/",
                headers={
                    "Authorization": "Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            result = response.json()

            if response.status_code == 200 and result.get("status"):
                production_order_id = result.get('order_id')
                logger.info(f"✅ Order synced to Production: #{production_order_id}")

                # 4. Fetch order details to get tracking URL
                try:
                    detail_response = await client.get(
                        f"https://cvety.kz/api/v2/orders/detail",
                        params={
                            "access_token": "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144",
                            "id": production_order_id
                        }
                    )

                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        tracking_url = detail_data.get("data", {}).get("raw", {}).get("urls", {}).get("status")

                        if tracking_url:
                            result["tracking_url"] = tracking_url
                            logger.info(f"📍 Tracking URL: {tracking_url}")
                        else:
                            logger.warning("⚠️ Tracking URL not found in detail response")
                    else:
                        logger.warning(f"⚠️ Failed to fetch order details: {detail_response.status_code}")

                except Exception as e:
                    logger.warning(f"⚠️ Could not fetch tracking URL (non-critical): {e}")
                    # Non-critical error, continue with order_id
            else:
                logger.error(f"❌ Production API returned error: {result}")

            return result

    except Exception as e:
        logger.error(f"❌ Failed to sync to Production API: {e}")
        return {
            "status": False,
            "error": "production_api_failed",
            "message": f"Could not sync to Production: {str(e)}"
        }


@ToolRegistry.register(domain="orders", requires_auth=False)
async def list_orders_admin(
    telegram_user_id: str,
    shop_id: int = 8,
    status: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    List all orders for shop (admin access via Telegram).

    No token required - uses telegram_user_id for staff verification.
    Backend verifies telegram_user_id belongs to staff member.

    Args:
        telegram_user_id: Telegram user ID from bot
        shop_id: Shop ID to list orders from
        status: Optional status filter (NEW, PAID, etc.)
        limit: Max orders to return
        skip: Offset for pagination

    Returns:
        List of orders for the shop
    """
    params = merge_required_optional(
        {"telegram_user_id": telegram_user_id, "shop_id": shop_id, "limit": limit, "skip": skip},
        {"status": status}
    )

    return await api_client.get("/orders/admin/by-telegram", params=params)
