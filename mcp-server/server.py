"""
Flower Shop MCP Server - Refactored Architecture

Slim orchestrator that imports domain tools and registers them with FastMCP.
Business logic is organized into domain packages for maintainability.
"""
import os
from mcp.server.fastmcp import FastMCP

# Configure structured logging FIRST
from core.logging import configure_logging, get_logger

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Import core infrastructure
from core.config import Config
from core.registry import ToolRegistry

# Import all domain tools
from domains.auth import tools as auth_tools
from domains.products import tools as product_tools
from domains.orders import tools as order_tools
from domains.inventory import tools as inventory_tools
from domains.telegram import tools as telegram_tools
from domains.shop import tools as shop_tools
from domains.kaspi import tools as kaspi_tools
from domains.visual_search import tools as visual_search_tools

# Create MCP server instance
mcp = FastMCP(
    name="Flower Shop API",
    instructions="""
    This server provides access to a multi-tenant flower shop management system.

    Main capabilities:
    - Product catalog management (CRUD operations)
    - Order management and tracking
    - Authentication and user management
    - Warehouse operations (inventory tracking, stock movements, inventory checks)
    - Shop settings and configuration
    - Kaspi Pay integration (create payments, check status, process refunds)

    All authenticated operations require a valid JWT token obtained via login.
    Multi-tenancy is enforced via shop_id in JWT tokens.

    Payment processing via Kaspi Pay is available for Kazakhstan market.

    AI-Powered Features:
    - AI visual search using pgvector PostgreSQL (find similar products by image)
    - Smart order creation with natural language understanding
    """,
)

# ===== Register Authentication Tools =====

@mcp.tool()
async def login(phone: str, password: str):
    """Authenticate user and get access token."""
    return await auth_tools.login(phone, password)


@mcp.tool()
async def get_current_user(token: str):
    """Get current authenticated user information."""
    return await auth_tools.get_current_user(token)


# ===== Register Product Tools =====

@mcp.tool()
async def list_products(
    shop_id=None, search=None, product_type=None, enabled_only=True,
    min_price=None, max_price=None, skip=0, limit=20
):
    """Get list of products with filtering."""
    return await product_tools.list_products(
        shop_id, search, product_type, enabled_only, min_price, max_price, skip, limit
    )


@mcp.tool()
async def get_product(product_id: int, shop_id=None):
    """Get detailed information about a specific product."""
    return await product_tools.get_product(product_id, shop_id)


@mcp.tool()
async def create_product(token: str, name: str, type: str, price: int, description=None, enabled=True):
    """Create a new product (admin only)."""
    return await product_tools.create_product(token, name, type, price, description, enabled)


@mcp.tool()
async def update_product(token: str, product_id: int, name=None, price=None, description=None, enabled=None):
    """Update an existing product (admin only)."""
    return await product_tools.update_product(token, product_id, name, price, description, enabled)


@mcp.tool()
async def check_product_availability(product_id: int, quantity: int = 1, shop_id: int = Config.DEFAULT_SHOP_ID):
    """Check if a product is available in the requested quantity."""
    return await product_tools.check_product_availability(product_id, quantity, shop_id)


@mcp.tool()
async def get_bestsellers(shop_id: int = Config.DEFAULT_SHOP_ID, limit: int = 10):
    """Get bestselling products sorted by order count."""
    return await product_tools.get_bestsellers(shop_id, limit)


@mcp.tool()
async def get_featured_products(shop_id: int = Config.DEFAULT_SHOP_ID, limit: int = 10):
    """Get featured/curated products recommended by the shop."""
    return await product_tools.get_featured_products(shop_id, limit)


@mcp.tool()
async def search_products_smart(shop_id: int = Config.DEFAULT_SHOP_ID, query=None, budget=None, occasion=None, limit: int = 20):
    """Smart product search with budget and occasion filtering."""
    return await product_tools.search_products_smart(shop_id, query, budget, occasion, limit)


# ===== Register Order Tools =====

@mcp.tool()
async def list_orders(token: str, status=None, customer_phone=None, search=None, skip: int = 0, limit: int = 20):
    """Get list of orders with filtering (admin only)."""
    return await order_tools.list_orders(token, status, customer_phone, search, skip, limit)


@mcp.tool()
async def get_order(token: str, order_id: int):
    """Get detailed information about a specific order (admin only)."""
    return await order_tools.get_order(token, order_id)


@mcp.tool()
async def create_order(
    customer_name: str, customer_phone: str, delivery_date: str, delivery_time: str,
    shop_id: int, items: list, total_price: int, delivery_type: str = "delivery",
    delivery_address=None, pickup_address=None, notes=None, telegram_user_id=None,
    recipient_name=None, recipient_phone=None, sender_phone=None
):
    """Create a new order (public endpoint for Telegram bot)."""
    return await order_tools.create_order(
        customer_name, customer_phone, delivery_date, delivery_time, shop_id, items,
        total_price, delivery_type, delivery_address, pickup_address, notes,
        telegram_user_id, recipient_name, recipient_phone, sender_phone
    )


@mcp.tool()
async def update_order_status(token: str, order_id: int, status: str, notes=None):
    """Update order status (admin only)."""
    return await order_tools.update_order_status(token, order_id, status, notes)


@mcp.tool()
async def update_order(tracking_id: str, delivery_address=None, delivery_date=None,
                      delivery_time=None, delivery_notes=None, notes=None, recipient_name=None):
    """Update order details by tracking ID (customer-facing)."""
    return await order_tools.update_order(
        tracking_id, delivery_address, delivery_date, delivery_time,
        delivery_notes, notes, recipient_name
    )


@mcp.tool()
async def track_order(tracking_id: str):
    """Track order status by tracking ID (public endpoint)."""
    return await order_tools.track_order(tracking_id)


@mcp.tool()
async def track_order_by_phone(customer_phone: str, shop_id: int):
    """Track orders by customer phone number."""
    return await order_tools.track_order_by_phone(customer_phone, shop_id)


@mcp.tool()
async def preview_order_cost(shop_id: int, items: list):
    """Calculate total order cost before placing the order."""
    return await order_tools.preview_order_cost(shop_id, items)


@mcp.tool()
async def cancel_order(order_id: int, reason: str, shop_id: int = Config.DEFAULT_SHOP_ID):
    """Cancel an order. Only NEW/PENDING orders can be cancelled."""
    return await order_tools.cancel_order(order_id, reason, shop_id)


@mcp.tool()
async def sync_order_to_production(order_data=None, tracking_id=None, shop_id: int = Config.DEFAULT_SHOP_ID):
    """Sync Railway order to Production Bitrix system."""
    return await order_tools.sync_order_to_production(order_data, tracking_id, shop_id)


# ===== Register Inventory Tools =====

@mcp.tool()
async def list_warehouse_items(token: str, search=None, skip: int = 0, limit: int = 50):
    """Get list of warehouse inventory items (admin only)."""
    return await inventory_tools.list_warehouse_items(token, search, skip, limit)


@mcp.tool()
async def add_warehouse_stock(token: str, warehouse_item_id: int, quantity: int, notes=None):
    """Add stock to warehouse item (admin only)."""
    return await inventory_tools.add_warehouse_stock(token, warehouse_item_id, quantity, notes)


@mcp.tool()
async def record_warehouse_operation(
    token: str,
    warehouse_item_id: int,
    quantity: int,
    operation_type: str,
    notes=None
):
    """Record warehouse stock movement operation (admin only)."""
    return await inventory_tools.record_warehouse_operation(
        token, warehouse_item_id, quantity, operation_type, notes
    )


@mcp.tool()
async def get_warehouse_history(
    token: str,
    warehouse_item_id: int,
    operation_type=None,
    skip: int = 0,
    limit: int = 50
):
    """Get warehouse operations history for a specific item (admin only)."""
    return await inventory_tools.get_warehouse_history(
        token, warehouse_item_id, operation_type, skip, limit
    )


@mcp.tool()
async def create_inventory_check(token: str, conducted_by: str, items: list, comment=None):
    """Create new inventory check with all items (admin only)."""
    return await inventory_tools.create_inventory_check(token, conducted_by, items, comment)


@mcp.tool()
async def list_inventory_checks(token: str, skip: int = 0, limit: int = 20):
    """Get list of inventory checks (admin only)."""
    return await inventory_tools.list_inventory_checks(token, skip, limit)


# ===== Register Telegram Tools =====

@mcp.tool()
async def get_telegram_client(telegram_user_id: str, shop_id: int):
    """Get telegram client by telegram_user_id and shop_id."""
    return await telegram_tools.get_telegram_client(telegram_user_id, shop_id)


@mcp.tool()
async def register_telegram_client(
    telegram_user_id: str, phone: str, customer_name: str, shop_id: int,
    telegram_username=None, telegram_first_name=None
):
    """Register or update a telegram client with contact information."""
    return await telegram_tools.register_telegram_client(
        telegram_user_id, phone, customer_name, shop_id, telegram_username, telegram_first_name
    )


# ===== Register Shop Tools =====

@mcp.tool()
async def get_shop_settings(shop_id: int):
    """Get public shop settings and configuration."""
    return await shop_tools.get_shop_settings(shop_id)


@mcp.tool()
async def get_working_hours(shop_id: int):
    """Get shop working hours schedule."""
    return await shop_tools.get_working_hours(shop_id)


@mcp.tool()
async def update_shop_settings(token: str, shop_name=None, description=None, phone=None, email=None, address=None):
    """Update shop settings (admin only)."""
    return await shop_tools.update_shop_settings(token, shop_name, description, phone, email, address)


@mcp.tool()
async def get_faq(shop_id: int = Config.DEFAULT_SHOP_ID, category=None):
    """Get Frequently Asked Questions for the shop."""
    return await shop_tools.get_faq(shop_id, category)


@mcp.tool()
async def get_reviews(shop_id: int = Config.DEFAULT_SHOP_ID, limit: int = 10):
    """Get company reviews with ratings and statistics."""
    return await shop_tools.get_reviews(shop_id, limit)


@mcp.tool()
async def get_client_profile(telegram_user_id: str, shop_id: int = Config.DEFAULT_SHOP_ID):
    """Get client profile with order history and saved addresses."""
    return await shop_tools.get_client_profile(telegram_user_id, shop_id)


@mcp.tool()
async def save_client_address(
    telegram_user_id: str, name: str, address: str, phone: str,
    shop_id: int = Config.DEFAULT_SHOP_ID, is_default: bool = False
):
    """Save client address for future orders."""
    return await shop_tools.save_client_address(telegram_user_id, name, address, phone, shop_id, is_default)


@mcp.tool()
async def get_delivery_slots(shop_id: int = Config.DEFAULT_SHOP_ID, date: str = "", product_ids=None):
    """Get available delivery windows for a specific date."""
    return await shop_tools.get_delivery_slots(shop_id, date, product_ids)


@mcp.tool()
async def validate_delivery_time(shop_id: int = Config.DEFAULT_SHOP_ID, delivery_time: str = "", product_ids=None):
    """Validate customer's exact requested delivery time."""
    return await shop_tools.validate_delivery_time(shop_id, delivery_time, product_ids)


@mcp.tool()
async def check_delivery_feasibility(shop_id: int = Config.DEFAULT_SHOP_ID, delivery_date: str = "", product_ids=None):
    """Check if delivery is feasible on requested date."""
    return await shop_tools.check_delivery_feasibility(shop_id, delivery_date, product_ids)


# ===== Register Kaspi Pay Tools =====

@mcp.tool()
async def kaspi_create_payment(phone: str, amount: float, message: str):
    """Create a new Kaspi Pay remote payment request."""
    return await kaspi_tools.kaspi_create_payment(phone, amount, message)


@mcp.tool()
async def kaspi_check_payment_status(external_id: str):
    """Check status of a Kaspi Pay payment."""
    return await kaspi_tools.kaspi_check_payment_status(external_id)


@mcp.tool()
async def kaspi_get_payment_details(external_id: str):
    """Get detailed information about a Kaspi Pay payment."""
    return await kaspi_tools.kaspi_get_payment_details(external_id)


@mcp.tool()
async def kaspi_refund_payment(external_id: str, amount: float):
    """Refund a Kaspi Pay payment (full or partial)."""
    return await kaspi_tools.kaspi_refund_payment(external_id, amount)


# ===== Register Visual Search Tools =====

@mcp.tool()
async def search_similar_bouquets(image_url: str, shop_id: int, topK: int = 5):
    """Find similar bouquets using AI-powered visual search."""
    return await visual_search_tools.search_similar_bouquets(image_url, shop_id, topK)


# ===== Main Entry Point =====

if __name__ == "__main__":
    # Validate and print registry summary
    ToolRegistry.validate()
    ToolRegistry.print_summary()

    # Run MCP server
    mcp.run()
