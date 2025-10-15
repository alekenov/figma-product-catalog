"""
Shop Settings Management API endpoints
Handles shop configuration, working hours, and delivery settings
Multi-tenancy: Each user manages their own shop
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import (
    Shop, ShopRead, ShopUpdate,
    WorkingHoursUpdate, DeliverySettingsUpdate,
    User, UserRole, City
)
from auth_utils import (
    get_current_active_user, require_director,
    require_manager_or_director, get_current_user_shop_id
)
from utils import tenge_to_kopecks, kopecks_to_tenge

router = APIRouter()


async def get_user_shop(session: AsyncSession, shop_id: int) -> Shop:
    """
    Get user's shop by shop_id.

    Args:
        session: Database session
        shop_id: Shop ID to retrieve

    Returns:
        Shop instance

    Raises:
        HTTPException: If shop not found
    """
    shop = await session.get(Shop, shop_id)

    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )

    return shop


@router.get("/settings/public")
async def get_public_shop_settings(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int
):
    """
    Get public shop settings without authentication.
    Used by customer-facing website for display purposes only.

    Args:
        shop_id: The shop ID to get public settings for
    """
    shop = await get_user_shop(session, shop_id)

    return {
        "shop_name": shop.name,
        "phone": shop.phone,
        "address": shop.address,
        "city": shop.city.value if shop.city else None,
        "weekday_hours": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
        "weekend_hours": f"{shop.weekend_start} - {shop.weekend_end}" if not shop.weekend_closed else "Closed",
        "weekday_closed": shop.weekday_closed,
        "weekend_closed": shop.weekend_closed,
        "delivery_cost_tenge": kopecks_to_tenge(shop.delivery_cost),
        "free_delivery_threshold_tenge": kopecks_to_tenge(shop.free_delivery_amount),
        "pickup_available": shop.pickup_available,
        "delivery_available": shop.delivery_available
    }


@router.get("/settings", response_model=ShopRead)
async def get_shop_settings(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """
    Get current shop settings for authenticated user's shop.
    Available to all authenticated users in the shop.
    """
    shop = await get_user_shop(session, shop_id)

    # Create response
    return ShopRead(
        id=shop.id,
        name=shop.name,
        owner_id=shop.owner_id,
        phone=shop.phone,
        address=shop.address,
        city=shop.city,
        weekday_start=shop.weekday_start,
        weekday_end=shop.weekday_end,
        weekday_closed=shop.weekday_closed,
        weekend_start=shop.weekend_start,
        weekend_end=shop.weekend_end,
        weekend_closed=shop.weekend_closed,
        delivery_cost=shop.delivery_cost,
        free_delivery_amount=shop.free_delivery_amount,
        pickup_available=shop.pickup_available,
        delivery_available=shop.delivery_available,
        created_at=shop.created_at,
        updated_at=shop.updated_at
    )


@router.put("/settings", response_model=ShopRead)
async def update_shop_settings(
    *,
    session: AsyncSession = Depends(get_session),
    shop_update: ShopUpdate,
    shop_id: int = Depends(get_current_user_shop_id),
    current_user: User = Depends(require_manager_or_director)
):
    """
    Update shop settings for authenticated user's shop.
    Requires director or manager role.
    """
    shop = await get_user_shop(session, shop_id)

    # Track old values for milestone detection
    old_name = shop.name
    old_city = shop.city

    update_data = shop_update.model_dump(exclude_unset=True)

    # Apply updates
    for field, value in update_data.items():
        if hasattr(shop, field):
            setattr(shop, field, value)

    await session.commit()
    await session.refresh(shop)

    # Analytics & Notifications
    try:
        from services import analytics, telegram_notifications

        # Check if name changed from default
        if old_name == "Мой магазин" and shop.name != "Мой магазин":
            if await analytics.mark_name_customized(session, shop_id):
                await telegram_notifications.notify_shop_name_changed(
                    shop_id=shop.id,
                    new_name=shop.name,
                    owner_name=current_user.name,
                    owner_phone=current_user.phone,
                    city=shop.city.value if shop.city else None
                )

        # Check if city was just added
        if old_city is None and shop.city is not None:
            await analytics.mark_city_added(session, shop_id)

        # Check if address was just added
        if shop.address and len(shop.address) > 0:
            await analytics.mark_address_added(session, shop_id)

        # Check onboarding completion
        is_onboarding_completed = await analytics.check_and_mark_onboarding_completed(session, shop_id)

        if is_onboarding_completed:
            # Send onboarding completion notification
            from datetime import datetime
            await telegram_notifications.notify_onboarding_completed(
                shop_id=shop.id,
                shop_name=shop.name,
                owner_name=current_user.name,
                owner_phone=current_user.phone,
                registration_time=shop.created_at,
                completion_time=datetime.utcnow()
            )

    except Exception as e:
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.error("shop_settings_notification_failed", error=str(e))

    # Return response
    return ShopRead(
        id=shop.id,
        name=shop.name,
        owner_id=shop.owner_id,
        phone=shop.phone,
        address=shop.address,
        city=shop.city,
        weekday_start=shop.weekday_start,
        weekday_end=shop.weekday_end,
        weekday_closed=shop.weekday_closed,
        weekend_start=shop.weekend_start,
        weekend_end=shop.weekend_end,
        weekend_closed=shop.weekend_closed,
        delivery_cost=shop.delivery_cost,
        free_delivery_amount=shop.free_delivery_amount,
        pickup_available=shop.pickup_available,
        delivery_available=shop.delivery_available,
        created_at=shop.created_at,
        updated_at=shop.updated_at
    )


@router.put("/working-hours", response_model=ShopRead)
async def update_working_hours(
    *,
    session: AsyncSession = Depends(get_session),
    working_hours: WorkingHoursUpdate,
    shop_id: int = Depends(get_current_user_shop_id),
    current_user: User = Depends(require_manager_or_director)
):
    """
    Update shop working hours for authenticated user's shop.
    Requires director or manager role.
    """
    shop = await get_user_shop(session, shop_id)

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
    if working_hours.weekday_start is not None:
        if not validate_time_format(working_hours.weekday_start):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekday_start format. Use HH:MM"
            )
        shop.weekday_start = working_hours.weekday_start

    if working_hours.weekday_end is not None:
        if not validate_time_format(working_hours.weekday_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekday_end format. Use HH:MM"
            )
        shop.weekday_end = working_hours.weekday_end

    if working_hours.weekday_closed is not None:
        shop.weekday_closed = working_hours.weekday_closed

    # Update weekend hours
    if working_hours.weekend_start is not None:
        if not validate_time_format(working_hours.weekend_start):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekend_start format. Use HH:MM"
            )
        shop.weekend_start = working_hours.weekend_start

    if working_hours.weekend_end is not None:
        if not validate_time_format(working_hours.weekend_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid weekend_end format. Use HH:MM"
            )
        shop.weekend_end = working_hours.weekend_end

    if working_hours.weekend_closed is not None:
        shop.weekend_closed = working_hours.weekend_closed

    await session.commit()
    await session.refresh(shop)

    return ShopRead(
        id=shop.id,
        name=shop.name,
        owner_id=shop.owner_id,
        phone=shop.phone,
        address=shop.address,
        city=shop.city,
        weekday_start=shop.weekday_start,
        weekday_end=shop.weekday_end,
        weekday_closed=shop.weekday_closed,
        weekend_start=shop.weekend_start,
        weekend_end=shop.weekend_end,
        weekend_closed=shop.weekend_closed,
        delivery_cost=shop.delivery_cost,
        free_delivery_amount=shop.free_delivery_amount,
        pickup_available=shop.pickup_available,
        delivery_available=shop.delivery_available,
        created_at=shop.created_at,
        updated_at=shop.updated_at
    )


@router.put("/delivery", response_model=ShopRead)
async def update_delivery_settings(
    *,
    session: AsyncSession = Depends(get_session),
    delivery_settings: DeliverySettingsUpdate,
    shop_id: int = Depends(get_current_user_shop_id),
    current_user: User = Depends(require_manager_or_director)
):
    """
    Update delivery settings for authenticated user's shop.
    Requires director or manager role.
    Accepts delivery costs in kopecks (as stored in DB).
    """
    shop = await get_user_shop(session, shop_id)

    # Validate delivery cost (already in kopecks)
    if delivery_settings.delivery_cost is not None:
        if delivery_settings.delivery_cost < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery cost cannot be negative"
            )
        shop.delivery_cost = delivery_settings.delivery_cost

    # Validate free delivery amount (already in kopecks)
    if delivery_settings.free_delivery_amount is not None:
        if delivery_settings.free_delivery_amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free delivery amount cannot be negative"
            )
        shop.free_delivery_amount = delivery_settings.free_delivery_amount

    # Update availability settings
    if delivery_settings.pickup_available is not None:
        shop.pickup_available = delivery_settings.pickup_available

    if delivery_settings.delivery_available is not None:
        shop.delivery_available = delivery_settings.delivery_available

    # Validate that at least one fulfillment method is available
    if not shop.pickup_available and not shop.delivery_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one fulfillment method (pickup or delivery) must be available"
        )

    await session.commit()
    await session.refresh(shop)

    return ShopRead(
        id=shop.id,
        name=shop.name,
        owner_id=shop.owner_id,
        phone=shop.phone,
        address=shop.address,
        city=shop.city,
        weekday_start=shop.weekday_start,
        weekday_end=shop.weekday_end,
        weekday_closed=shop.weekday_closed,
        weekend_start=shop.weekend_start,
        weekend_end=shop.weekend_end,
        weekend_closed=shop.weekend_closed,
        delivery_cost=shop.delivery_cost,
        free_delivery_amount=shop.free_delivery_amount,
        pickup_available=shop.pickup_available,
        delivery_available=shop.delivery_available,
        created_at=shop.created_at,
        updated_at=shop.updated_at
    )


@router.get("/working-hours")
async def get_working_hours(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int
):
    """
    Get shop working hours schedule (public endpoint).
    Used by customer-facing applications to display shop hours.

    Args:
        shop_id: Shop ID to get working hours for

    Returns:
        Working hours schedule for all days of the week
    """
    shop = await get_user_shop(session, shop_id)

    return {
        "monday": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
        "tuesday": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
        "wednesday": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
        "thursday": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
        "friday": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
        "saturday": f"{shop.weekend_start} - {shop.weekend_end}" if not shop.weekend_closed else "Closed",
        "sunday": f"{shop.weekend_start} - {shop.weekend_end}" if not shop.weekend_closed else "Closed",
        "weekday_closed": shop.weekday_closed,
        "weekend_closed": shop.weekend_closed
    }


@router.get("/hours/current")
async def get_current_status(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """
    Get current shop status (open/closed) based on current time.
    Available to all authenticated users in the shop.
    """
    from datetime import datetime, time
    import pytz

    shop = await get_user_shop(session, shop_id)

    # Get current time in Almaty timezone
    almaty_tz = pytz.timezone('Asia/Almaty')
    now = datetime.now(almaty_tz)
    current_time = now.time()
    is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6

    # Determine if shop is open
    is_open = False
    hours_info = {}

    if is_weekend:
        if not shop.weekend_closed:
            start_time = time.fromisoformat(shop.weekend_start)
            end_time = time.fromisoformat(shop.weekend_end)
            is_open = start_time <= current_time <= end_time

        hours_info = {
            "day_type": "weekend",
            "hours": f"{shop.weekend_start} - {shop.weekend_end}" if not shop.weekend_closed else "Closed",
            "closed": shop.weekend_closed
        }
    else:
        if not shop.weekday_closed:
            start_time = time.fromisoformat(shop.weekday_start)
            end_time = time.fromisoformat(shop.weekday_end)
            is_open = start_time <= current_time <= end_time

        hours_info = {
            "day_type": "weekday",
            "hours": f"{shop.weekday_start} - {shop.weekday_end}" if not shop.weekday_closed else "Closed",
            "closed": shop.weekday_closed
        }

    return {
        "is_open": is_open,
        "current_time": current_time.strftime("%H:%M"),
        "current_day": now.strftime("%A"),
        "shop_name": shop.name,
        "address": shop.address,
        "city": shop.city.value if shop.city else None,
        **hours_info
    }


@router.get("/delivery/calculate")
async def calculate_delivery_cost(
    *,
    session: AsyncSession = Depends(get_session),
    order_total_tenge: int,
    shop_id: int = Depends(get_current_user_shop_id)
):
    """
    Calculate delivery cost for given order total.
    Available to all authenticated users in the shop.
    """
    if order_total_tenge < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order total cannot be negative"
        )

    shop = await get_user_shop(session, shop_id)

    order_total_kopecks = tenge_to_kopecks(order_total_tenge)
    delivery_cost_kopecks = 0

    # Check if order qualifies for free delivery
    if order_total_kopecks >= shop.free_delivery_amount:
        delivery_cost_kopecks = 0
        free_delivery = True
    else:
        delivery_cost_kopecks = shop.delivery_cost
        free_delivery = False

    return {
        "order_total_tenge": order_total_tenge,
        "delivery_cost_tenge": kopecks_to_tenge(delivery_cost_kopecks),
        "free_delivery": free_delivery,
        "free_delivery_threshold_tenge": kopecks_to_tenge(shop.free_delivery_amount),
        "amount_needed_for_free_delivery_tenge": max(0, kopecks_to_tenge(shop.free_delivery_amount) - order_total_tenge),
        "pickup_available": shop.pickup_available,
        "delivery_available": shop.delivery_available
    }