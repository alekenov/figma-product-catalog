"""Product management tools for Production API."""

import sys
sys.path.append('../../mcp-shared')

from client import CvetyProductionClient
from config import settings
from mcp_shared.schemas.products import ProductResponse, ProductCreate, ProductStatusUpdate
from mcp_shared.enums import ProductType
from mcp_shared.utils.logging import get_logger
from uuid import uuid4

logger = get_logger(__name__)


async def list_products_production(
    product_type: str | None = None,
    is_available: bool | None = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    List products from cvety.kz production API.

    Args:
        product_type: Filter by type ('vitrina' or 'catalog')
        is_available: Filter by availability
        limit: Maximum number of products to return (1-100)
        offset: Number of products to skip

    Returns:
        {
            "success": true,
            "data": [ProductResponse...],
            "total": 150
        }

    Example:
        # Get first 10 ready-made bouquets
        await list_products_production(product_type="vitrina", limit=10)
    """
    client = CvetyProductionClient()

    params = {
        "limit": min(max(1, limit), 100),
        "offset": offset,
        "cityId": settings.cvety_city_id
    }

    if product_type:
        params["type"] = product_type

    if is_available is not None:
        params["isAvailable"] = is_available

    logger.info(f"Listing products from Production: {params}")

    response = await client.get("/products", params=params)

    return {
        "success": True,
        "data": response.get("data", []),
        "total": len(response.get("data", []))
    }


async def create_product_production(
    title: str,
    price: int,
    images_urls: list[str],
    section: list[str],
    color: list[str],
    description: str | None = None
) -> dict:
    """
    Create a new product on cvety.kz production.

    Args:
        title: Product title (min 3 chars)
        price: Price in kopecks (e.g., 1500000 = 15,000₸)
        images_urls: List of image URLs (at least 1)
        section: Product sections (e.g., ["roses"])
        color: Product colors (e.g., ["red", "pink"])
        description: Optional product description

    Returns:
        {
            "success": true,
            "data": {
                "id": 12345,
                "xml_id": "mcp-abc123",
                "created": true
            }
        }

    Example:
        await create_product_production(
            title="Букет роз 25 шт",
            price=1500000,  # 15,000₸
            images_urls=["https://cdn.example.com/roses.jpg"],
            section=["roses"],
            color=["red"]
        )
    """
    client = CvetyProductionClient()

    product_id = f"mcp-{uuid4().hex[:8]}"

    payload = {
        "id": product_id,
        "title": title,
        "price": price,
        "images_urls": images_urls,
        "owner": "cvetykz",  # shop XML_ID for shop_id=17008
        "properties": {
            "section": section,
            "color": color
        }
    }

    if description:
        payload["description"] = description

    logger.info(f"Creating product on Production: {title}")

    response = await client.post("/create", json_data=payload)

    return {
        "success": response.get("status", False),
        "data": response.get("data", {}),
        "timestamp": response.get("timestamp")
    }


async def update_product_status_production(
    product_id: int,
    active: bool | None = None,
    in_stock: bool | None = None,
    is_ready: bool | None = None
) -> dict:
    """
    Update product status (active, in_stock, is_ready) on Production.

    Args:
        product_id: Product ID
        active: Set product active/inactive
        in_stock: Set product in stock / out of stock
        is_ready: Set product as ready-made bouquet (vitrina)

    Returns:
        {
            "success": true,
            "data": {
                "active": true,
                "in_stock": true
            }
        }

    Example:
        # Deactivate product
        await update_product_status_production(product_id=123, active=False)
    """
    client = CvetyProductionClient()

    payload = {"id": product_id}

    if active is not None:
        payload["active"] = active

    if in_stock is not None:
        payload["in_stock"] = in_stock

    if is_ready is not None:
        payload["is_ready"] = is_ready

    logger.info(f"Updating product {product_id} status on Production: {payload}")

    response = await client.post("/update-status", json_data=payload)

    return {
        "success": response.get("status", False),
        "data": response.get("changed", {}),
        "timestamp": response.get("timestamp")
    }


async def delete_product_production(product_id: int) -> dict:
    """
    Delete a product from Production API.

    ⚠️ WARNING: This is a destructive operation. Product cannot be recovered.

    Args:
        product_id: Product ID to delete

    Returns:
        {
            "success": true,
            "message": "Product deleted"
        }

    Example:
        await delete_product_production(product_id=123)
    """
    client = CvetyProductionClient()

    logger.warning(f"Deleting product {product_id} from Production")

    response = await client.post(f"/products/delete", json_data={"id": product_id})

    return {
        "success": response.get("status", False),
        "message": "Product deleted",
        "timestamp": response.get("timestamp")
    }
