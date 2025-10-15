"""
Analytics Service for tracking shop milestones and sending notifications.

Handles:
- Checking if milestone is reached for first time
- Updating milestone flags in database
- Triggering appropriate Telegram notifications
"""
from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.analytics import ShopMilestone
from models.shop import Shop
from models.products import Product
from core.logging import get_logger

logger = get_logger(__name__)


async def get_or_create_milestone(session: AsyncSession, shop_id: int) -> ShopMilestone:
    """
    Get existing milestone record or create new one for shop.

    Args:
        session: Database session
        shop_id: Shop ID

    Returns:
        ShopMilestone: Milestone record
    """
    query = select(ShopMilestone).where(ShopMilestone.shop_id == shop_id)
    result = await session.execute(query)
    milestone = result.scalar_one_or_none()

    if not milestone:
        milestone = ShopMilestone(shop_id=shop_id)
        session.add(milestone)
        await session.flush()
        logger.info("milestone_created", shop_id=shop_id)

    return milestone


async def mark_name_customized(session: AsyncSession, shop_id: int) -> bool:
    """
    Mark shop name as customized (changed from default).

    Returns:
        bool: True if this is first time (should notify), False if already marked
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.name_customized:
        return False  # Already notified

    milestone.name_customized = True
    milestone.name_customized_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="name_customized")
    return True


async def mark_city_added(session: AsyncSession, shop_id: int) -> bool:
    """
    Mark city as added to shop settings.

    Returns:
        bool: True if this is first time, False if already marked
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.city_added:
        return False

    milestone.city_added = True
    milestone.city_added_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="city_added")
    return True


async def mark_address_added(session: AsyncSession, shop_id: int) -> bool:
    """
    Mark address as added to shop settings.

    Returns:
        bool: True if this is first time, False if already marked
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.address_added:
        return False

    milestone.address_added = True
    milestone.address_added_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="address_added")
    return True


async def mark_first_product_added(session: AsyncSession, shop_id: int) -> bool:
    """
    Mark first product as added.

    Returns:
        bool: True if this is first product (should notify), False if already had products
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.first_product_added:
        return False  # Already notified

    milestone.first_product_added = True
    milestone.first_product_added_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="first_product_added")
    return True


async def mark_shop_opened(session: AsyncSession, shop_id: int) -> bool:
    """
    Mark shop as opened (is_open=true).

    Returns:
        bool: True if this is first time shop opened, False if already marked
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.shop_opened:
        return False

    milestone.shop_opened = True
    milestone.shop_opened_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="shop_opened")
    return True


async def mark_first_order_received(session: AsyncSession, shop_id: int) -> bool:
    """
    Mark first order as received.

    Returns:
        bool: True if this is first order (should notify), False if already had orders
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.first_order_received:
        return False  # Already notified

    milestone.first_order_received = True
    milestone.first_order_received_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="first_order_received")
    return True


async def check_and_mark_onboarding_completed(session: AsyncSession, shop_id: int) -> bool:
    """
    Check if all onboarding steps are completed and mark if true.

    Onboarding steps:
    - Name customized (not "Мой магазин")
    - City added
    - At least one product added
    - Shop opened (is_open=true)

    Returns:
        bool: True if just completed onboarding (should notify), False otherwise
    """
    milestone = await get_or_create_milestone(session, shop_id)

    if milestone.onboarding_completed:
        return False  # Already completed

    # Check all conditions
    if not (milestone.name_customized and
            milestone.city_added and
            milestone.first_product_added and
            milestone.shop_opened):
        return False  # Not all steps done yet

    # Mark as completed
    milestone.onboarding_completed = True
    milestone.onboarding_completed_at = datetime.utcnow()
    session.add(milestone)
    await session.commit()

    logger.info("milestone_achieved", shop_id=shop_id, milestone="onboarding_completed")
    return True


async def get_product_count(session: AsyncSession, shop_id: int) -> int:
    """Get total product count for shop"""
    query = select(Product).where(Product.shop_id == shop_id)
    result = await session.execute(query)
    products = result.scalars().all()
    return len(products)


async def get_shop_with_owner(session: AsyncSession, shop_id: int):
    """Get shop with owner information for notifications"""
    from models.users import User

    query = select(Shop).where(Shop.id == shop_id)
    result = await session.execute(query)
    shop = result.scalar_one_or_none()

    if not shop:
        return None, None

    owner_query = select(User).where(User.id == shop.owner_id)
    owner_result = await session.execute(owner_query)
    owner = owner_result.scalar_one_or_none()

    return shop, owner
