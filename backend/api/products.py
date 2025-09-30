from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from database import get_session
from models import (
    Product, ProductCreate, ProductRead, ProductUpdate, ProductType,
    ProductAvailability, ProductDetailRead, ProductImage, ProductVariant,
    ProductRecipe, ProductAddon, ProductBundle, PickupLocation,
    ProductReview, CompanyReview, CompositionItemRead, ProductBundleItemRead,
    ReviewsAggregateRead, ReviewsBreakdownRead, City
)
from services.inventory_service import InventoryService

router = APIRouter()


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
):
    """Get list of products with filtering and search"""

    # Build query
    query = select(Product)

    # Apply filters
    if enabled_only:
        query = query.where(Product.enabled == True)

    if type:
        query = query.where(Product.type == type)

    if search:
        query = query.where(col(Product.name).ilike(f"%{search}%"))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    products = result.scalars().all()

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

    # Build base query for enabled products
    query = select(Product).where(Product.enabled == True)

    # Filter by city if provided
    if city:
        # Check if city exists in cities JSON array
        query = query.where(func.json_extract(Product.cities, '$').like(f'%{city.lower()}%'))

    # Filter by tags if provided
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        for tag in tag_list:
            query = query.where(func.json_extract(Product.tags, '$').like(f'%{tag}%'))

    # Get featured products
    featured_query = query.where(Product.is_featured == True).limit(limit)
    featured_result = await session.execute(featured_query)
    featured_products = featured_result.scalars().all()

    # Get all products to extract available tags
    all_products_result = await session.execute(
        select(Product).where(Product.enabled == True)
    )
    all_products = all_products_result.scalars().all()

    # Extract unique tags
    available_tags = set()
    for product in all_products:
        if product.tags:
            available_tags.update(product.tags)

    return {
        "featured": featured_products,
        "available_tags": sorted(list(available_tags)),
        "bestsellers": featured_products  # Same as featured for now
    }


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
    result = await session.execute(
        select(Product).where(Product.enabled == True)
    )
    products = result.scalars().all()

    # Extract unique tags
    tags = set()
    cities = set()
    prices = []

    for product in products:
        if product.tags:
            tags.update(product.tags)
        if product.cities:
            cities.update(product.cities)
        prices.append(product.price)

    # Calculate price range
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0

    return {
        "tags": sorted(list(tags)),
        "cities": sorted(list(cities)),
        "price_range": {
            "min": min_price,
            "max": max_price,
            "min_tenge": min_price // 100,
            "max_tenge": max_price // 100
        },
        "product_types": [t.value for t in ProductType]
    }


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
    from sqlalchemy.orm import selectinload

    # Load product with all relationships using eager loading
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.recipes).selectinload(ProductRecipe.warehouse_item)
        )
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Load images
    images_result = await session.execute(
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.order)
    )
    images = images_result.scalars().all()

    # Load variants (sizes)
    variants_result = await session.execute(
        select(ProductVariant)
        .where(ProductVariant.product_id == product_id)
        .where(ProductVariant.enabled == True)
        .order_by(ProductVariant.price)
    )
    variants = variants_result.scalars().all()

    # Load addons
    addons_result = await session.execute(
        select(ProductAddon)
        .where(ProductAddon.product_id == product_id)
        .where(ProductAddon.enabled == True)
    )
    addons = addons_result.scalars().all()

    # Load bundles (frequently bought together)
    bundles_result = await session.execute(
        select(ProductBundle, Product)
        .join(Product, ProductBundle.bundled_product_id == Product.id)
        .where(ProductBundle.main_product_id == product_id)
        .where(ProductBundle.enabled == True)
        .where(Product.enabled == True)
        .order_by(ProductBundle.display_order)
        .limit(5)
    )
    bundle_rows = bundles_result.all()

    frequently_bought = [
        ProductBundleItemRead(
            id=bundled_product.id,
            name=bundled_product.name,
            price=bundled_product.price,
            image=bundled_product.image
        )
        for _, bundled_product in bundle_rows
    ]

    # Build composition from recipes
    composition = [
        CompositionItemRead(
            id=recipe.warehouse_item.id,
            name=recipe.warehouse_item.name,
            quantity=recipe.quantity
        )
        for recipe in product.recipes
        if recipe.warehouse_item
    ]

    # Load pickup locations
    pickup_result = await session.execute(
        select(PickupLocation)
        .where(PickupLocation.enabled == True)
        .order_by(PickupLocation.display_order)
    )
    pickup_locations_data = pickup_result.scalars().all()

    # Format pickup locations as strings
    pickup_locations = [
        f"{loc.address}{f' ({loc.landmark})' if loc.landmark else ''}"
        for loc in pickup_locations_data
    ]

    # Load product reviews
    product_reviews_result = await session.execute(
        select(ProductReview)
        .where(ProductReview.product_id == product_id)
        .options(selectinload(ProductReview.photos))
        .order_by(ProductReview.created_at.desc())
        .limit(10)
    )
    product_reviews = product_reviews_result.scalars().all()

    # Calculate product review aggregates
    product_review_count = len(product_reviews)
    product_avg_rating = sum(r.rating for r in product_reviews) / product_review_count if product_review_count > 0 else 0.0

    # Rating breakdown
    product_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in product_reviews:
        product_breakdown[review.rating] += 1

    # Collect review photos
    product_review_photos = []
    for review in product_reviews:
        for photo in review.photos:
            product_review_photos.append(photo.url)

    # Load company reviews
    company_reviews_result = await session.execute(
        select(CompanyReview)
        .order_by(CompanyReview.created_at.desc())
        .limit(10)
    )
    company_reviews = company_reviews_result.scalars().all()

    # Calculate company review aggregates
    company_review_count = len(company_reviews)
    company_avg_rating = sum(r.rating for r in company_reviews) / company_review_count if company_review_count > 0 else 0.0

    # Company rating breakdown
    company_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in company_reviews:
        company_breakdown[review.rating] += 1

    # Build response
    return ProductDetailRead(
        id=product.id,
        name=product.name,
        price=product.price,
        type=product.type,
        description=product.description,
        image=product.image,
        enabled=product.enabled,
        is_featured=product.is_featured,
        rating=round(product_avg_rating, 1) if product_review_count > 0 else None,
        review_count=product_review_count,
        rating_count=product_review_count,  # Simplified: same as review_count
        images=images,
        variants=variants,
        composition=composition,
        addons=addons,
        frequently_bought=frequently_bought,
        pickup_locations=pickup_locations,
        reviews={
            "product": {
                "count": product_review_count,
                "average_rating": round(product_avg_rating, 1),
                "breakdown": product_breakdown,
                "photos": product_review_photos[:6],  # Limit to 6 photos
                "items": product_reviews[:5]  # Limit to 5 reviews initially
            },
            "company": {
                "count": company_review_count,
                "average_rating": round(company_avg_rating, 1),
                "breakdown": company_breakdown,
                "photos": [],  # Company reviews don't have photos
                "items": company_reviews[:5]  # Limit to 5 reviews initially
            }
        }
    )


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int
):
    """Get single product by ID"""
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
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


@router.post("/", response_model=ProductRead)
async def create_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_in: ProductCreate
):
    """Create new product"""

    # Create product instance
    product = Product.model_validate(product_in)

    # Add to session and commit
    session.add(product)
    await session.commit()
    await session.refresh(product)

    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    product_in: ProductUpdate
):
    """Update product"""

    # Get existing product
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update fields that were provided
    product_data = product_in.model_dump(exclude_unset=True)
    for field, value in product_data.items():
        setattr(product, field, value)

    # Commit changes
    await session.commit()
    await session.refresh(product)

    return product


@router.patch("/{product_id}/status", response_model=ProductRead)
async def toggle_product_status(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int,
    enabled: bool
):
    """Toggle product enabled/disabled status"""

    # Get existing product
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update enabled status
    product.enabled = enabled

    # Commit changes
    await session.commit()
    await session.refresh(product)

    return product


@router.delete("/{product_id}")
async def delete_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: int
):
    """Delete product"""

    # Get existing product
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete product
    await session.delete(product)
    await session.commit()

    return {"message": "Product deleted successfully"}


@router.get("/search/suggestions")
async def get_search_suggestions(
    *,
    session: AsyncSession = Depends(get_session),
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions")
):
    """Get search suggestions for autocomplete"""

    # Search for products with names similar to query
    query = select(Product.name).where(
        col(Product.name).ilike(f"%{q}%")
    ).where(Product.enabled == True).limit(limit)

    result = await session.execute(query)
    suggestions = result.scalars().all()

    return {"suggestions": suggestions}


@router.get("/stats/summary")
async def get_product_stats(
    *,
    session: AsyncSession = Depends(get_session)
):
    """Get product statistics summary"""

    # Single aggregating query for all statistics
    stats_query = select(
        func.count(Product.id).label("total"),
        func.sum(case((Product.enabled == True, 1), else_=0)).label("enabled"),
        func.sum(case((Product.type == ProductType.FLOWERS, 1), else_=0)).label("flowers"),
        func.sum(case((Product.type == ProductType.SWEETS, 1), else_=0)).label("sweets"),
        func.sum(case((Product.type == ProductType.FRUITS, 1), else_=0)).label("fruits"),
        func.sum(case((Product.type == ProductType.GIFTS, 1), else_=0)).label("gifts")
    )

    result = await session.execute(stats_query)
    stats = result.first()

    # Handle None values with defaults
    total = stats.total or 0
    enabled = stats.enabled or 0

    return {
        "total_products": total,
        "enabled_products": enabled,
        "disabled_products": total - enabled,
        "by_type": {
            ProductType.FLOWERS.value: stats.flowers or 0,
            ProductType.SWEETS.value: stats.sweets or 0,
            ProductType.FRUITS.value: stats.fruits or 0,
            ProductType.GIFTS.value: stats.gifts or 0
        }
    }