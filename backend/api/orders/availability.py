"""
Orders Availability Router - Availability checks and public marketplace endpoints

Handles product availability validation, inventory reservations,
order preview calculations, and public order creation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import (
    Order, OrderRead, OrderCreateWithItems,
    OrderItemRequest, ProductAvailability, AvailabilityResponse
)
from services.order_service import OrderService
from services.inventory_service import InventoryService
from services.client_service import client_service
from services.profile_builder_service import profile_builder_service
from auth_utils import get_current_user_shop_id
from utils import normalize_phone_number

router = APIRouter()

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
