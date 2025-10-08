"""
Telegram client management tools for MCP server.
"""
from typing import Optional, Dict, Any
from core.api_client import api_client
from core.registry import ToolRegistry


@ToolRegistry.register(domain="telegram", requires_auth=False, is_public=True)
async def get_telegram_client(telegram_user_id: str, shop_id: int) -> Optional[Dict[str, Any]]:
    """
    Get telegram client by telegram_user_id and shop_id.
    Used to check if telegram user is already registered.
    """
    return await api_client.get(
        "/telegram/client",
        params={"telegram_user_id": telegram_user_id, "shop_id": shop_id}
    )


@ToolRegistry.register(domain="telegram", requires_auth=False, is_public=True)
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
    """
    return await api_client.post(
        "/telegram/client/register",
        json_data={
            "telegram_user_id": telegram_user_id,
            "phone": phone,
            "customer_name": customer_name,
            "shop_id": shop_id,
            "telegram_username": telegram_username,
            "telegram_first_name": telegram_first_name
        }
    )
