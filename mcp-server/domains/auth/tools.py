"""
Authentication tools for MCP server.
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

from core.api_client import api_client
from core.registry import ToolRegistry

# Note: mcp instance is imported from server.py during registration
mcp = None  # Will be set during initialization


def init_mcp(mcp_instance: FastMCP):
    """Initialize MCP instance for this module."""
    global mcp
    mcp = mcp_instance


@ToolRegistry.register(domain="auth", requires_auth=False, is_public=True)
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
    result = await api_client.post(
        endpoint="/auth/login",
        json_data={"phone": phone, "password": password},
    )
    return result


@ToolRegistry.register(domain="auth", requires_auth=True)
async def get_current_user(token: str) -> Dict[str, Any]:
    """
    Get current authenticated user information.

    Args:
        token: JWT access token from login

    Returns:
        User information including id, phone, role, shop_id
    """
    result = await api_client.get(
        endpoint="/auth/me",
        token=token,
    )
    return result
