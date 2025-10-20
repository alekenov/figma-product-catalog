"""MCP Production Server - Proxy for cvety.kz API."""

import sys
sys.path.append('../mcp-shared')

from fastmcp import FastMCP
from config import settings
from mcp_shared.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging(level=settings.log_level, format_json=settings.log_json)
logger = get_logger(__name__)

# Initialize MCP server
mcp = FastMCP("cvety-production", dependencies=["httpx", "pydantic", "pydantic-settings"])

logger.info("Starting MCP Production Server")
logger.info(f"Production API: {settings.cvety_api_base_url}")
logger.info(f"Shop ID: {settings.cvety_shop_id}, City ID: {settings.cvety_city_id}")


# Import and register tools
from domains.products.tools import (
    list_products_production,
    create_product_production,
    update_product_status_production,
    delete_product_production,
)

from domains.orders.tools import (
    list_orders_production,
    get_order_details_production,
    update_order_status_production,
)


# Products
@mcp.tool()
async def list_products(
    product_type: str | None = None,
    is_available: bool | None = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """List products from cvety.kz production. Filter by type (vitrina/catalog) and availability."""
    return await list_products_production(product_type, is_available, limit, offset)


@mcp.tool()
async def create_product(
    title: str,
    price: int,
    images_urls: list[str],
    section: list[str],
    color: list[str],
    description: str | None = None
) -> dict:
    """Create new product on production. Price in kopecks (15000₸ = 1500000)."""
    return await create_product_production(title, price, images_urls, section, color, description)


@mcp.tool()
async def update_product_status(
    product_id: int,
    active: bool | None = None,
    in_stock: bool | None = None,
    is_ready: bool | None = None
) -> dict:
    """Update product status (active, in_stock, is_ready) on production."""
    return await update_product_status_production(product_id, active, in_stock, is_ready)


@mcp.tool()
async def delete_product(product_id: int) -> dict:
    """⚠️ Delete product from production (destructive operation)."""
    return await delete_product_production(product_id)


# Orders
@mcp.tool()
async def list_orders(
    status: str | None = None,
    customer_phone: str | None = None,
    limit: int = 20
) -> dict:
    """List orders from production. Filter by status (assembled, in-transit, delivered) or customer phone."""
    return await list_orders_production(status, customer_phone, limit)


@mcp.tool()
async def get_order_details(order_id: int) -> dict:
    """Get detailed information about a specific order from production."""
    return await get_order_details_production(order_id)


@mcp.tool()
async def update_order_status(
    order_id: int,
    new_status: str,
    notes: str | None = None
) -> dict:
    """Update order status on production. Valid: assembled→in-transit→delivered or →cancelled."""
    return await update_order_status_production(order_id, new_status, notes)


# Health check
@mcp.tool()
async def health_check() -> dict:
    """Check if MCP Production server is healthy and can connect to cvety.kz API."""
    from client import CvetyProductionClient

    try:
        client = CvetyProductionClient()
        # Try to fetch shop info as health check
        response = await client.get("/shop-info")

        return {
            "success": True,
            "server": "mcp-production",
            "production_api": "online",
            "shop_id": settings.cvety_shop_id,
            "city_id": settings.cvety_city_id
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "server": "mcp-production",
            "production_api": "offline",
            "error": str(e)
        }


if __name__ == "__main__":
    logger.info("MCP Production Server ready")
    logger.info("Available tools: 8 (products: 4, orders: 3, health: 1)")
