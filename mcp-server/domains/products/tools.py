"""
Product tools for MCP server.
Handles product catalog, availability checking, and search.
"""
from typing import List, Dict, Any, Optional
from core.api_client import api_client
from core.registry import ToolRegistry
from core.config import Config
from core.utils import merge_required_optional, drop_none


# Product CRUD Tools

@ToolRegistry.register(domain="products", requires_auth=False, is_public=True)
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
        product_type: Filter by type. Valid values: "flowers", "sweets", "fruits", "gifts"
        enabled_only: Show only enabled products
        min_price: Minimum price in tenge
        max_price: Maximum price in tenge
        skip: Number of products to skip (pagination)
        limit: Number of products to return (max 100)

    Returns:
        List of products with details
    """
    params = merge_required_optional(
        {"skip": skip, "limit": limit, "enabled_only": enabled_only},
        {
            "shop_id": shop_id,
            "search": search,
            "type": product_type,
            "min_price": min_price,
            "max_price": max_price,
        },
    )

    return await api_client.get("/products/", params=params)


@ToolRegistry.register(domain="products", requires_auth=False, is_public=True)
async def get_product(product_id: int, shop_id: Optional[int] = None) -> Dict[str, Any]:
    """Get detailed information about a specific product."""
    return await api_client.get(
        f"/products/{product_id}",
        params=drop_none({"shop_id": shop_id}),
    )


@ToolRegistry.register(domain="products", requires_auth=True)
async def create_product(
    token: str,
    name: str,
    type: str,
    price: int,
    description: Optional[str] = None,
    enabled: bool = True,
) -> Dict[str, Any]:
    """Create a new product (admin only)."""
    data = drop_none({
        "name": name,
        "type": type,
        "price": price,
        "enabled": enabled,
        "description": description,
    })

    return await api_client.post("/products/", json_data=data, token=token)


@ToolRegistry.register(domain="products", requires_auth=True)
async def update_product(
    token: str,
    product_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update an existing product (admin only)."""
    data = drop_none(
        {
            "name": name,
            "price": price,
            "description": description,
            "enabled": enabled,
        }
    )

    return await api_client.put(f"/products/{product_id}", json_data=data, token=token)


# Product Discovery Tools

@ToolRegistry.register(domain="products", requires_auth=False, is_public=True)
async def check_product_availability(
    product_id: int,
    quantity: int = 1,
    shop_id: int = Config.DEFAULT_SHOP_ID
) -> Dict[str, Any]:
    """
    Check if a product is available in the requested quantity.
    Considers warehouse inventory and product recipes.
    """
    return await api_client.get(
        f"/products/{product_id}/availability",
        params=merge_required_optional(
            {"quantity": quantity},
            {"shop_id": shop_id},
        ),
    )


@ToolRegistry.register(domain="products", requires_auth=False, is_public=True)
async def get_bestsellers(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get bestselling products sorted by order count."""
    return await api_client.get(
        "/products/public/bestsellers",
        params=merge_required_optional(
            {"limit": limit},
            {"shop_id": shop_id},
        ),
    )


@ToolRegistry.register(domain="products", requires_auth=False, is_public=True)
async def get_featured_products(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get featured/curated products recommended by the shop."""
    return await api_client.get(
        "/products/public/featured",
        params=merge_required_optional(
            {"skip": 0, "limit": limit},
            {"shop_id": shop_id},
        ),
    )


@ToolRegistry.register(domain="products", requires_auth=False, is_public=True)
async def search_products_smart(
    shop_id: int = Config.DEFAULT_SHOP_ID,
    query: Optional[str] = None,
    budget: Optional[int] = None,
    occasion: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Smart product search with budget and occasion filtering.

    Args:
        query: Search text (e.g., "розы", "тюльпаны")
        budget: Max price in tenge
        occasion: "birthday", "wedding", "funeral", "romantic", etc.
    """
    return await api_client.get(
        "/products/public/smart-search",
        params=merge_required_optional(
            {"shop_id": shop_id, "limit": limit},
            {
                "query": query,
                "budget": budget,
                "occasion": occasion,
            },
        ),
    )
