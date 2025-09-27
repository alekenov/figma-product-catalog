from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from database import get_session
from models import (
    Product, ProductCreate, ProductRead, ProductUpdate, ProductType,
    ProductAvailability
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