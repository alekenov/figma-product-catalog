"""
Public Shops API endpoints for marketplace
Provides public access to shop information for customer-facing frontend
Does NOT require authentication
"""
from typing import List, Optional
from datetime import datetime, time as dt_time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from database import get_session
from models import (
    Shop, ShopPublicListItem, ShopPublicDetail,
    Product, ProductRead, City,
    CompanyReview
)

router = APIRouter()


def is_shop_open_now(shop: Shop) -> bool:
    """
    Check if shop is currently open based on working hours.

    Args:
        shop: Shop instance

    Returns:
        bool: True if shop is open now, False otherwise
    """
    now = datetime.now()
    current_time = now.time()
    is_weekend = now.weekday() >= 5  # Saturday=5, Sunday=6

    if is_weekend:
        if shop.weekend_closed:
            return False
        try:
            start = dt_time.fromisoformat(shop.weekend_start)
            end = dt_time.fromisoformat(shop.weekend_end)
            return start <= current_time <= end
        except ValueError:
            return False
    else:
        if shop.weekday_closed:
            return False
        try:
            start = dt_time.fromisoformat(shop.weekday_start)
            end = dt_time.fromisoformat(shop.weekday_end)
            return start <= current_time <= end
        except ValueError:
            return False


async def get_shop_rating_and_reviews(session: AsyncSession, shop_id: int) -> tuple[Optional[float], int]:
    """
    Calculate shop rating and review count.

    Args:
        session: Database session
        shop_id: Shop ID

    Returns:
        tuple: (average_rating, review_count)
    """
    # Get company reviews for this shop
    rating_query = select(
        func.avg(CompanyReview.rating).label('avg_rating'),
        func.count(CompanyReview.id).label('review_count')
    ).where(
        CompanyReview.shop_id == shop_id
    )

    result = await session.execute(rating_query)
    row = result.first()

    avg_rating = float(row.avg_rating) if row.avg_rating else None
    review_count = int(row.review_count) if row.review_count else 0

    return avg_rating, review_count


@router.get("/", response_model=List[ShopPublicListItem])
async def list_public_shops(
    *,
    session: AsyncSession = Depends(get_session),
    city: Optional[City] = Query(None, description="Filter by city"),
    skip: int = Query(0, ge=0, description="Number of shops to skip"),
    limit: int = Query(20, le=100, description="Maximum number of shops to return")
):
    """
    Get list of active shops for marketplace.
    Public endpoint - no authentication required.

    Returns shops with:
    - Basic info (name, city, phone, address)
    - Delivery settings
    - Rating and review count
    - Current open/closed status
    """
    query = select(Shop).where(Shop.is_active == True)

    if city:
        query = query.where(Shop.city == city)

    query = query.offset(skip).limit(limit).order_by(Shop.created_at.desc())

    result = await session.execute(query)
    shops = result.scalars().all()

    # Build response with computed fields
    shop_list = []
    for shop in shops:
        rating, review_count = await get_shop_rating_and_reviews(session, shop.id)
        is_open = is_shop_open_now(shop)

        shop_item = ShopPublicListItem.from_shop(
            shop=shop,
            rating=rating,
            review_count=review_count,
            is_open=is_open
        )
        shop_list.append(shop_item)

    return shop_list


@router.get("/{shop_id}", response_model=ShopPublicDetail)
async def get_shop_detail(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int
):
    """
    Get detailed information about a specific shop.
    Public endpoint - no authentication required.

    Returns:
    - Full shop information including working hours
    - Delivery settings
    - Rating and review count
    - Current open/closed status
    """
    query = select(Shop).where(
        Shop.id == shop_id,
        Shop.is_active == True
    )

    result = await session.execute(query)
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop with id {shop_id} not found or inactive"
        )

    rating, review_count = await get_shop_rating_and_reviews(session, shop_id)
    is_open = is_shop_open_now(shop)

    return ShopPublicDetail.from_shop(
        shop=shop,
        rating=rating,
        review_count=review_count,
        is_open=is_open
    )


@router.get("/{shop_id}/products", response_model=List[ProductRead])
async def get_shop_products(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int,
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200)
):
    """
    Get products for a specific shop.
    Public endpoint - no authentication required.

    Returns all enabled products for the shop.
    """
    # Verify shop exists and is active
    shop_query = select(Shop).where(
        Shop.id == shop_id,
        Shop.is_active == True
    )
    shop_result = await session.execute(shop_query)
    shop = shop_result.scalar_one_or_none()

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop with id {shop_id} not found or inactive"
        )

    # Get products for this shop
    query = select(Product).where(Product.shop_id == shop_id)

    # By default show only enabled products for public API
    if enabled is None:
        enabled = True

    if enabled is not None:
        query = query.where(Product.enabled == enabled)

    query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())

    result = await session.execute(query)
    products = result.scalars().all()

    return [ProductRead.model_validate(product) for product in products]
