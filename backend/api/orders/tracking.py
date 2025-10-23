"""
Orders Tracking Router - Public tracking endpoints

Handles public order tracking by phone, tracking ID, and order number.
Allows customers to view and update their orders without authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from database import get_session
from models import Order, OrderRead, OrderUpdate
from services.order_service import OrderService
from utils import normalize_phone_number

from .helpers import (
    load_order_with_relations,
    get_order_by_tracking_id,
    get_order_by_number
)
from .presenters import build_order_read, build_public_status_response

router = APIRouter()


@router.get("/by-phone/{phone}")
async def get_orders_by_phone(
    *,
    session: AsyncSession = Depends(get_session),
    phone: str = Path(..., description="Customer phone number"),
    shop_id: int = Query(..., description="Shop ID to filter orders")
):
    """
    Get all orders for a customer by phone number.
    Public endpoint used for customer order history.
    """
    # Normalize phone number
    from services.client_service import client_service
    normalized_phone = normalize_phone_number(phone)

    # Query orders for this phone and shop
    query = select(Order).options(
        selectinload(Order.items)
    ).where(
        Order.phone == normalized_phone,
        Order.shop_id == shop_id
    ).order_by(Order.created_at.desc())

    result = await session.execute(query)
    orders = result.scalars().all()

    # Build response with items
    return [
        build_order_read(order, order.items, [])
        for order in orders
    ]


@router.get("/by-tracking/{tracking_id}/status")
async def get_order_status_by_tracking(
    *,
    session: AsyncSession = Depends(get_session),
    tracking_id: str
):
    """
    Public order tracking endpoint - fetch order status by tracking ID.
    Used by OrderStatusPage for customer-facing order tracking.
    Uses secure 9-digit tracking ID instead of sequential order numbers.
    """
    order, items, photos = await load_order_with_relations(
        session, tracking_id=tracking_id, include_photos=True
    )
    return build_public_status_response(order, items, photos)


@router.put("/by-tracking/{tracking_id}", response_model=OrderRead)
async def update_order_by_tracking(
    *,
    session: AsyncSession = Depends(get_session),
    tracking_id: str,
    order_in: OrderUpdate,
    changed_by: str = Query(default="customer", description="Who is making the change: 'customer' or 'admin'")
):
    """
    Update order by tracking ID - used by customers on public tracking page.
    Allows customers to edit their order details before delivery.
    """
    # Get order by tracking ID
    order = await get_order_by_tracking_id(session, tracking_id)

    # Use centralized update method
    await OrderService.update_order_with_history(session, order, order_in, changed_by)

    # Return updated order with full relations
    return await OrderService.get_order_with_items(session, order.id)


@router.get("/by-number/{order_number}/status")
async def get_order_status_by_number(
    *,
    session: AsyncSession = Depends(get_session),
    order_number: str
):
    """
    Public order tracking endpoint - fetch order status by order number.
    Used by OrderStatusPage for customer-facing order tracking.
    DEPRECATED: Use /by-tracking/{tracking_id}/status instead for better security.
    """
    order, items, photos = await load_order_with_relations(
        session, order_number=order_number, include_photos=True
    )
    return build_public_status_response(order, items, photos)
