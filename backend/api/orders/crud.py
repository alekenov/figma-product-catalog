"""
Orders CRUD Router - Core CRUD operations and statistics

Handles order creation, retrieval, updates, deletion,
order items management, and dashboard statistics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from sqlmodel import select, col

from database import get_session
from models import (
    Order, OrderCreate, OrderCreateWithItems, OrderRead, OrderUpdate, OrderStatus,
    OrderItem, OrderItemCreate, OrderItemRead,
    OrderHistory, OrderPhoto, Product, User
)
from services.order_service import OrderService
from services.client_service import client_service
from services.inventory_service import InventoryService
from services.profile_builder_service import profile_builder_service
from auth_utils import get_current_user_shop_id, get_current_user
from utils import normalize_phone_number
from .presenters import build_order_read

router = APIRouter()


# Helper function for status parsing
def parse_order_status(status_str: Optional[str] = Query(None, description="Filter by order status (case-insensitive)")) -> Optional[OrderStatus]:
    """
    Parse and normalize order status parameter (case-insensitive).

    Accepts both uppercase and lowercase status values:
    - 'NEW' or 'new' → OrderStatus.NEW
    - 'PAID' or 'paid' → OrderStatus.PAID
    - etc.

    Args:
        status_str: Status string from query parameter

    Returns:
        OrderStatus enum value or None

    Raises:
        HTTPException: If status value is invalid
    """
    if not status_str:
        return None

    try:
        # Normalize to lowercase and create enum
        return OrderStatus(status_str.lower())
    except ValueError:
        # List valid status values for error message
        valid_statuses = ", ".join([s.value for s in OrderStatus])
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status '{status_str}'. Valid values: {valid_statuses}"
        )


@router.get("/", response_model=List[OrderRead])
async def get_orders(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to return"),
    status: Optional[OrderStatus] = Depends(parse_order_status),
    customer_phone: Optional[str] = Query(None, description="Filter by customer phone"),
    search: Optional[str] = Query(None, description="Search in customer name or order number"),
    assigned_to_me: bool = Query(False, description="Filter orders assigned to current user (as responsible or courier)"),
    assigned_to_id: Optional[int] = Query(None, description="Filter by assigned responsible person ID"),
    courier_id: Optional[int] = Query(None, description="Filter by assigned courier ID"),
):
    """
    Get list of orders with filtering (status filter is case-insensitive).

    Assignment filters:
    - assigned_to_me: Show orders where I'm either responsible or courier
    - assigned_to_id: Filter by specific responsible person
    - courier_id: Filter by specific courier
    """

    # Build query with eager loading of items
    query = select(Order).options(selectinload(Order.items))

    # CRITICAL: Filter by shop_id for multi-tenancy
    query = query.where(Order.shop_id == shop_id)

    # Apply filters
    if status:
        query = query.where(Order.status == status)

    if customer_phone:
        query = query.where(Order.phone == customer_phone)

    if search:
        query = query.where(
            col(Order.customerName).ilike(f"%{search}%") |
            col(Order.orderNumber).ilike(f"%{search}%")
        )

    # Assignment filters
    if assigned_to_me:
        # Show orders where current user is either responsible or courier
        query = query.where(
            (Order.assigned_to_id == current_user.id) |
            (Order.courier_id == current_user.id)
        )

    if assigned_to_id:
        query = query.where(Order.assigned_to_id == assigned_to_id)

    if courier_id:
        query = query.where(Order.courier_id == courier_id)

    # Order by creation date (newest first)
    query = query.order_by(Order.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query - items will be loaded automatically
    result = await session.execute(query)
    orders = result.scalars().all()

    # Create response models using pre-loaded items
    return [
        build_order_read(order, order.items, [])
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int = Path(..., ge=1, description="Order ID (must be positive)")
):
    """Get single order by ID with items and photos"""
    return await OrderService.get_order_with_items(session, order_id, shop_id)


@router.post("/", response_model=OrderRead)
async def create_order(
    order_in: OrderCreate,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Create new order without items"""

    # Auto-create or get existing client record for this shop
    _, client_created = await client_service.get_or_create_client(
        session,
        order_in.phone,
        shop_id,
        order_in.customerName
    )

    # Normalize phone number in order data
    order_in.phone = normalize_phone_number(order_in.phone)

    # Use OrderService for atomic order creation with shop_id
    order = await OrderService.create_simple_order(session, order_in, shop_id)

    # Return using the service method for consistent response formatting
    return await OrderService.get_order_with_items(session, order.id, shop_id)


@router.post("/with-items", response_model=OrderRead)
async def create_order_with_items(
    order_in: OrderCreateWithItems,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Create new order with items and availability validation"""

    # Auto-create or get existing client record for this shop
    _, client_created = await client_service.get_or_create_client(
        session,
        order_in.phone,
        shop_id,
        order_in.customerName
    )

    # Normalize phone number in order data
    order_in.phone = normalize_phone_number(order_in.phone)

    # Use OrderService for atomic order creation with items
    order = await OrderService.create_order_with_items(
        session, order_in, shop_id, order_in.check_availability
    )

    # Create Kaspi payment if payment_method is kaspi
    if order.payment_method == "kaspi":
        try:
            await OrderService.create_kaspi_payment_for_order(session, order)
        except Exception as e:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.error("kaspi_payment_creation_failed", order_id=order.id, error=str(e))
            # Continue even if payment creation fails

    # Update client profile (async, non-blocking)
    try:
        await profile_builder_service.update_client_profile_after_order(session, order)
    except Exception as e:
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.error("profile_update_failed", order_id=order.id, error=str(e))
        # Continue even if profile update fails

    # Analytics & Notifications (only for first order)
    try:
        from services import analytics, telegram_notifications
        from utils import kopecks_to_tenge

        # Check if this is the first order
        if await analytics.mark_first_order_received(session, shop_id):
            # Get shop and owner info for notification
            shop, owner = await analytics.get_shop_with_owner(session, shop_id)

            # Send first order notification
            await telegram_notifications.notify_first_order_received(
                shop_id=shop_id,
                shop_name=shop.name if shop else "Unknown",
                order_number=order.orderNumber,
                customer_name=order.customerName,
                customer_phone=order.phone,
                total_tenge=kopecks_to_tenge(order.total),
                delivery_address=order.delivery_address,
                owner_phone=owner.phone if owner else ""
            )

            # Check if onboarding is now complete
            await analytics.check_and_mark_onboarding_completed(session, shop_id)

    except Exception as e:
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.error("order_notification_failed", error=str(e))

    # Return using the service method for consistent response formatting
    return await OrderService.get_order_with_items(session, order.id, shop_id)


@router.put("/{order_id}", response_model=OrderRead)
async def update_order(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int,
    order_in: OrderUpdate,
    changed_by: str = Query(default="admin", description="Who is making the change: 'customer' or 'admin'")
):
    """Update order details with audit trail"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    # Use centralized update method
    await OrderService.update_order_with_history(session, order, order_in, changed_by)

    # Return updated order with full relations
    return await OrderService.get_order_with_items(session, order_id, shop_id)


@router.delete("/{order_id}")
async def delete_order(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int
):
    """Delete order and all its items"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    try:
        # Release any existing reservations first
        await InventoryService.release_reservations(session, order_id)

        # Delete related records explicitly (cascade may not be configured for all relations)

        # Delete OrderPhoto records
        photos_query = select(OrderPhoto).where(OrderPhoto.order_id == order_id)
        photos_result = await session.execute(photos_query)
        photos = photos_result.scalars().all()
        for photo in photos:
            await session.delete(photo)

        # Delete OrderHistory records
        history_query = select(OrderHistory).where(OrderHistory.order_id == order_id)
        history_result = await session.execute(history_query)
        history_records = history_result.scalars().all()
        for history in history_records:
            await session.delete(history)

        # Delete OrderItem records (should cascade, but delete explicitly to be safe)
        items_query = select(OrderItem).where(OrderItem.order_id == order_id)
        items_result = await session.execute(items_query)
        items = items_result.scalars().all()
        for item in items:
            await session.delete(item)

        # Finally delete the order itself
        await session.delete(order)
        await session.commit()

        return {"message": "Order deleted successfully"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete order: {str(e)}")


# ===============================
@router.post("/{order_id}/items", response_model=OrderItemRead)
async def add_order_item(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    product_id: int,
    quantity: int = 1,
    special_requests: Optional[str] = None
):
    """Add item to existing order"""

    # Check if order exists
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if product exists
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Calculate item total
    item_total = product.price * quantity

    # Create order item
    order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        product_name=product.name,
        product_price=product.price,
        quantity=quantity,
        item_total=item_total,
        special_requests=special_requests
    )

    session.add(order_item)

    # Update order totals
    order.subtotal += item_total
    order.total = order.subtotal + order.delivery_cost

    await session.commit()
    await session.refresh(order_item)

    return order_item


# ===============================
@router.get("/stats/dashboard")
async def get_order_dashboard_stats(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id)
):
    """Get order statistics for admin dashboard"""

    # Count orders by status for this shop
    status_stats = {}
    for status in OrderStatus:
        status_query = select(Order.id).where(Order.status == status).where(Order.shop_id == shop_id)
        status_result = await session.execute(status_query)
        status_stats[status.value] = len(status_result.all())

    # Count today's orders for this shop
    today = datetime.now().date()
    today_query = select(Order.id).where(func.date(Order.created_at) == today).where(Order.shop_id == shop_id)
    today_result = await session.execute(today_query)
    today_count = len(today_result.all())

    # Calculate today's revenue for this shop
    today_revenue_query = select(Order.total).where(
        func.date(Order.created_at) == today
    ).where(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED])).where(Order.shop_id == shop_id)
    today_revenue_result = await session.execute(today_revenue_query)
    today_revenue = sum(today_revenue_result.scalars().all())

    return {
        "orders_by_status": status_stats,
        "orders_today": today_count,
        "revenue_today": today_revenue,
        "total_orders": sum(status_stats.values())
    }


# ===============================
