"""
Product Helpers - Reusable data loading utilities

Consolidates database queries to eliminate duplication.
Provides clean interfaces for loading products with relations.
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, case
from sqlmodel import select, col
from fastapi import HTTPException

from models import (
    Product, ProductType, ProductImage, ProductVariant, ProductAddon,
    ProductBundle, ProductRecipe, ProductReview, CompanyReview, PickupLocation
)


async def get_products_filtered(
    session: AsyncSession,
    shop_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    product_type: Optional[ProductType] = None,
    enabled_only: bool = True,
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    city: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Product]:
    """
    Get products with filtering, search, and pagination.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy (required for tenant isolation)
        skip: Number of products to skip (pagination)
        limit: Maximum number of products to return
        product_type: Filter by product type
        enabled_only: Only return enabled products
        search: Search query for product names
        min_price: Minimum price filter
        max_price: Maximum price filter
        city: Filter by city (JSON array field)
        tags: Filter by tags (JSON array field)

    Returns:
        List of Product instances
    """
    # Build query
    query = select(Product)

    # CRITICAL: Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(Product.shop_id == shop_id)

    # Apply filters
    if enabled_only:
        query = query.where(Product.enabled == True)

    if product_type:
        query = query.where(Product.type == product_type)

    if search:
        query = query.where(col(Product.name).ilike(f"%{search}%"))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # Filter by city if provided
    if city:
        query = query.where(func.json_extract(Product.cities, '$').like(f'%{city.lower()}%'))

    # Filter by tags if provided
    if tags:
        for tag in tags:
            query = query.where(func.json_extract(Product.tags, '$').like(f'%{tag}%'))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_all_enabled_products(session: AsyncSession, shop_id: Optional[int] = None) -> List[Product]:
    """
    Get all enabled products.
    Used for extracting available tags, cities, and price ranges.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy

    Returns:
        List of all enabled Product instances
    """
    query = select(Product).where(Product.enabled == True)

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(Product.shop_id == shop_id)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_product_by_id(
    session: AsyncSession,
    product_id: int,
    shop_id: Optional[int] = None,
    raise_if_not_found: bool = True
) -> Optional[Product]:
    """
    Get single product by ID with shop_id verification.

    Args:
        session: Database session
        product_id: Product ID
        shop_id: Filter by shop_id for multi-tenancy
        raise_if_not_found: Raise HTTPException if product not found

    Returns:
        Product instance or None

    Raises:
        HTTPException: If product not found and raise_if_not_found=True
    """
    query = select(Product).where(Product.id == product_id)

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(Product.shop_id == shop_id)

    result = await session.execute(query)
    product = result.scalar_one_or_none()

    if not product and raise_if_not_found:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def load_product_with_recipes(
    session: AsyncSession,
    product_id: int,
    shop_id: Optional[int] = None
) -> Optional[Product]:
    """
    Load product with recipes and warehouse items eagerly loaded.

    Args:
        session: Database session
        product_id: Product ID
        shop_id: Filter by shop_id for multi-tenancy

    Returns:
        Product instance with recipes loaded, or None
    """
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.recipes).selectinload(ProductRecipe.warehouse_item)
        )
    )

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        stmt = stmt.where(Product.shop_id == shop_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def load_product_images(
    session: AsyncSession,
    product_id: int
) -> List[ProductImage]:
    """
    Load all images for a product, ordered by display order.

    Args:
        session: Database session
        product_id: Product ID

    Returns:
        List of ProductImage instances
    """
    result = await session.execute(
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.order)
    )
    return list(result.scalars().all())


async def load_product_variants(
    session: AsyncSession,
    product_id: int,
    enabled_only: bool = True
) -> List[ProductVariant]:
    """
    Load product variants (sizes), ordered by price.

    Args:
        session: Database session
        product_id: Product ID
        enabled_only: Only return enabled variants

    Returns:
        List of ProductVariant instances
    """
    query = (
        select(ProductVariant)
        .where(ProductVariant.product_id == product_id)
        .order_by(ProductVariant.price)
    )

    if enabled_only:
        query = query.where(ProductVariant.enabled == True)

    result = await session.execute(query)
    return list(result.scalars().all())


async def load_product_addons(
    session: AsyncSession,
    product_id: int,
    enabled_only: bool = True
) -> List[ProductAddon]:
    """
    Load product addons.

    Args:
        session: Database session
        product_id: Product ID
        enabled_only: Only return enabled addons

    Returns:
        List of ProductAddon instances
    """
    query = (
        select(ProductAddon)
        .where(ProductAddon.product_id == product_id)
    )

    if enabled_only:
        query = query.where(ProductAddon.enabled == True)

    result = await session.execute(query)
    return list(result.scalars().all())


async def load_product_bundles(
    session: AsyncSession,
    product_id: int,
    limit: int = 5
) -> List[Tuple[ProductBundle, Product]]:
    """
    Load frequently bought together products.

    Args:
        session: Database session
        product_id: Main product ID
        limit: Maximum number of bundles to return

    Returns:
        List of (ProductBundle, Product) tuples
    """
    result = await session.execute(
        select(ProductBundle, Product)
        .join(Product, ProductBundle.bundled_product_id == Product.id)
        .where(ProductBundle.main_product_id == product_id)
        .where(ProductBundle.enabled == True)
        .where(Product.enabled == True)
        .order_by(ProductBundle.display_order)
        .limit(limit)
    )
    return list(result.all())


async def load_pickup_locations(
    session: AsyncSession,
    shop_id: Optional[int] = None,
    enabled_only: bool = True
) -> List[PickupLocation]:
    """
    Load pickup locations ordered by display order.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy
        enabled_only: Only return enabled locations

    Returns:
        List of PickupLocation instances
    """
    query = select(PickupLocation)

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(PickupLocation.shop_id == shop_id)

    query = query.order_by(PickupLocation.display_order)

    if enabled_only:
        query = query.where(PickupLocation.enabled == True)

    result = await session.execute(query)
    return list(result.scalars().all())


async def load_product_reviews(
    session: AsyncSession,
    product_id: int,
    limit: int = 10
) -> List[ProductReview]:
    """
    Load product reviews with photos eagerly loaded.

    Args:
        session: Database session
        product_id: Product ID
        limit: Maximum number of reviews to return

    Returns:
        List of ProductReview instances with photos loaded
    """
    result = await session.execute(
        select(ProductReview)
        .where(ProductReview.product_id == product_id)
        .options(selectinload(ProductReview.photos))
        .order_by(ProductReview.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def load_company_reviews(
    session: AsyncSession,
    shop_id: Optional[int] = None,
    limit: int = 10
) -> List[CompanyReview]:
    """
    Load company-wide reviews.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy
        limit: Maximum number of reviews to return

    Returns:
        List of CompanyReview instances
    """
    query = select(CompanyReview)

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(CompanyReview.shop_id == shop_id)

    query = query.order_by(CompanyReview.created_at.desc()).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def search_product_suggestions(
    session: AsyncSession,
    search_query: str,
    shop_id: Optional[int] = None,
    limit: int = 5
) -> List[str]:
    """
    Get product name suggestions for autocomplete.

    Args:
        session: Database session
        search_query: Search query string
        shop_id: Filter by shop_id for multi-tenancy
        limit: Maximum number of suggestions

    Returns:
        List of product names matching the query
    """
    query = (
        select(Product.name)
        .where(col(Product.name).ilike(f"%{search_query}%"))
        .where(Product.enabled == True)
    )

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        query = query.where(Product.shop_id == shop_id)

    query = query.limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_product_statistics(
    session: AsyncSession,
    shop_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get product statistics summary with counts by type.

    Args:
        session: Database session
        shop_id: Filter by shop_id for multi-tenancy

    Returns:
        Dictionary with total, enabled, disabled counts and breakdown by type
    """
    # Single aggregating query for all statistics
    stats_query = select(
        func.count(Product.id).label("total"),
        func.sum(case((Product.enabled == True, 1), else_=0)).label("enabled"),
        func.sum(case((Product.type == ProductType.FLOWERS, 1), else_=0)).label("flowers"),
        func.sum(case((Product.type == ProductType.SWEETS, 1), else_=0)).label("sweets"),
        func.sum(case((Product.type == ProductType.FRUITS, 1), else_=0)).label("fruits"),
        func.sum(case((Product.type == ProductType.GIFTS, 1), else_=0)).label("gifts")
    )

    # Filter by shop_id for multi-tenancy
    if shop_id is not None:
        stats_query = stats_query.where(Product.shop_id == shop_id)

    result = await session.execute(stats_query)
    stats = result.first()

    # Handle None values with defaults
    total = stats.total or 0
    enabled = stats.enabled or 0

    return {
        "total": total,
        "enabled": enabled,
        "disabled": total - enabled,
        "by_type": {
            ProductType.FLOWERS.value: stats.flowers or 0,
            ProductType.SWEETS.value: stats.sweets or 0,
            ProductType.FRUITS.value: stats.fruits or 0,
            ProductType.GIFTS.value: stats.gifts or 0
        }
    }
