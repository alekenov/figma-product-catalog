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
        json_data={"items": items},
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
