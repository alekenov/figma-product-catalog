"""
Order Helpers - Reusable data loading utilities

Consolidates database queries to eliminate duplication.
Provides clean interfaces for loading orders with relations.
"""

from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException

from models import Order, OrderItem, OrderPhoto


async def load_order_items(session: AsyncSession, order_id: int) -> List[OrderItem]:
    """
    Load all items for an order.

    Args:
        session: Database session
        order_id: Order ID

    Returns:
        List of OrderItem instances
    """
    query = select(OrderItem).where(OrderItem.order_id == order_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def load_order_photos(session: AsyncSession, order_id: int) -> List[OrderPhoto]:
    """
    Load all photos for an order.

    Args:
        session: Database session
        order_id: Order ID

    Returns:
        List of OrderPhoto instances
    """
    query = select(OrderPhoto).where(OrderPhoto.order_id == order_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def load_order_with_relations(
    session: AsyncSession,
    order_id: Optional[int] = None,
    tracking_id: Optional[str] = None,
    order_number: Optional[str] = None,
    include_photos: bool = True
) -> Tuple[Order, List[OrderItem], List[OrderPhoto]]:
    """
    Load order with items and optionally photos.
    Supports lookup by ID, tracking_id, or order_number.

    Args:
        session: Database session
        order_id: Order ID (primary lookup)
        tracking_id: Tracking ID (alternative lookup)
        order_number: Order number (alternative lookup)
        include_photos: Whether to load photos

    Returns:
        Tuple of (order, items, photos)

    Raises:
        HTTPException: If order not found
    """
    # Load order
    if order_id:
        order = await session.get(Order, order_id)
        identifier = f"ID {order_id}"
    elif tracking_id:
        query = select(Order).where(Order.tracking_id == tracking_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        identifier = f"tracking ID {tracking_id}"
    elif order_number:
        query = select(Order).where(Order.orderNumber == order_number)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        identifier = f"order number {order_number}"
    else:
        raise ValueError("Must provide one of: order_id, tracking_id, or order_number")

    if not order:
        raise HTTPException(status_code=404, detail=f"Order with {identifier} not found")

    # Load items
    items = await load_order_items(session, order.id)

    # Load photos if requested
    photos = await load_order_photos(session, order.id) if include_photos else []

    return order, items, photos


async def get_order_by_tracking_id(session: AsyncSession, tracking_id: str) -> Order:
    """
    Get order by tracking ID.

    Args:
        session: Database session
        tracking_id: Tracking ID

    Returns:
        Order instance

    Raises:
        HTTPException: If order not found
    """
    query = select(Order).where(Order.tracking_id == tracking_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order with tracking ID {tracking_id} not found")

    return order


async def get_order_by_number(session: AsyncSession, order_number: str) -> Order:
    """
    Get order by order number.

    Args:
        session: Database session
        order_number: Order number

    Returns:
        Order instance

    Raises:
        HTTPException: If order not found
    """
    query = select(Order).where(Order.orderNumber == order_number)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_number} not found")

    return order
