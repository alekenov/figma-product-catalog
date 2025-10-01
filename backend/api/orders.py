from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select, col
from database import get_session
from models import (
    Order, OrderCreate, OrderCreateWithItems, OrderRead, OrderUpdate, OrderStatus,
    OrderItem, OrderItemCreate, OrderItemRead,
    OrderHistory, OrderHistoryRead,
    OrderPhoto, OrderPhotoRead,
    Product, ProductRecipe, WarehouseItem, WarehouseOperation, WarehouseOperationType,
    OrderReservation, OrderReservationCreate,
    OrderItemRequest, ProductAvailability, AvailabilityResponse
)
from services.inventory_service import InventoryService
from services.client_service import client_service
from services.order_service import OrderService
import httpx

router = APIRouter()


@router.get("/", response_model=List[OrderRead])
async def get_orders(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    customer_phone: Optional[str] = Query(None, description="Filter by customer phone"),
    search: Optional[str] = Query(None, description="Search in customer name or order number"),
):
    """Get list of orders with filtering"""

    # Build query with eager loading of items
    query = select(Order).options(selectinload(Order.items))

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

    # Order by creation date (newest first)
    query = query.order_by(Order.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query - items will be loaded automatically
    result = await session.execute(query)
    orders = result.scalars().all()

    # Create response models using pre-loaded items
    order_responses = []
    for order in orders:
        order_response = OrderRead(
            id=order.id,
            tracking_id=order.tracking_id,
            orderNumber=order.orderNumber,
            customerName=order.customerName,
            phone=order.phone,
            customer_email=order.customer_email,
            delivery_address=order.delivery_address,
            delivery_date=order.delivery_date,
            delivery_notes=order.delivery_notes,
            subtotal=order.subtotal,
            delivery_cost=order.delivery_cost,
            total=order.total,
            status=order.status,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[OrderItemRead.model_validate(item) for item in order.items]
        )
        order_responses.append(order_response)

    return order_responses


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Get single order by ID with items and photos"""
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Load order items
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await session.execute(items_query)
    items = list(items_result.scalars().all())

    # Load order photos
    photos_query = select(OrderPhoto).where(OrderPhoto.order_id == order.id)
    photos_result = await session.execute(photos_query)
    photos = list(photos_result.scalars().all())

    # Create response model manually to avoid relationship issues
    return OrderRead(
        id=order.id,
        tracking_id=order.tracking_id,
        orderNumber=order.orderNumber,
        customerName=order.customerName,
        phone=order.phone,
        customer_email=order.customer_email,
        delivery_address=order.delivery_address,
        delivery_date=order.delivery_date,
        delivery_notes=order.delivery_notes,
        subtotal=order.subtotal,
        delivery_cost=order.delivery_cost,
        total=order.total,
        status=order.status,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[OrderItemRead.model_validate(item) for item in items],
        photos=[OrderPhotoRead.model_validate(photo) for photo in photos]
    )


def map_status_to_frontend(status: OrderStatus) -> str:
    """
    Map backend OrderStatus to frontend vocabulary.
    Frontend OrderProgressBar expects: 'confirmed', 'preparing', 'delivering'
    """
    mapping = {
        OrderStatus.NEW: "confirmed",
        OrderStatus.PAID: "confirmed",
        OrderStatus.ACCEPTED: "confirmed",
        OrderStatus.ASSEMBLED: "preparing",
        OrderStatus.IN_DELIVERY: "delivering",
        OrderStatus.DELIVERED: "delivering",
        OrderStatus.CANCELLED: "confirmed"  # Show as first stage for cancelled
    }
    return mapping.get(status, "confirmed")


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
    # Find order by tracking ID
    query = select(Order).where(Order.tracking_id == tracking_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order with tracking ID {tracking_id} not found")

    # Load order items
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await session.execute(items_query)
    items = list(items_result.scalars().all())

    # Load order photos
    from models import OrderPhoto
    photos_query = select(OrderPhoto).where(OrderPhoto.order_id == order.id)
    photos_result = await session.execute(photos_query)
    photos = list(photos_result.scalars().all())

    # Format datetime
    date_time_str = "Not specified"
    if order.delivery_date:
        date_time_str = order.delivery_date.strftime("%A %d %B, %H:%M")
    elif order.created_at:
        date_time_str = order.created_at.strftime("%A %d %B, %H:%M")

    # Format delivery type
    delivery_type_display = "Standard Delivery"
    if order.delivery_type == "express":
        delivery_type_display = "Express 30 min"
    elif order.delivery_type == "scheduled" and order.scheduled_time:
        delivery_type_display = f"Scheduled: {order.scheduled_time}"
    elif order.delivery_type == "pickup":
        delivery_type_display = "Self Pickup"

    # Build response matching frontend OrderStatusPage expectations
    return {
        "tracking_id": order.tracking_id,
        "order_number": order.orderNumber,
        "status": map_status_to_frontend(order.status),  # Frontend vocabulary
        "recipient": {
            "name": order.recipient_name or order.customerName,
            "phone": order.recipient_phone or order.phone
        },
        "pickup_address": order.pickup_address or "Store address not specified",
        "delivery_address": order.delivery_address or "Not specified",
        "date_time": date_time_str,
        "sender": {
            "phone": order.sender_phone or order.phone
        },
        "photos": [
            {
                "url": photo.photo_url,
                "label": photo.label or photo.photo_type,
                "feedback": photo.client_feedback,
                "comment": photo.client_comment
            }
            for photo in photos
        ],
        "items": [
            {
                "name": f"{item.product_name}",
                "price": item.item_total
            }
            for item in items
        ],
        "delivery_cost": order.delivery_cost,
        "delivery_type": delivery_type_display,
        "total": order.total,
        "bonus_points": order.bonus_points or 0
    }


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

    # Find order by tracking ID
    query = select(Order).where(Order.tracking_id == tracking_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order with tracking ID {tracking_id} not found")

    # Check if order can be edited based on status
    non_editable_statuses = [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
    if order.status in non_editable_statuses:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot edit order with status '{order.status}'. Order is already completed."
        )

    # Update fields that were provided and log changes
    order_data = order_in.model_dump(exclude_unset=True)
    for field, new_value in order_data.items():
        old_value = getattr(order, field, None)

        # Only log if value actually changed
        if old_value != new_value:
            # Convert values to strings for history logging
            old_value_str = str(old_value) if old_value is not None else None
            new_value_str = str(new_value) if new_value is not None else None

            # Create history record
            history_entry = OrderHistory(
                order_id=order.id,
                changed_by=changed_by,
                field_name=field,
                old_value=old_value_str,
                new_value=new_value_str
            )
            session.add(history_entry)

            # Update the order field
            setattr(order, field, new_value)

    # Commit changes
    await session.commit()

    # Clear session to avoid expired object issues
    session.expunge_all()

    # Use service method to properly load order with all relationships
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
    # Find order by order number
    query = select(Order).where(Order.orderNumber == order_number)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_number} not found")

    # Load order items
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await session.execute(items_query)
    items = list(items_result.scalars().all())

    # Load order photos
    from models import OrderPhoto
    photos_query = select(OrderPhoto).where(OrderPhoto.order_id == order.id)
    photos_result = await session.execute(photos_query)
    photos = list(photos_result.scalars().all())

    # Format datetime
    date_time_str = "Not specified"
    if order.delivery_date:
        date_time_str = order.delivery_date.strftime("%A %d %B, %H:%M")
    elif order.created_at:
        date_time_str = order.created_at.strftime("%A %d %B, %H:%M")

    # Format delivery type
    delivery_type_display = "Standard Delivery"
    if order.delivery_type == "express":
        delivery_type_display = "Express 30 min"
    elif order.delivery_type == "scheduled" and order.scheduled_time:
        delivery_type_display = f"Scheduled: {order.scheduled_time}"
    elif order.delivery_type == "pickup":
        delivery_type_display = "Self Pickup"

    # Build response matching frontend OrderStatusPage expectations
    return {
        "order_number": order.orderNumber,
        "status": map_status_to_frontend(order.status),  # Frontend vocabulary
        "recipient": {
            "name": order.recipient_name or order.customerName,
            "phone": order.recipient_phone or order.phone
        },
        "pickup_address": order.pickup_address or "Store address not specified",
        "delivery_address": order.delivery_address or "Not specified",
        "date_time": date_time_str,
        "sender": {
            "phone": order.sender_phone or order.phone
        },
        "photos": [
            {
                "url": photo.photo_url,
                "label": photo.label or photo.photo_type,
                "feedback": photo.client_feedback,
                "comment": photo.client_comment
            }
            for photo in photos
        ],
        "items": [
            {
                "name": f"{item.product_name}",
                "price": item.item_total
            }
            for item in items
        ],
        "delivery_cost": order.delivery_cost,
        "delivery_type": delivery_type_display,
        "total": order.total,
        "bonus_points": order.bonus_points or 0
    }


@router.post("/", response_model=OrderRead)
async def create_order(
    order_in: OrderCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create new order without items"""

    # Auto-create or get existing client record
    _, client_created = await client_service.get_or_create_client(
        session,
        order_in.phone,
        order_in.customerName
    )

    # Normalize phone number in order data
    order_in.phone = client_service.normalize_phone(order_in.phone)

    # Use OrderService for atomic order creation
    order = await OrderService.create_simple_order(session, order_in)

    # Return using the service method for consistent response formatting
    return await OrderService.get_order_with_items(session, order.id)


@router.post("/with-items", response_model=OrderRead)
async def create_order_with_items(
    order_in: OrderCreateWithItems,
    session: AsyncSession = Depends(get_session)
):
    """Create new order with items and availability validation"""

    # Auto-create or get existing client record
    _, client_created = await client_service.get_or_create_client(
        session,
        order_in.phone,
        order_in.customerName
    )

    # Normalize phone number in order data
    order_in.phone = client_service.normalize_phone(order_in.phone)

    # Use OrderService for atomic order creation with items
    order = await OrderService.create_order_with_items(
        session, order_in, order_in.check_availability
    )

    # Return using the service method for consistent response formatting
    return await OrderService.get_order_with_items(session, order.id)


@router.put("/{order_id}", response_model=OrderRead)
async def update_order(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    order_in: OrderUpdate,
    changed_by: str = Query(default="admin", description="Who is making the change: 'customer' or 'admin'")
):
    """Update order details with audit trail"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if order can be edited based on status
    non_editable_statuses = [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
    if order.status in non_editable_statuses:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot edit order with status '{order.status}'. Order is already completed."
        )

    # Update fields that were provided and log changes
    order_data = order_in.model_dump(exclude_unset=True)
    for field, new_value in order_data.items():
        old_value = getattr(order, field, None)

        # Only log if value actually changed
        if old_value != new_value:
            # Convert values to strings for history logging
            old_value_str = str(old_value) if old_value is not None else None
            new_value_str = str(new_value) if new_value is not None else None

            # Create history record
            history_entry = OrderHistory(
                order_id=order.id,
                changed_by=changed_by,
                field_name=field,
                old_value=old_value_str,
                new_value=new_value_str
            )
            session.add(history_entry)

            # Update the order field
            setattr(order, field, new_value)

    # Commit changes
    await session.commit()

    # Clear session to avoid expired object issues
    session.expunge_all()

    # Use service method to properly load order with all relationships
    return await OrderService.get_order_with_items(session, order.id)


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


@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    status: OrderStatus,
    notes: Optional[str] = None
):
    """Update order status with automatic warehouse deduction for assembled orders"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status

    # Begin transaction
    try:
        # Handle status transitions with reservation logic
        if status == OrderStatus.ASSEMBLED and old_status != OrderStatus.ASSEMBLED:
            # Convert reservations to actual deductions
            await InventoryService.convert_reservations_to_deductions(session, order.id)
        elif status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
            # Release reservations for cancelled orders
            await InventoryService.release_reservations(session, order.id)

        # Update status and notes
        order.status = status
        if notes:
            order.notes = notes

        # Commit changes
        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Use service method to properly load order with all relationships
        return await OrderService.get_order_with_items(session, order.id)

    except Exception as e:
        # Rollback transaction on any error
        await session.rollback()
        if "insufficient stock" in str(e).lower():
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")


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


@router.delete("/{order_id}")
async def delete_order(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Delete order and all its items"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        # Release any existing reservations first
        await InventoryService.release_reservations(session, order_id)

        # Delete order (items and reservations will be deleted via cascade)
        await session.delete(order)
        await session.commit()

        return {"message": "Order deleted successfully"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete order: {str(e)}")


async def _convert_reservations_to_deductions(
    session: AsyncSession,
    order: Order
) -> None:
    """Convert reservations to actual warehouse deductions when order is assembled"""

    # Get all reservations for this order
    reservations_query = select(OrderReservation, WarehouseItem).join(
        WarehouseItem, OrderReservation.warehouse_item_id == WarehouseItem.id
    ).where(OrderReservation.order_id == order.id)

    reservations_result = await session.execute(reservations_query)
    reservations_with_items = reservations_result.all()

    if not reservations_with_items:
        # No reservations found, fall back to old deduction logic for backwards compatibility
        await _process_warehouse_deductions(session, order)
        return

    # Process each reservation
    for reservation, warehouse_item in reservations_with_items:
        # Check if we still have enough stock (safety check)
        if warehouse_item.quantity < reservation.reserved_quantity:
            raise ValueError(
                f"Insufficient stock for {warehouse_item.name}. "
                f"Required: {reservation.reserved_quantity}, Available: {warehouse_item.quantity}"
            )

        # Perform deduction
        warehouse_item.quantity -= reservation.reserved_quantity

        # Create warehouse operation record
        operation = WarehouseOperation(
            warehouse_item_id=warehouse_item.id,
            operation_type=WarehouseOperationType.SALE,
            quantity_change=-reservation.reserved_quantity,
            balance_after=warehouse_item.quantity,
            description=f"Продажа - Заказ #{order.orderNumber} (конвертация резерва)",
            order_id=order.id
        )

        session.add(operation)

        # Delete the reservation since it's now converted to actual deduction
        await session.delete(reservation)


async def _process_warehouse_deductions(
    session: AsyncSession,
    order: Order
) -> None:
    """Process automatic warehouse deductions for order assembly"""

    # Get all order items
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await session.execute(items_query)
    order_items = items_result.scalars().all()

    if not order_items:
        raise ValueError("Order has no items to assemble")

    # Collect all warehouse deductions needed
    warehouse_deductions = {}

    for item in order_items:
        # Get product recipes for this item
        recipes_query = select(ProductRecipe, WarehouseItem).join(
            WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id
        ).where(ProductRecipe.product_id == item.product_id)

        recipes_result = await session.execute(recipes_query)
        recipes_with_items = recipes_result.all()

        if not recipes_with_items:
            # Product has no recipe - skip deduction for this item
            continue

        # Calculate total deductions for this item quantity
        for recipe, warehouse_item in recipes_with_items:
            if recipe.is_optional:
                continue  # Skip optional ingredients for now

            total_needed = recipe.quantity * item.quantity

            if warehouse_item.id not in warehouse_deductions:
                warehouse_deductions[warehouse_item.id] = {
                    'warehouse_item': warehouse_item,
                    'total_quantity': 0,
                    'product_details': []
                }

            warehouse_deductions[warehouse_item.id]['total_quantity'] += total_needed
            warehouse_deductions[warehouse_item.id]['product_details'].append({
                'product_name': item.product_name,
                'order_quantity': item.quantity,
                'recipe_quantity': recipe.quantity,
                'total_needed': total_needed
            })

    # Check stock availability and perform deductions
    deduction_operations = []

    for warehouse_item_id, deduction_data in warehouse_deductions.items():
        warehouse_item = deduction_data['warehouse_item']
        total_quantity = deduction_data['total_quantity']
        product_details = deduction_data['product_details']

        # Check if we have sufficient stock
        if warehouse_item.quantity < total_quantity:
            # Build detailed error message
            products_str = ", ".join([
                f"{detail['product_name']} (x{detail['order_quantity']})"
                for detail in product_details
            ])

            raise ValueError(
                f"Insufficient stock for {warehouse_item.name}. "
                f"Required: {total_quantity}, Available: {warehouse_item.quantity}. "
                f"Needed for products: {products_str}"
            )

        # Update warehouse quantity
        warehouse_item.quantity -= total_quantity

        # Create detailed description
        products_detail = "; ".join([
            f"{detail['product_name']} x{detail['order_quantity']} (нужно {detail['total_needed']})"
            for detail in product_details
        ])

        # Create warehouse operation record
        operation = WarehouseOperation(
            warehouse_item_id=warehouse_item_id,
            operation_type=WarehouseOperationType.SALE,
            quantity_change=-total_quantity,
            balance_after=warehouse_item.quantity,
            description=f"Продажа - Заказ #{order.orderNumber} - {products_detail}",
            order_id=order.id
        )

        session.add(operation)
        deduction_operations.append(operation)

    # If we get here, all deductions were successful
    # Operations will be committed with the main transaction


# ===============================
# Availability Checking Endpoints
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
    items_query = select(OrderItem).where(OrderItem.order_id == order_id)
    items_result = await session.execute(items_query)
    items = items_result.scalars().all()

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
    items_query = select(OrderItem).where(OrderItem.order_id == order_id)
    items_result = await session.execute(items_query)
    items = items_result.scalars().all()

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


@router.get("/stats/dashboard")
async def get_order_dashboard_stats(
    *,
    session: AsyncSession = Depends(get_session)
):
    """Get order statistics for admin dashboard"""

    # Count orders by status
    status_stats = {}
    for status in OrderStatus:
        status_query = select(Order.id).where(Order.status == status)
        status_result = await session.execute(status_query)
        status_stats[status.value] = len(status_result.all())

    # Count today's orders
    today = datetime.now().date()
    today_query = select(Order.id).where(col(Order.created_at).cast("DATE") == today)
    today_result = await session.execute(today_query)
    today_count = len(today_result.all())

    # Calculate today's revenue
    today_revenue_query = select(Order.total).where(
        col(Order.created_at).cast("DATE") == today
    ).where(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]))
    today_revenue_result = await session.execute(today_revenue_query)
    today_revenue = sum(today_revenue_result.all())

    return {
        "orders_by_status": status_stats,
        "orders_today": today_count,
        "revenue_today": today_revenue,
        "total_orders": sum(status_stats.values())
    }


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
    query = select(Order).where(Order.tracking_id == tracking_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

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