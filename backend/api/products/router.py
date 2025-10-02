"""
Products Router - Thin route handlers

All route handlers follow the pattern:
1. Validate input
2. Call helpers for data loading
3. Call service for business logic (write operations)
4. Call presenters for response formatting
5. Return response

No business logic or DB queries directly in routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import (
    Product, ProductCreate, ProductRead, ProductUpdate, ProductType,
    ProductAvailability, ProductDetailRead, ProductImageCreate, ProductImageRead
)
from services.inventory_service import InventoryService
from services.product_service import ProductService
from auth_utils import get_current_user_shop_id

from . import helpers
from . import presenters
from . import validations

router = APIRouter()


# ===== Public Read Endpoints =====

@router.get("/", response_model=List[ProductRead])
async def get_products(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of products to return"),
    type: Optional[ProductType] = Query(None, description="Filter by product type"),
    enabled_only: bool = Query(True, description="Show only enabled products"),
    search: Optional[str] = Query(None, description="Search in product names"),
    min_price: Optional[int] = Query(None, description="Minimum price in tenge"),
    max_price: Optional[int] = Query(None, description="Maximum price in tenge"),
    shop_id: Optional[int] = Query(None, description="Filter by shop_id for multi-tenancy")
):
    """
    Get list of products with filtering and search.

    For customer website: pass shop_id query parameter
    For admin panel: use authenticated endpoint /admin/products
    """
    products = await helpers.get_products_filtered(
        session=session,
        shop_id=shop_id,
        skip=skip,
        limit=limit,
        product_type=type,
        enabled_only=enabled_only,
        search=search,
        min_price=min_price,
        max_price=max_price
    )
    return products


# ===== Admin Authenticated Endpoints =====

@router.get("/admin/products", response_model=List[ProductRead])
async def get_admin_products(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of products to return"),
    type: Optional[ProductType] = Query(None, description="Filter by product type"),
    enabled_only: bool = Query(False, description="Show only enabled products"),
    search: Optional[str] = Query(None, description="Search in product names"),
    min_price: Optional[int] = Query(None, description="Minimum price in tenge"),
    max_price: Optional[int] = Query(None, description="Maximum price in tenge"),
):
    """
    Get products for authenticated admin users.
    Automatically filters by the user's shop_id for complete data isolation.
    """
    products = await helpers.get_products_filtered(
        session=session,
        shop_id=shop_id,  # Automatically injected from JWT
        skip=skip,
        limit=limit,
        product_type=type,
        enabled_only=enabled_only,
        search=search,
        min_price=min_price,
        max_price=max_price
    )
    return products


@router.get("/home")
async def get_home_products(
    *,
    session: AsyncSession = Depends(get_session),
    city: Optional[str] = Query(None, description="Filter by city"),
    tags: Optional[str] = Query(None, description="Comma-separated tags (urgent,budget,discount)"),
    limit: int = Query(20, ge=1, le=100, description="Number of products to return")
):
    """
    Get products for homepage with featured items and filters.

    Returns:
    - featured: Featured/bestseller products
    - available_tags: All unique tags from products
    - bestsellers: Same as featured for now
    """
    # Parse tags if provided
    tag_list = validations.parse_tag_list(tags) if tags else None

    # Get filtered products
    featured_products = await helpers.get_products_filtered(
        session=session,
        limit=limit,
        enabled_only=True,
        city=city,
        tags=tag_list
    )

    # Get all enabled products to extract available tags
    all_products = await helpers.get_all_enabled_products(session)
    available_tags = presenters.extract_unique_tags(all_products)

    return presenters.build_home_response(featured_products, available_tags)


@router.get("/filters")
async def get_product_filters(
    *,
    session: AsyncSession = Depends(get_session)
):
    """
    Get available filter options for products.

    Returns all unique tags, price range, and available cities.
    """
    # Get all enabled products
    products = await helpers.get_all_enabled_products(session)

    # Extract filter data
    tags = presenters.extract_unique_tags(products)
    cities = presenters.extract_unique_cities(products)
    price_range = presenters.calculate_price_range(products)

    return presenters.build_filters_response(tags, cities, price_range)


@router.get("/{product_id}/detail", response_model=ProductDetailRead)
async def get_product_detail(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int
):
    """
    Get complete product details with all relationships:
    - Images, variants, composition, addons, bundles
    - Product and company reviews with aggregates
    - Pickup locations
    """
    # Load product with recipes
    product = await helpers.load_product_with_recipes(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Load all relationships in parallel (conceptually - async will handle)
    images = await helpers.load_product_images(session, product_id)
    variants = await helpers.load_product_variants(session, product_id, enabled_only=True)
    addons = await helpers.load_product_addons(session, product_id, enabled_only=True)
    bundle_rows = await helpers.load_product_bundles(session, product_id, limit=5)
    pickup_locations_data = await helpers.load_pickup_locations(session, enabled_only=True)
    product_reviews = await helpers.load_product_reviews(session, product_id, limit=10)
    company_reviews = await helpers.load_company_reviews(session, limit=10)

    # Format data using presenters
    composition = presenters.format_composition(product.recipes)
    frequently_bought = presenters.format_bundles(bundle_rows)
    pickup_locations = presenters.format_pickup_locations(pickup_locations_data)

    # Build complete response
    return presenters.build_product_detail_read(
        product=product,
        images=images,
        variants=variants,
        addons=addons,
        composition=composition,
        frequently_bought=frequently_bought,
        pickup_locations=pickup_locations,
        product_reviews=product_reviews,
        company_reviews=company_reviews
    )


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int
):
    """Get single product by ID"""
    product = await helpers.get_product_by_id(session, product_id, raise_if_not_found=True)
    return product


@router.get("/{product_id}/availability", response_model=ProductAvailability)
async def get_product_availability(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    quantity: int = Query(1, gt=0, description="Quantity to check availability for")
):
    """Get availability information for a specific product"""
    return await InventoryService.check_product_availability(session, product_id, quantity)


# ===== Search & Stats =====

@router.get("/search/suggestions")
async def get_search_suggestions(
    *,
    session: AsyncSession = Depends(get_session),
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions")
):
    """Get search suggestions for autocomplete"""
    suggestions = await helpers.search_product_suggestions(session, q, limit)
    return {"suggestions": suggestions}


@router.get("/stats/summary")
async def get_product_stats(
    *,
    session: AsyncSession = Depends(get_session)
):
    """Get product statistics summary"""
    stats = await helpers.get_product_statistics(session)
    return presenters.build_product_stats_response(stats)


# ===== Write Operations (CRUD) =====

@router.post("/", response_model=ProductRead)
async def create_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_in: ProductCreate,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Create new product"""
    product = await ProductService.create_product(
        session=session,
        product_in=product_in,
        shop_id=shop_id,
        commit=True
    )
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    product_in: ProductUpdate,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Update product"""
    product = await ProductService.update_product(
        session=session,
        product_id=product_id,
        product_in=product_in,
        shop_id=shop_id,
        commit=True
    )
    return product


@router.patch("/{product_id}/status", response_model=ProductRead)
async def toggle_product_status(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    enabled: bool,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Toggle product enabled/disabled status"""
    product = await ProductService.toggle_product_status(
        session=session,
        product_id=product_id,
        enabled=enabled,
        shop_id=shop_id,
        commit=True
    )
    return product


@router.delete("/{product_id}")
async def delete_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Delete product"""
    await ProductService.delete_product(
        session=session,
        product_id=product_id,
        shop_id=shop_id,
        commit=True
    )
    return {"message": "Product deleted successfully"}


# ===== Image Management =====

@router.post("/{product_id}/images", response_model=ProductImageRead)
async def create_product_image(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    image_in: ProductImageCreate,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Create a new product image"""
    image = await ProductService.create_product_image(
        session=session,
        product_id=product_id,
        image_in=image_in,
        shop_id=shop_id,
        commit=True
    )
    return image


@router.delete("/{product_id}/images/{image_id}")
async def delete_product_image(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    image_id: int,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Delete a product image"""
    await ProductService.delete_product_image(
        session=session,
        product_id=product_id,
        image_id=image_id,
        shop_id=shop_id,
        commit=True
    )
    return {"message": "Image deleted successfully"}
