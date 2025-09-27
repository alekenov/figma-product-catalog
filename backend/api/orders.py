from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select, col
from database import get_session
from models import (
    Order, OrderCreate, OrderCreateWithItems, OrderRead, OrderUpdate, OrderStatus,
    OrderItem, OrderItemCreate, OrderItemRead,
    Product, ProductRecipe, WarehouseItem, WarehouseOperation, WarehouseOperationType,
    OrderReservation, OrderReservationCreate,
    OrderItemRequest, ProductAvailability, AvailabilityResponse
)
from services.inventory_service import InventoryService
from services.client_service import client_service
from services.order_service import OrderService

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
    """Get single order by ID with items"""
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Load order items
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await session.execute(items_query)
    items = list(items_result.scalars().all())

    # Create response model manually to avoid relationship issues
    return OrderRead(
        id=order.id,
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
        items=[OrderItemRead.model_validate(item) for item in items]
    )


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
    order_in: OrderUpdate
):
    """Update order details"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update fields that were provided
    order_data = order_in.model_dump(exclude_unset=True)
    for field, value in order_data.items():
        setattr(order, field, value)

    # Commit changes
    await session.commit()
    await session.refresh(order)

    # Load items for response
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await session.execute(items_query)
    order.items = list(items_result.all())

    return order


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
        await session.refresh(order)

        # Load items for response
        items_query = select(OrderItem).where(OrderItem.order_id == order.id)
        items_result = await session.execute(items_query)
        order.items = list(items_result.all())

        return order

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