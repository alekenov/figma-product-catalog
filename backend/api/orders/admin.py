"""
Orders Admin Router - Admin endpoints without JWT token

Provides admin access to orders using Telegram user ID verification.
Used by Admin Telegram Bot for staff members.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from database import get_session
from models import (
    Order, OrderRead, OrderStatus, OrderItem,
    Client, User, UserRole
)
from .presenters import build_order_read

router = APIRouter()


@router.get("/admin/by-telegram", response_model=List[OrderRead])
async def list_orders_by_telegram_admin(
    *,
    session: AsyncSession = Depends(get_session),
    telegram_user_id: str = Query(..., description="Telegram user ID for authorization"),
    shop_id: int = Query(..., description="Shop ID"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    limit: int = Query(20, ge=1, le=100, description="Number of orders to return"),
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
):
    """
    List all orders for shop (admin access via Telegram).

    No JWT token required - uses telegram_user_id for staff verification.

    Authorization flow:
    1. Find Client by telegram_user_id + shop_id
    2. Check if client.phone belongs to User with staff role (DIRECTOR, MANAGER, ADMIN)
    3. If verified → return ALL orders for shop_id
    4. If not verified → 403 Forbidden

    Args:
        telegram_user_id: Telegram user ID from bot
        shop_id: Shop ID to list orders from
        status: Optional status filter (NEW, PAID, etc.)
        limit: Max orders to return
        skip: Offset for pagination

    Returns:
        List of orders for the shop

    Raises:
        404: User not found in system
        403: User is not staff member
    """
    # 1. Find Client by telegram_user_id
    result = await session.execute(
        select(Client)
        .where(Client.telegram_user_id == telegram_user_id)
        .where(Client.shop_id == shop_id)
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"User with telegram_user_id={telegram_user_id} not found in shop {shop_id}"
        )

    # 2. Check if phone belongs to User with staff role
    result = await session.execute(
        select(User)
        .where(User.phone == client.phone)
        .where(User.shop_id == shop_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=403,
            detail="Phone number not registered as staff member"
        )

    # Check user role - allow DIRECTOR, MANAGER, ADMIN
    staff_roles = [UserRole.DIRECTOR, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPERADMIN]
    if user.role not in staff_roles:
        raise HTTPException(
            status_code=403,
            detail=f"User role {user.role.value} is not authorized for admin access. Required: DIRECTOR, MANAGER, or ADMIN"
        )

    # 3. Build query for ALL orders in this shop
    query = (
        select(Order)
        .where(Order.shop_id == shop_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.responsible_person),
            selectinload(Order.courier)
        )
    )

    # Apply status filter if provided
    if status:
        try:
            order_status = OrderStatus(status.lower())
            query = query.where(Order.status == order_status)
        except ValueError:
            valid_statuses = ", ".join([s.value for s in OrderStatus])
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status '{status}'. Valid values: {valid_statuses}"
            )

    # Apply pagination and ordering
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    orders = result.scalars().all()

    # Build response using presenter
    return [build_order_read(order) for order in orders]
