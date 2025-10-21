"""
Orders Router - Declarative API endpoints

Consolidates all order-related endpoints with clean separation of concerns.
Uses services for business logic, helpers for data loading, and presenters for formatting.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from sqlmodel import select, col
import httpx

from database import get_session
from models import (
    Order, OrderCreate, OrderCreateWithItems, OrderRead, OrderUpdate, OrderStatus,
    OrderItem, OrderItemCreate, OrderItemRead,
    OrderHistory, OrderHistoryRead,
    OrderPhoto, OrderPhotoRead,
    Product, ProductRecipe, WarehouseItem, WarehouseOperation, WarehouseOperationType,
    OrderReservation, OrderReservationCreate,
    OrderItemRequest, ProductAvailability, AvailabilityResponse,
    Shop, User, UserRole
)
from services.inventory_service import InventoryService
from services.client_service import client_service
from services.order_service import OrderService
from services.profile_builder_service import profile_builder_service
from auth_utils import get_current_user_shop_id, get_current_user
from utils import normalize_phone_number

from .helpers import (
    load_order_items, load_order_photos, load_order_with_relations,
    get_order_by_tracking_id, get_order_by_number
)
from .presenters import (
    map_status_to_frontend, format_delivery_datetime, format_delivery_type,
    build_order_read, build_public_status_response
)

router = APIRouter()


# ===============================
# Helper Functions
# ===============================

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


# ===============================
# Group 1: CRUD Operations
# ===============================

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
# Group 2: Public Tracking Endpoints
# ===============================

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


# ===============================
# Group 3: Status & History Management
# ===============================

@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int,
    status: OrderStatus,
    notes: Optional[str] = None
):
    """Update order status with automatic warehouse deduction for assembled orders"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    old_status = order.status

    # Begin transaction
    try:
        # Handle status transitions with reservation logic
        if status == OrderStatus.ASSEMBLED and old_status != OrderStatus.ASSEMBLED:
            # Convert reservations to actual deductions (without committing - let router control transaction)
            await InventoryService.convert_reservations_to_deductions(session, order.id, commit=False)
        elif status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
            # Release reservations for cancelled orders
            await InventoryService.release_reservations(session, order.id)

        # Update status and notes
        order.status = status
        if notes:
            order.notes = notes

        # Commit changes (now includes both inventory operations and status update)
        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Use service method to properly load order with all relationships
        return await OrderService.get_order_with_items(session, order.id, shop_id)

    except Exception as e:
        # Rollback transaction on any error
        await session.rollback()
        if "insufficient stock" in str(e).lower():
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")


class CancelRequest(BaseModel):
    """Request model for order cancellation"""
    reason: str = Field(..., description="Reason for cancellation")


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    cancel_data: CancelRequest
):
    """
    Cancel an order by customer or admin.

    - Changes status to CANCELLED
    - Releases inventory reservations
    - Creates order history entry
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if order can be cancelled (only new, accepted, assembled can be cancelled)
    if order.status not in [OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.ASSEMBLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status {order.status.value}"
        )

    try:
        # Release reservations (handle case when no reservations exist)
        try:
            await InventoryService.release_reservations(session, order.id)
        except Exception as reservation_error:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.warning("reservation_release_failed", order_id=order.id, error=str(reservation_error))
            # Continue with cancellation even if reservation release fails

        # Update status
        old_status = order.status
        order.status = OrderStatus.CANCELLED
        if cancel_data.reason:
            order.notes = f"Cancelled: {cancel_data.reason}"

        # Create history entry
        history = OrderHistory(
            order_id=order_id,
            field_name="status",
            old_value=old_status.value,
            new_value=f"cancelled (Reason: {cancel_data.reason})" if cancel_data.reason else "cancelled",
            changed_by="customer"
        )
        session.add(history)

        await session.commit()
        session.expunge_all()

        # Return updated order (use order's shop_id for fetching)
        return await OrderService.get_order_with_items(session, order.id, order.shop_id)

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.error("order_cancellation_failed", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")


@router.get("/{order_id}/history", response_model=list[OrderHistoryRead])
async def get_order_history(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Get change history for an order"""

    # Verify order exists
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Query history records
    statement = select(OrderHistory).where(
        OrderHistory.order_id == order_id
    ).order_by(OrderHistory.changed_at.desc())

    result = await session.execute(statement)
    history_records = result.scalars().all()

    return history_records


# ===============================
# Group 4: Order Items Management
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
# Group 5: Warehouse & Availability
# ===============================

@router.post("/check-availability", response_model=AvailabilityResponse)
async def check_order_availability(
    *,
    session: AsyncSession = Depends(get_session),
    order_items: List[OrderItemRequest]
):
    """Check availability for order items before creating order"""
    return await InventoryService.check_batch_availability(session, order_items)


@router.post("/preview")
async def preview_order(
    *,
    session: AsyncSession = Depends(get_session),
    order_items: List[OrderItemRequest]
):
    """
    Preview cart items before checkout - validates inventory and calculates totals.
    Used by frontend CartPage before actual order creation.
    """
    # Check availability
    availability = await InventoryService.check_batch_availability(session, order_items)

    # Calculate estimated total
    estimated_total = 0
    for item_request in order_items:
        product = await session.get(Product, item_request.product_id)
        if product:
            estimated_total += product.price * item_request.quantity

    return {
        "available": availability.available,
        "items": [item.model_dump() for item in availability.items],
        "warnings": availability.warnings,
        "estimated_total": estimated_total
    }


# ===============================
# Group 8: Public Marketplace Endpoints
# ===============================

@router.post("/public/preview")
async def preview_order_public(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Query(..., description="Shop ID for the order"),
    order_items: List[OrderItemRequest]
):
    """
    Public marketplace endpoint - Preview cart items before checkout.
    No authentication required - used by anonymous customers browsing the marketplace.

    Validates:
    - Product availability
    - Shop delivery settings
    - Total calculations
    """
    # Verify shop exists and is active
    shop_query = select(Shop).where(Shop.id == shop_id, Shop.is_active == True)
    shop_result = await session.execute(shop_query)
    shop = shop_result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail=f"Shop with id {shop_id} not found or inactive")

    # Check availability (products must belong to this shop)
    availability = await InventoryService.check_batch_availability(session, order_items)

    # Calculate subtotal and validate products belong to shop
    subtotal = 0
    for item_request in order_items:
        product = await session.get(Product, item_request.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_request.product_id} not found")

        # Verify product belongs to the specified shop
        if product.shop_id != shop_id:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item_request.product_id} does not belong to shop {shop_id}"
            )

        subtotal += product.price * item_request.quantity

    # Calculate delivery cost from shop settings
    from utils import kopecks_to_tenge
    delivery_cost_tenge = kopecks_to_tenge(shop.delivery_cost)

    # Check if free delivery applies
    free_delivery_threshold_tenge = kopecks_to_tenge(shop.free_delivery_amount)
    if subtotal >= free_delivery_threshold_tenge:
        delivery_cost_tenge = 0

    # Calculate total
    total = subtotal + delivery_cost_tenge

    return {
        "available": availability.available,
        "items": [item.model_dump() for item in availability.items],
        "warnings": availability.warnings,
        "subtotal": subtotal,
        "delivery_cost": delivery_cost_tenge,
        "free_delivery_threshold": free_delivery_threshold_tenge,
        "free_delivery_applied": subtotal >= free_delivery_threshold_tenge,
        "total": total,
        "shop": {
            "id": shop.id,
            "name": shop.name,
            "delivery_available": shop.delivery_available,
            "pickup_available": shop.pickup_available
        }
    }


@router.post("/public/create", response_model=OrderRead)
async def create_order_public(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Query(..., description="Shop ID for the order"),
    order_in: OrderCreateWithItems
):
    """
    Public marketplace endpoint - Create order for anonymous customer.
    No authentication required - allows customers to place orders without registration.

    Process:
    1. Validates shop exists and is active
    2. Creates/retrieves client record
    3. Validates product availability
    4. Creates order with items
    5. Returns order with tracking ID for customer tracking
    """
    # Verify shop exists and is active
    shop_query = select(Shop).where(Shop.id == shop_id, Shop.is_active == True)
    shop_result = await session.execute(shop_query)
    shop = shop_result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail=f"Shop with id {shop_id} not found or inactive")

    # Validate all products belong to this shop
    for item in order_in.items:
        product = await session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.shop_id != shop_id:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} does not belong to shop {shop_id}"
            )

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

    # DEBUG: Log payment method details
    from core.logging import get_logger
    logger = get_logger(__name__)
    logger.info(
        "public_order_created_checking_payment_method",
        order_id=order.id,
        payment_method=order.payment_method,
        payment_method_type=type(order.payment_method).__name__,
        payment_method_repr=repr(order.payment_method),
        is_kaspi_exact=order.payment_method == "kaspi",
        is_kaspi_lower=str(order.payment_method).lower() == "kaspi"
    )

    # Create Kaspi payment if payment_method is kaspi
    if order.payment_method == "kaspi":
        logger.info("kaspi_payment_block_entered", order_id=order.id)
        try:
            logger.info("kaspi_payment_calling_service", order_id=order.id)
            await OrderService.create_kaspi_payment_for_order(session, order)
            logger.info("kaspi_payment_service_completed", order_id=order.id)
        except Exception as e:
            logger.error("kaspi_payment_creation_failed", order_id=order.id, error=str(e), error_type=type(e).__name__)
            # Continue even if payment creation fails
    else:
        logger.info("kaspi_payment_block_skipped", order_id=order.id, reason="payment_method_not_kaspi")

    # Update client profile (async, non-blocking)
    try:
        await profile_builder_service.update_client_profile_after_order(session, order)
    except Exception as e:
        logger.error("profile_update_failed", order_id=order.id, error=str(e))
        # Continue even if profile update fails

    # Analytics & Notifications (only for first order)
    try:
        from services import analytics, telegram_notifications
        from utils import kopecks_to_tenge

        # Check if this is the first order
        if await analytics.mark_first_order_received(session, shop_id):
            # Get shop and owner info for notification
            shop_data, owner = await analytics.get_shop_with_owner(session, shop_id)

            # Send first order notification
            await telegram_notifications.notify_first_order_received(
                shop_id=shop_id,
                shop_name=shop_data.name if shop_data else "Unknown",
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


@router.get("/{order_id}/availability", response_model=AvailabilityResponse)
async def check_existing_order_availability(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Check availability for existing order items"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get order items and convert to OrderItemRequest format
    items = await load_order_items(session, order_id)

    order_item_requests = [
        OrderItemRequest(
            product_id=item.product_id,
            quantity=item.quantity,
            special_requests=item.special_requests
        )
        for item in items
    ]

    return await InventoryService.check_batch_availability(session, order_item_requests)


@router.post("/{order_id}/reserve", response_model=dict)
async def reserve_order_items(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Reserve warehouse items for an order"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get order items
    items = await load_order_items(session, order_id)

    if not items:
        raise HTTPException(status_code=400, detail="Order has no items to reserve")

    order_item_requests = [
        OrderItemRequest(
            product_id=item.product_id,
            quantity=item.quantity,
            special_requests=item.special_requests
        )
        for item in items
    ]

    try:
        success = await InventoryService.create_reservation(
            session, order_id, order_item_requests, validate_availability=True
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot reserve items: {str(e)}")

    return {"message": "Items reserved successfully"}


@router.delete("/{order_id}/reservations")
async def release_order_reservations(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Release all reservations for an order"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    count = await InventoryService.release_reservations(session, order_id)

    return {"message": f"Successfully released {count} reservations"}


# ===============================
# Group 6: Photo Management
# ===============================

# Cloudflare Worker URL for image uploads
IMAGE_WORKER_URL = "https://flower-shop-images.alekenov.workers.dev"


@router.post("/{order_id}/photo")
async def upload_order_photo(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    file: UploadFile = File(...),
):
    """
    Upload photo for order (before delivery).

    - Uploads photo to Cloudflare R2
    - Saves photo URL in database
    - Automatically changes order status to ASSEMBLED
    - Only 1 photo per order (replaces existing)
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")

    await file.seek(0)  # Reset file pointer

    try:
        # Upload to Cloudflare Worker
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {
                'file': (file.filename, contents, file.content_type)
            }

            response = await client.post(
                f"{IMAGE_WORKER_URL}/upload",
                files=files
            )

            if response.status_code != 201:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload image to storage: {error_data.get('error', 'Unknown error')}"
                )

            result = response.json()
            photo_url = result.get('url')

            if not photo_url:
                raise HTTPException(status_code=500, detail="No URL returned from image storage")

        # Delete existing photo for this order (only 1 photo allowed)
        existing_photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == "delivery"
        )
        existing_photos_result = await session.execute(existing_photos_query)
        existing_photos = list(existing_photos_result.scalars().all())

        for existing_photo in existing_photos:
            await session.delete(existing_photo)

        # Create new photo record
        new_photo = OrderPhoto(
            order_id=order_id,
            photo_url=photo_url,
            photo_type="delivery",
            label="Фото до доставки"
        )
        session.add(new_photo)

        # Automatically change status to ASSEMBLED
        old_status = order.status
        if old_status != OrderStatus.ASSEMBLED:
            order.status = OrderStatus.ASSEMBLED

            # Create history record
            history = OrderHistory(
                order_id=order_id,
                field_name="status",
                old_value=old_status.value,
                new_value=OrderStatus.ASSEMBLED.value,
                changed_by="admin"
            )
            session.add(history)

        await session.commit()
        await session.refresh(new_photo)

        return {
            "success": True,
            "photo_url": photo_url,
            "photo_id": new_photo.id,
            "message": "Photo uploaded successfully and order status changed to ASSEMBLED"
        }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to image storage: {str(e)}")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@router.delete("/{order_id}/photo")
async def delete_order_photo(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """
    Delete photo from order.

    - Removes photo record from database
    - Changes order status back to ACCEPTED
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        # Find and delete photo
        photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == "delivery"
        )
        photos_result = await session.execute(photos_query)
        photos = list(photos_result.scalars().all())

        if not photos:
            raise HTTPException(status_code=404, detail="No photo found for this order")

        # Delete photo record
        for photo in photos:
            await session.delete(photo)

        # Change status back to ACCEPTED
        old_status = order.status
        if old_status != OrderStatus.ACCEPTED:
            order.status = OrderStatus.ACCEPTED

            # Create history record
            history = OrderHistory(
                order_id=order_id,
                field_name="status",
                old_value=old_status.value,
                new_value=OrderStatus.ACCEPTED.value,
                changed_by="admin"
            )
            session.add(history)

        await session.commit()

        return {
            "success": True,
            "message": "Photo deleted successfully and order status changed to ACCEPTED"
        }

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete photo: {str(e)}")


class PhotoCreateRequest(BaseModel):
    """Request model for creating photo record directly (testing only)"""
    photo_url: str = Field(..., description="Photo URL")
    photo_type: str = Field(default="delivery", description="Photo type")
    label: Optional[str] = Field(None, description="Photo label")


@router.post("/{order_id}/photo/test")
async def create_order_photo_test(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int,
    photo_data: PhotoCreateRequest
):
    """
    Create photo record directly without file upload (for testing).

    **Testing endpoint only** - creates OrderPhoto record with provided URL.
    Used by automated tests to create photo records before testing feedback.
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    try:
        # Delete existing photo for this order (only 1 photo allowed)
        existing_photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == photo_data.photo_type
        )
        existing_photos_result = await session.execute(existing_photos_query)
        existing_photos = list(existing_photos_result.scalars().all())

        for existing_photo in existing_photos:
            await session.delete(existing_photo)

        # Create new photo record
        new_photo = OrderPhoto(
            order_id=order_id,
            photo_url=photo_data.photo_url,
            photo_type=photo_data.photo_type,
            label=photo_data.label or "Test photo"
        )
        session.add(new_photo)

        await session.commit()
        await session.refresh(new_photo)

        return {
            "success": True,
            "photo_url": new_photo.photo_url,
            "photo_id": new_photo.id,
            "message": "Photo record created successfully"
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create photo record: {str(e)}")


class PhotoFeedbackRequest(BaseModel):
    """Request model for photo feedback"""
    feedback: str = Field(..., description="Client feedback: 'like' or 'dislike'")
    comment: Optional[str] = Field(None, description="Optional comment (required for dislike)")


@router.post("/by-tracking/{tracking_id}/photo/feedback")
async def submit_photo_feedback_by_tracking(
    *,
    session: AsyncSession = Depends(get_session),
    tracking_id: str,
    feedback_data: PhotoFeedbackRequest
):
    """
    Submit customer feedback for order photo by tracking ID.

    - Accepts like/dislike feedback
    - Optional comment (especially for dislikes)
    - Creates order history entry
    - Updates photo record with feedback
    """

    # Validate feedback type
    if feedback_data.feedback not in ["like", "dislike"]:
        raise HTTPException(
            status_code=400,
            detail="Feedback must be 'like' or 'dislike'"
        )

    # Find order by tracking ID
    order = await get_order_by_tracking_id(session, tracking_id)
    order_id = order.id

    try:
        # Find order photo
        photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == "delivery"
        )
        photos_result = await session.execute(photos_query)
        photo = photos_result.scalar_one_or_none()

        if not photo:
            raise HTTPException(
                status_code=404,
                detail="No photo found for this order. Cannot submit feedback."
            )

        # Check if feedback already submitted
        if photo.client_feedback:
            raise HTTPException(
                status_code=400,
                detail="Feedback already submitted for this photo"
            )

        # Update photo with feedback
        photo.client_feedback = feedback_data.feedback
        photo.client_comment = feedback_data.comment
        photo.feedback_at = datetime.now()

        # Create history entry
        feedback_icon = "👍" if feedback_data.feedback == "like" else "👎"
        history_message = f"{feedback_icon} {feedback_data.feedback.capitalize()}"
        if feedback_data.comment:
            history_message += f": {feedback_data.comment}"

        history = OrderHistory(
            order_id=order_id,
            field_name="photo_feedback",
            old_value=None,
            new_value=history_message,
            changed_by="customer"
        )
        session.add(history)

        await session.commit()
        await session.refresh(photo)

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback": {
                "type": photo.client_feedback,
                "comment": photo.client_comment,
                "submitted_at": photo.feedback_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


# ===============================
# Group 7: Statistics
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
# Group 9: Assignment Management
# ===============================

class AssignRequest(BaseModel):
    """Request model for assignment"""
    user_id: int = Field(..., description="ID of user to assign")


@router.patch("/{order_id}/assign-responsible", response_model=OrderRead)
async def assign_responsible(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int = Path(..., description="Order ID"),
    assign_data: AssignRequest
):
    """
    Assign responsible person to order.

    Only DIRECTOR or MANAGER can assign.
    Responsible can be DIRECTOR, MANAGER, or FLORIST (not COURIER).
    """

    # Validate permissions - only DIRECTOR or MANAGER can assign
    if current_user.role not in [UserRole.DIRECTOR, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Only DIRECTOR or MANAGER can assign responsible person"
        )

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    # Get user to assign
    assignee = await session.get(User, assign_data.user_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify assignee belongs to same shop
    if assignee.shop_id != shop_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign user from different shop"
        )

    # Validate role - responsible cannot be COURIER
    if assignee.role == UserRole.COURIER:
        raise HTTPException(
            status_code=400,
            detail="COURIER cannot be assigned as responsible. Use assign-courier endpoint instead."
        )

    # Validate role - must be DIRECTOR, MANAGER, or FLORIST
    if assignee.role not in [UserRole.DIRECTOR, UserRole.MANAGER, UserRole.FLORIST]:
        raise HTTPException(
            status_code=400,
            detail="Responsible must be DIRECTOR, MANAGER, or FLORIST"
        )

    try:
        # Store old value for history
        old_value = None
        if order.assigned_to_id:
            old_user = await session.get(User, order.assigned_to_id)
            old_value = f"{old_user.name} (ID: {old_user.id})" if old_user else str(order.assigned_to_id)

        # Update order assignment
        order.assigned_to_id = assign_data.user_id
        order.assigned_by_id = current_user.id
        order.assigned_at = datetime.now()

        # Create history entry
        new_value = f"{assignee.name} (ID: {assignee.id})"
        history = OrderHistory(
            order_id=order_id,
            field_name="assigned_to",
            old_value=old_value,
            new_value=new_value,
            changed_by="admin"
        )
        session.add(history)

        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Return updated order with full relations
        return await OrderService.get_order_with_items(session, order_id, shop_id)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to assign responsible: {str(e)}")


@router.patch("/{order_id}/assign-courier", response_model=OrderRead)
async def assign_courier(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int = Path(..., description="Order ID"),
    assign_data: AssignRequest
):
    """
    Assign courier to order.

    Only DIRECTOR or MANAGER can assign.
    Courier must have COURIER role.
    """

    # Validate permissions - only DIRECTOR or MANAGER can assign
    if current_user.role not in [UserRole.DIRECTOR, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Only DIRECTOR or MANAGER can assign courier"
        )

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    # Get user to assign
    assignee = await session.get(User, assign_data.user_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify assignee belongs to same shop
    if assignee.shop_id != shop_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign user from different shop"
        )

    # Validate role - courier must have COURIER role
    if assignee.role != UserRole.COURIER:
        raise HTTPException(
            status_code=400,
            detail="Only users with COURIER role can be assigned as courier"
        )

    try:
        # Store old value for history
        old_value = None
        if order.courier_id:
            old_user = await session.get(User, order.courier_id)
            old_value = f"{old_user.name} (ID: {old_user.id})" if old_user else str(order.courier_id)

        # Update order courier assignment
        order.courier_id = assign_data.user_id
        order.assigned_by_id = current_user.id
        order.assigned_at = datetime.now()

        # Create history entry
        new_value = f"{assignee.name} (ID: {assignee.id})"
        history = OrderHistory(
            order_id=order_id,
            field_name="courier",
            old_value=old_value,
            new_value=new_value,
            changed_by="admin"
        )
        session.add(history)

        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Return updated order with full relations
        return await OrderService.get_order_with_items(session, order_id, shop_id)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to assign courier: {str(e)}")

