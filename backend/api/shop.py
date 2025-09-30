"""
Shop Settings Management API endpoints
Handles shop configuration, working hours, and delivery settings
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import (
    ShopSettings, ShopSettingsRead, ShopSettingsUpdate,
    User, UserRole, City
)
from auth_utils import (
    get_current_active_user, require_director,
    require_manager_or_director
)
from utils import tenge_to_kopecks, kopecks_to_tenge

router = APIRouter()


async def get_or_create_shop_settings(session: AsyncSession) -> ShopSettings:
    """Get shop settings or create default ones if none exist."""
    query = select(ShopSettings).limit(1)
    result = await session.execute(query)
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings
        settings = ShopSettings(
            shop_name="Цветы Казахстан",
            address="г. Алматы, ул. Абая 123",
            city=City.ALMATY,
            weekday_start="09:00",
            weekday_end="18:00",
            weekend_start="10:00",
            weekend_end="17:00",
            delivery_cost=tenge_to_kopecks(1500),  # 1500 tenge
            free_delivery_amount=tenge_to_kopecks(10000),  # 10000 tenge
            pickup_available=True,
            delivery_available=True
        )
        session.add(settings)
        await session.commit()
        await session.refresh(settings)

    return settings


@router.get("/settings/public")
async def get_public_shop_settings(
    *,
    session: AsyncSession = Depends(get_session)
):
    """
    Get public shop settings without authentication.
    Used by customer-facing website for display purposes only.
    """
    settings = await get_or_create_shop_settings(session)

    return {
        "shop_name": settings.shop_name,
        "address": settings.address,
        "city": settings.city.value if settings.city else None,
        "weekday_hours": f"{settings.weekday_start} - {settings.weekday_end}" if not settings.weekday_closed else "Closed",
        "weekend_hours": f"{settings.weekend_start} - {settings.weekend_end}" if not settings.weekend_closed else "Closed",
        "weekday_closed": settings.weekday_closed,
        "weekend_closed": settings.weekend_closed,
        "delivery_cost_tenge": kopecks_to_tenge(settings.delivery_cost),
        "free_delivery_threshold_tenge": kopecks_to_tenge(settings.free_delivery_amount),
        "pickup_available": settings.pickup_available,
        "delivery_available": settings.delivery_available
    }


@router.get("/settings", response_model=ShopSettingsRead)
async def get_shop_settings(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current shop settings
    Available to all authenticated users
    """
    settings = await get_or_create_shop_settings(session)

    # Create response with tenge values
    return ShopSettingsRead(
        id=settings.id,
        shop_name=settings.shop_name,
        address=settings.address,
        city=settings.city,
        weekday_start=settings.weekday_start,
        weekday_end=settings.weekday_end,
        weekday_closed=settings.weekday_closed,
        weekend_start=settings.weekend_start,
        weekend_end=settings.weekend_end,
        weekend_closed=settings.weekend_closed,
        delivery_cost=settings.delivery_cost,
        free_delivery_amount=settings.free_delivery_amount,
        pickup_available=settings.pickup_available,
        delivery_available=settings.delivery_available,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )


@router.put("/settings", response_model=ShopSettingsRead)
async def update_shop_settings(
    *,
    session: AsyncSession = Depends(get_session),
    settings_update: ShopSettingsUpdate,
    current_user: User = Depends(require_director)
):
    """
    Update shop settings
    Requires director role
    """
    settings = await get_or_create_shop_settings(session)
    update_data = settings_update.model_dump(exclude_unset=True)

    # Handle tenge to kopecks conversions
    if "delivery_cost_tenge" in update_data:
        update_data["delivery_cost"] = tenge_to_kopecks(update_data.pop("delivery_cost_tenge"))

    if "free_delivery_amount_tenge" in update_data:
        update_data["free_delivery_amount"] = tenge_to_kopecks(update_data.pop("free_delivery_amount_tenge"))

    # Apply updates
    for field, value in update_data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)

    await session.commit()
    await session.refresh(settings)

    # Return response with tenge values
    return ShopSettingsRead(
        id=settings.id,
        shop_name=settings.shop_name,
        address=settings.address,
        city=settings.city,
        weekday_start=settings.weekday_start,
        weekday_end=settings.weekday_end,
        weekday_closed=settings.weekday_closed,
        weekend_start=settings.weekend_start,
        weekend_end=settings.weekend_end,
        weekend_closed=settings.weekend_closed,
        delivery_cost=settings.delivery_cost,
        free_delivery_amount=settings.free_delivery_amount,
        pickup_available=settings.pickup_available,
        delivery_available=settings.delivery_available,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )


@router.put("/working-hours", response_model=ShopSettingsRead)
async def update_working_hours(
    *,
    session: AsyncSession = Depends(get_session),
    weekday_start: Optional[str] = None,
    weekday_end: Optional[str] = None,
    weekday_closed: Optional[bool] = None,
    weekend_start: Optional[str] = None,
    weekend_end: Optional[str] = None,
    weekend_closed: Optional[bool] = None,
    current_user: User = Depends(require_director)
):
    """
    Update shop working hours
    Requires director role
    """
    settings = await get_or_create_shop_settings(session)

    # Validate time format (HH:MM)
    def validate_time_format(time_str: str) -> bool:
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    # Update weekday hours
    if weekday_start is not None:
        if not validate_time_format(weekday_start):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekday_start format. Use HH:MM"
            )
        settings.weekday_start = weekday_start

    if weekday_end is not None:
        if not validate_time_format(weekday_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekday_end format. Use HH:MM"
            )
        settings.weekday_end = weekday_end

    if weekday_closed is not None:
        settings.weekday_closed = weekday_closed

    # Update weekend hours
    if weekend_start is not None:
        if not validate_time_format(weekend_start):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekend_start format. Use HH:MM"
            )
        settings.weekend_start = weekend_start

    if weekend_end is not None:
        if not validate_time_format(weekend_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekend_end format. Use HH:MM"
            )
        settings.weekend_end = weekend_end

    if weekend_closed is not None:
        settings.weekend_closed = weekend_closed

    await session.commit()
    await session.refresh(settings)

    return ShopSettingsRead(
        id=settings.id,
        shop_name=settings.shop_name,
        address=settings.address,
        city=settings.city,
        weekday_start=settings.weekday_start,
        weekday_end=settings.weekday_end,
        weekday_closed=settings.weekday_closed,
        weekend_start=settings.weekend_start,
        weekend_end=settings.weekend_end,
        weekend_closed=settings.weekend_closed,
        delivery_cost=settings.delivery_cost,
        free_delivery_amount=settings.free_delivery_amount,
        pickup_available=settings.pickup_available,
        delivery_available=settings.delivery_available,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )


@router.put("/delivery", response_model=ShopSettingsRead)
async def update_delivery_settings(
    *,
    session: AsyncSession = Depends(get_session),
    delivery_cost_tenge: Optional[int] = None,
    free_delivery_amount_tenge: Optional[int] = None,
    pickup_available: Optional[bool] = None,
    delivery_available: Optional[bool] = None,
    current_user: User = Depends(require_director)
):
    """
    Update delivery settings
    Requires director role
    """
    settings = await get_or_create_shop_settings(session)

    # Validate delivery cost
    if delivery_cost_tenge is not None:
        if delivery_cost_tenge < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery cost cannot be negative"
            )
        settings.delivery_cost = tenge_to_kopecks(delivery_cost_tenge)

    # Validate free delivery amount
    if free_delivery_amount_tenge is not None:
        if free_delivery_amount_tenge < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free delivery amount cannot be negative"
            )
        settings.free_delivery_amount = tenge_to_kopecks(free_delivery_amount_tenge)

    # Update availability settings
    if pickup_available is not None:
        settings.pickup_available = pickup_available

    if delivery_available is not None:
        settings.delivery_available = delivery_available

    # Validate that at least one fulfillment method is available
    if not settings.pickup_available and not settings.delivery_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one fulfillment method (pickup or delivery) must be available"
        )

    await session.commit()
    await session.refresh(settings)

    return ShopSettingsRead(
        id=settings.id,
        shop_name=settings.shop_name,
        address=settings.address,
        city=settings.city,
        weekday_start=settings.weekday_start,
        weekday_end=settings.weekday_end,
        weekday_closed=settings.weekday_closed,
        weekend_start=settings.weekend_start,
        weekend_end=settings.weekend_end,
        weekend_closed=settings.weekend_closed,
        delivery_cost=settings.delivery_cost,
        free_delivery_amount=settings.free_delivery_amount,
        pickup_available=settings.pickup_available,
        delivery_available=settings.delivery_available,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )


@router.get("/hours/current")
async def get_current_status(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current shop status (open/closed) based on current time
    Available to all authenticated users
    """
    from datetime import datetime, time
    import pytz

    settings = await get_or_create_shop_settings(session)

    # Get current time in Almaty timezone
    almaty_tz = pytz.timezone('Asia/Almaty')
    now = datetime.now(almaty_tz)
    current_time = now.time()
    is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6

    # Determine if shop is open
    is_open = False
    hours_info = {}

    if is_weekend:
        if not settings.weekend_closed:
            start_time = time.fromisoformat(settings.weekend_start)
            end_time = time.fromisoformat(settings.weekend_end)
            is_open = start_time <= current_time <= end_time

        hours_info = {
            "day_type": "weekend",
            "hours": f"{settings.weekend_start} - {settings.weekend_end}" if not settings.weekend_closed else "Closed",
            "closed": settings.weekend_closed
        }
    else:
        if not settings.weekday_closed:
            start_time = time.fromisoformat(settings.weekday_start)
            end_time = time.fromisoformat(settings.weekday_end)
            is_open = start_time <= current_time <= end_time

        hours_info = {
            "day_type": "weekday",
            "hours": f"{settings.weekday_start} - {settings.weekday_end}" if not settings.weekday_closed else "Closed",
            "closed": settings.weekday_closed
        }

    return {
        "is_open": is_open,
        "current_time": current_time.strftime("%H:%M"),
        "current_day": now.strftime("%A"),
        "shop_name": settings.shop_name,
        "address": settings.address,
        "city": settings.city.value,
        **hours_info
    }


@router.get("/delivery/calculate")
async def calculate_delivery_cost(
    *,
    session: AsyncSession = Depends(get_session),
    order_total_tenge: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate delivery cost for given order total
    Available to all authenticated users
    """
    if order_total_tenge < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order total cannot be negative"
        )

    settings = await get_or_create_shop_settings(session)

    order_total_kopecks = tenge_to_kopecks(order_total_tenge)
    delivery_cost_kopecks = 0

    # Check if order qualifies for free delivery
    if order_total_kopecks >= settings.free_delivery_amount:
        delivery_cost_kopecks = 0
        free_delivery = True
    else:
        delivery_cost_kopecks = settings.delivery_cost
        free_delivery = False

    return {
        "order_total_tenge": order_total_tenge,
        "delivery_cost_tenge": kopecks_to_tenge(delivery_cost_kopecks),
        "free_delivery": free_delivery,
        "free_delivery_threshold_tenge": kopecks_to_tenge(settings.free_delivery_amount),
        "amount_needed_for_free_delivery_tenge": max(0, kopecks_to_tenge(settings.free_delivery_amount) - order_total_tenge),
        "pickup_available": settings.pickup_available,
        "delivery_available": settings.delivery_available
    }