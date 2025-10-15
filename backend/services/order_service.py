"""
Order Service

Provides atomic order number generation and order business logic.
Handles order total calculations, validation, and data integrity.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func, Integer
from fastapi import HTTPException

from models import (
    Order, OrderCreate, OrderCreateWithItems, OrderRead, OrderItemRequest, OrderUpdate,
    OrderItem, Product, OrderStatus, OrderCounter, OrderHistory
)
from core.logging import get_logger


class OrderService:
    """Service class for order operations with atomic guarantees"""

    @staticmethod
    async def ensure_counter_exists(session: AsyncSession) -> None:
        """Ensure the order counter record exists and is synchronized with existing orders"""
        try:
            # Try to get the counter record
            result = await session.execute(select(OrderCounter).where(OrderCounter.id == 1))
            counter = result.scalar_one_or_none()

            if not counter:
                # Get the maximum order number from existing orders
                max_order_query = await session.execute(
                    select(func.max(
                        func.cast(func.substr(Order.orderNumber, 2), Integer)
                    )).select_from(Order)
                )
                max_order_num = max_order_query.scalar() or 0

                # Create the counter record initialized with the max order number
                counter = OrderCounter(id=1, counter=max_order_num)
                session.add(counter)
                await session.commit()
        except Exception as e:
            # Handle potential race condition during creation
            await session.rollback()
            # Try again - another process might have created it
            result = await session.execute(select(OrderCounter).where(OrderCounter.id == 1))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize order counter: {str(e)}"
                )

    @staticmethod
    async def generate_tracking_id(session: AsyncSession) -> str:
        """
        Generate unique 9-digit tracking ID for public order tracking.

        Returns:
            9-digit string (e.g., "847562910")

        Raises:
            HTTPException if unable to generate unique ID after max attempts
        """
        import random

        max_attempts = 10

        for _ in range(max_attempts):
            # Generate random 9-digit number
            tracking_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])

            # Check uniqueness
            result = await session.execute(
                select(Order).where(Order.tracking_id == tracking_id)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                return tracking_id

        # If we couldn't generate unique ID after max attempts
        raise HTTPException(
            status_code=500,
            detail="Failed to generate unique tracking ID"
        )

    @staticmethod
    async def generate_order_number(session: AsyncSession) -> str:
        """
        Generate unique order number atomically using transaction isolation.

        This method ensures no race conditions even under high concurrency.
        Returns order number in format: #00001
        """
        try:
            # Ensure counter exists
            await OrderService.ensure_counter_exists(session)

            # Begin a new transaction for atomicity
            await session.begin_nested()

            # For SQLite: UPDATE and SELECT in one transaction with immediate mode
            # This ensures atomicity even without RETURNING clause
            await session.execute(
                text("UPDATE ordercounter SET counter = counter + 1, last_updated = CURRENT_TIMESTAMP WHERE id = 1")
            )

            # Get the updated counter value in the same transaction
            result = await session.execute(
                text("SELECT counter FROM ordercounter WHERE id = 1")
            )
            new_counter = result.scalar_one()

            # Commit the nested transaction
            await session.commit()

            # Generate order number with zero-padding
            order_number = f"#{str(new_counter).zfill(5)}"

            return order_number

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate order number: {str(e)}"
            )

    @staticmethod
    async def calculate_order_totals(
        session: AsyncSession,
        items: List[OrderItemRequest],
        delivery_cost: int = 0,
        shop_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate order totals and validate items.

        Args:
            session: Database session
            items: List of order items to calculate
            delivery_cost: Delivery cost in tenge
            shop_id: Shop ID for multi-tenancy verification (optional)

        Returns:
            Dict containing subtotal, total, and validated item data
        """
        subtotal = 0
        order_items_data = []

        for item_request in items:
            # Get product details
            product = await session.get(Product, item_request.product_id)
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item_request.product_id} not found"
                )

            # Verify product belongs to shop if shop_id provided
            if shop_id is not None and product.shop_id != shop_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Product '{product.name}' does not belong to your shop"
                )

            if not product.enabled:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product '{product.name}' is not available"
                )

            # Validate quantity
            if item_request.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid quantity {item_request.quantity} for product '{product.name}'"
                )

            # Calculate item total
            item_total = product.price * item_request.quantity
            subtotal += item_total

            # Prepare item data for creation
            order_items_data.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_price": product.price,
                "quantity": item_request.quantity,
                "item_total": item_total,
                "special_requests": item_request.special_requests
            })

        total = subtotal + delivery_cost

        return {
            "subtotal": subtotal,
            "total": total,
            "items_data": order_items_data
        }

    @staticmethod
    async def create_order_with_items(
        session: AsyncSession,
        order_data: OrderCreateWithItems,
        shop_id: int,
        check_availability: bool = True
    ) -> Order:
        """
        Create a new order with items atomically.

        Args:
            session: Database session
            order_data: Order creation data
            shop_id: Shop ID for multi-tenancy
            check_availability: Whether to check ingredient availability

        Returns:
            Created Order instance
        """
        # Check availability if requested
        if check_availability and order_data.items:
            from services.inventory_service import InventoryService
            availability = await InventoryService.check_batch_availability(
                session, order_data.items
            )
            if not availability.available:
                warnings_str = "; ".join(availability.warnings)
                raise HTTPException(
                    status_code=400,
                    detail=f"Order cannot be created due to insufficient stock: {warnings_str}"
                )

        # Generate atomic order number and tracking ID
        order_number = await OrderService.generate_order_number(session)
        tracking_id = await OrderService.generate_tracking_id(session)

        # Calculate totals and validate items belong to shop
        totals = await OrderService.calculate_order_totals(
            session, order_data.items, order_data.delivery_cost, shop_id
        )

        # Create order instance with shop_id
        order_dict = order_data.model_dump(exclude={"items", "check_availability"})

        # Fix Bug #2: Strip timezone from delivery_date if present
        # PostgreSQL column is TIMESTAMP WITHOUT TIME ZONE, but frontend sends ISO string with timezone
        if order_dict.get("delivery_date") and hasattr(order_dict["delivery_date"], "tzinfo"):
            order_dict["delivery_date"] = order_dict["delivery_date"].replace(tzinfo=None)

        order_dict.update({
            "shop_id": shop_id,  # Inject shop_id for multi-tenancy
            "tracking_id": tracking_id,
            "orderNumber": order_number,
            "subtotal": totals["subtotal"],
            "total": totals["total"]
        })

        order = Order(**order_dict)

        # Add order to session
        session.add(order)
        await session.flush()  # Get the order ID without committing

        # Create order items
        created_items = []
        for item_data in totals["items_data"]:
            item_data["order_id"] = order.id
            order_item = OrderItem(**item_data)
            session.add(order_item)
            created_items.append(order_item)

        # Commit the transaction
        await session.commit()

        # Refresh to get all fields
        await session.refresh(order)
        for item in created_items:
            await session.refresh(item)

        # Reserve ingredients if availability checking was enabled
        if check_availability and order_data.items:
            try:
                from services.inventory_service import InventoryService
                await InventoryService.create_reservation(
                    session, order.id, order_data.items, validate_availability=False
                )
            except Exception as e:
                # Log warning but don't fail the order creation
                # In production, you might want to handle this differently
                pass

        return order

    @staticmethod
    async def create_simple_order(
        session: AsyncSession,
        order_data: OrderCreate,
        shop_id: int
    ) -> Order:
        """
        Create a simple order without items.

        Args:
            session: Database session
            order_data: Order creation data
            shop_id: Shop ID for multi-tenancy

        Returns:
            Created Order instance
        """
        # Generate atomic order number and tracking ID
        order_number = await OrderService.generate_order_number(session)
        tracking_id = await OrderService.generate_tracking_id(session)

        # Create order instance with shop_id
        order_dict = order_data.model_dump()

        # Fix Bug #2: Strip timezone from delivery_date if present
        if order_dict.get("delivery_date") and hasattr(order_dict["delivery_date"], "tzinfo"):
            order_dict["delivery_date"] = order_dict["delivery_date"].replace(tzinfo=None)

        order_dict.update({
            "shop_id": shop_id,  # Inject shop_id for multi-tenancy
            "tracking_id": tracking_id,
            "orderNumber": order_number,
            "subtotal": 0,  # Will be calculated when items are added
            "total": order_data.delivery_cost  # Just delivery cost for now
        })

        order = Order(**order_dict)

        # Add to session and commit
        session.add(order)
        await session.commit()
        await session.refresh(order)

        return order

    @staticmethod
    async def validate_order_data(order_data: Dict[str, Any]) -> None:
        """
        Validate order data for business rules.

        Args:
            order_data: Dictionary containing order fields
        """
        # Validate customer name
        if not order_data.get("customerName") or len(order_data["customerName"].strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Customer name is required"
            )

        # Validate phone number
        if not order_data.get("phone") or len(order_data["phone"].strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Phone number is required"
            )

        # Validate delivery cost
        delivery_cost = order_data.get("delivery_cost", 0)
        if delivery_cost < 0:
            raise HTTPException(
                status_code=400,
                detail="Delivery cost cannot be negative"
            )

        # Validate delivery date if provided
        delivery_date = order_data.get("delivery_date")
        if delivery_date and delivery_date < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Delivery date cannot be in the past"
            )

    @staticmethod
    async def get_order_with_items(
        session: AsyncSession,
        order_id: int,
        shop_id: Optional[int] = None
    ) -> OrderRead:
        """
        Get an order with its items, properly formatted for API response.

        Args:
            session: Database session
            order_id: Order ID to retrieve
            shop_id: Shop ID for multi-tenancy verification (optional)

        Returns:
            OrderRead instance
        """
        # Get order
        order = await session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Verify order belongs to shop if shop_id provided
        if shop_id is not None and order.shop_id != shop_id:
            raise HTTPException(status_code=403, detail="Order does not belong to your shop")

        # Get order items
        items_query = select(OrderItem).where(OrderItem.order_id == order.id)
        items_result = await session.execute(items_query)
        items = list(items_result.scalars().all())

        # Create response model manually to avoid relationship issues
        from models import OrderItemRead
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
            # Phase 3 fields
            recipient_name=order.recipient_name,
            recipient_phone=order.recipient_phone,
            sender_phone=order.sender_phone,
            pickup_address=order.pickup_address,
            delivery_type=order.delivery_type,
            scheduled_time=order.scheduled_time,
            payment_method=order.payment_method,
            order_comment=order.order_comment,
            bonus_points=order.bonus_points,
            # Kaspi Pay fields
            kaspi_payment_id=order.kaspi_payment_id,
            kaspi_payment_status=order.kaspi_payment_status,
            kaspi_payment_created_at=order.kaspi_payment_created_at,
            kaspi_payment_completed_at=order.kaspi_payment_completed_at,
            # AI Agent clarification flags
            ask_delivery_address=order.ask_delivery_address,
            ask_delivery_time=order.ask_delivery_time,
            # Metadata
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[OrderItemRead.model_validate(item) for item in items]
        )

    @staticmethod
    async def recalculate_order_total(session: AsyncSession, order_id: int) -> Order:
        """
        Recalculate order total based on current items.

        Args:
            session: Database session
            order_id: Order ID to recalculate

        Returns:
            Updated Order instance
        """
        order = await session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Get all order items
        items_query = select(OrderItem).where(OrderItem.order_id == order_id)
        items_result = await session.execute(items_query)
        items = items_result.scalars().all()

        # Calculate new subtotal
        subtotal = sum(item.item_total for item in items)

        # Update order totals
        order.subtotal = subtotal
        order.total = subtotal + order.delivery_cost

        await session.commit()
        await session.refresh(order)

        return order

    @staticmethod
    def validate_order_editable(order: Order) -> None:
        """
        Validate that an order can be edited based on its status.

        Args:
            order: Order to validate

        Raises:
            HTTPException: If order cannot be edited
        """
        non_editable_statuses = [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
        if order.status in non_editable_statuses:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot edit order with status '{order.status}'. Order is already completed."
            )

    @staticmethod
    async def update_order_with_history(
        session: AsyncSession,
        order: Order,
        order_update: OrderUpdate,
        changed_by: str = "admin"
    ) -> Order:
        """
        Update order fields with automatic history tracking.
        Consolidates update logic to eliminate duplication.

        Args:
            session: Database session
            order: Order to update
            order_update: Update data
            changed_by: Who is making the change ('customer' or 'admin')

        Returns:
            Updated Order instance
        """
        # Validate order can be edited
        OrderService.validate_order_editable(order)

        # Update fields that were provided and log changes
        order_data = order_update.model_dump(exclude_unset=True)
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

        return order

    @staticmethod
    async def create_kaspi_payment_for_order(
        session: AsyncSession,
        order: Order
    ) -> Optional[str]:
        """
        Create Kaspi Pay payment for order and update order with payment info.

        Args:
            session: Database session
            order: Order to create payment for

        Returns:
            External ID (QrPaymentId) if payment created, None otherwise

        Raises:
            HTTPException: If payment creation fails
        """
        # Only create payment for Kaspi orders
        if order.payment_method != "kaspi":
            return None

        try:
            from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError

            kaspi_service = get_kaspi_service()

            # Create payment (amount in tenge)
            response = await kaspi_service.create_payment(
                phone=order.phone,
                amount=order.total / 100,  # Convert kopecks to tenge
                message=f"Заказ {order.orderNumber}"
            )

            # Extract external ID from response
            external_id = response.get("data", {}).get("externalId")

            if external_id:
                # Update order with payment info
                order.kaspi_payment_id = str(external_id)
                order.kaspi_payment_status = "Wait"
                order.kaspi_payment_created_at = datetime.now()
                await session.commit()
                await session.refresh(order)  # Refresh to avoid detached object issues

                logger = get_logger(__name__)
                logger.info(
                    "kaspi_payment_created_for_order",
                    order_id=order.id,
                    order_number=order.orderNumber,
                    external_id=external_id
                )

                return external_id

            raise HTTPException(
                status_code=500,
                detail="Kaspi Pay did not return externalId"
            )

        except KaspiPayServiceError as e:
            logger = get_logger(__name__)
            logger.error(
                "kaspi_payment_failed",
                order_id=order.id,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create Kaspi payment: {str(e)}"
            )