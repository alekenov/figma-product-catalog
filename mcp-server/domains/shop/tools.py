"""
Shop management tools for MCP server.
"""
from typing import Dict, Any, Optional, List
from core.api_client import api_client
from core.registry import ToolRegistry
from core.config import Config
from core.utils import merge_required_optional, drop_none


# Shop Settings

@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def get_shop_settings(shop_id: int) -> Dict[str, Any]:
    """Get public shop settings and configuration."""
    return await api_client.get(
        "/shop/settings/public",
        params={"shop_id": shop_id}
    )


@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def get_working_hours(shop_id: int) -> Dict[str, Any]:
    """Get shop working hours schedule."""
    shop = await api_client.get(
        "/shop/settings/public",
        params={"shop_id": shop_id}
    )

    return {
        "weekday_start": shop.get("weekday_start"),
        "weekday_end": shop.get("weekday_end"),
        "weekday_closed": shop.get("weekday_closed", False),
        "weekend_start": shop.get("weekend_start"),
        "weekend_end": shop.get("weekend_end"),
        "weekend_closed": shop.get("weekend_closed", False),
    }


@ToolRegistry.register(domain="shop", requires_auth=True)
async def update_shop_settings(
    token: str,
    shop_name: Optional[str] = None,
    description: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
) -> Dict[str, Any]:
    """Update shop settings (admin only)."""
    data = drop_none(
        {
            "shop_name": shop_name,
            "description": description,
            "phone": phone,
            "email": email,
            "address": address,
        }
    )

    return await api_client.put("/shop/settings", json_data=data, token=token)


# Content & Discovery

@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def get_faq(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get Frequently Asked Questions for the shop."""
    params = merge_required_optional(
        {"shop_id": shop_id},
        {"category": category},
    )
    return await api_client.get("/content/faqs", params=params)


@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def get_reviews(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    limit: int = 10
) -> Dict[str, Any]:
    """Get company reviews with ratings and statistics."""
    return await api_client.get(
        "/reviews/company",
        params={"limit": limit, "offset": 0}
    )


# Client Profile

@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def get_client_profile(
    telegram_user_id: str,
    shop_id: int = Config.DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """Get client profile with order history and saved addresses."""
    return await api_client.get(
        f"/clients/telegram/{telegram_user_id}/profile",
        params={"shop_id": shop_id}
    )


@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def save_client_address(
    telegram_user_id: str,
    name: str,
    address: str,
    phone: str,
    shop_id: int = Config.DEFAULT_SHOP_ID,
    is_default: bool = False
) -> Dict[str, Any]:
    """Save client address for future orders."""
    return await api_client.post(
        f"/clients/telegram/{telegram_user_id}/addresses",
        json_data={
            "name": name,
            "address": address,
            "phone": phone,
            "is_default": is_default
        },
        params={"shop_id": shop_id}
    )


# Delivery Logistics

@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def get_delivery_slots(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    date: str = "",
    product_ids: Optional[str] = None
) -> Dict[str, Any]:
    """Get available delivery windows for a specific date."""
    return await api_client.get(
        "/delivery/slots",
        params=merge_required_optional(
            {"shop_id": shop_id, "date": date},
            {"product_ids": product_ids},
        ),
    )


@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def validate_delivery_time(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    delivery_time: str = "",
    product_ids: Optional[str] = None
) -> Dict[str, Any]:
    """Validate customer's exact requested delivery time."""
    return await api_client.post(
        "/delivery/validate",
        json_data={},  # Backend uses query params for this endpoint
        params=merge_required_optional(
            {"shop_id": shop_id, "delivery_time": delivery_time},
            {"product_ids": product_ids},
        ),
    )


@ToolRegistry.register(domain="shop", requires_auth=False, is_public=True)
async def check_delivery_feasibility(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    delivery_date: str = "",
    product_ids: Optional[str] = None
) -> Dict[str, Any]:
    """Check if delivery is feasible on requested date."""
    return await api_client.get(
        "/delivery/feasibility",
        params=merge_required_optional(
            {"shop_id": shop_id, "delivery_date": delivery_date},
            {"product_ids": product_ids},
        ),
    )
