"""
Inventory Service - Consolidated warehouse and inventory management.

This service provides a clean interface for all inventory-related operations,
consolidating logic from availability_service.py, orders.py, and other files.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from models import (
    Product, ProductRecipe, WarehouseItem, OrderReservation,
    OrderItemRequest, ProductAvailability, IngredientAvailability, AvailabilityResponse,
    Order, OrderItem, OrderStatus, WarehouseOperation, WarehouseOperationType
)


class InventoryError(Exception):
    """Base exception for inventory operations"""
    pass


class InsufficientStockError(InventoryError):
    """Raised when there's insufficient stock for an operation"""
    pass


class ReservationError(InventoryError):
    """Raised when reservation operations fail"""
    pass


class InventoryService:
    """
    Consolidated inventory management service.

    Provides clean interfaces for:
    - Checking product availability
    - Managing reservations (create, release)
    - Batch operations for multiple products
    - Stock calculations with reservation consideration
    - Warehouse deductions for order assembly
    """

    # ===============================
    # Core Availability Methods
    # ===============================

    @staticmethod
    async def get_reserved_quantities(
        session: AsyncSession,
        warehouse_item_ids: List[int]
    ) -> Dict[int, int]:
        """
        Get currently reserved quantities for warehouse items.

        Args:
            session: Database session
            warehouse_item_ids: List of warehouse item IDs to check

        Returns:
            Dictionary mapping warehouse_item_id -> total_reserved_quantity
        """
        if not warehouse_item_ids:
            return {}

        query = select(
            OrderReservation.warehouse_item_id,
            func.sum(OrderReservation.reserved_quantity).label("total_reserved")
        ).where(
            OrderReservation.warehouse_item_id.in_(warehouse_item_ids)
        ).group_by(OrderReservation.warehouse_item_id)

        result = await session.execute(query)
        return dict(result.all())

    @staticmethod
    async def calculate_available_quantity(
        session: AsyncSession,
        warehouse_item_id: int
    ) -> Tuple[int, int, int]:
        """
        Calculate available quantity for a warehouse item considering reservations.

        Args:
            session: Database session
            warehouse_item_id: Warehouse item ID

        Returns:
            Tuple of (total_quantity, reserved_quantity, available_quantity)

        Raises:
            InventoryError: If warehouse item not found
        """
        # Get warehouse item
        warehouse_item = await session.get(WarehouseItem, warehouse_item_id)
        if not warehouse_item:
            raise InventoryError(f"Warehouse item {warehouse_item_id} not found")

        # Get reserved quantities
        reserved_quantities = await InventoryService.get_reserved_quantities(
            session, [warehouse_item_id]
        )

        total_quantity = warehouse_item.quantity
        reserved_quantity = reserved_quantities.get(warehouse_item_id, 0)
        available_quantity = total_quantity - reserved_quantity

        return total_quantity, reserved_quantity, available_quantity

    @staticmethod
    async def check_product_availability(
        session: AsyncSession,
        product_id: int,
        quantity_requested: int
    ) -> ProductAvailability:
        """
        Check availability for a single product.

        Args:
            session: Database session
            product_id: Product ID to check
            quantity_requested: Requested quantity

        Returns:
            ProductAvailability object with detailed availability information
        """
        # Get product
        product_result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            return ProductAvailability(
                product_id=product_id,
                product_name="Unknown Product",
                quantity_requested=quantity_requested,
                available=False,
                max_quantity=0,
                ingredients=[]
            )

        # Check if product is enabled
        if not product.enabled:
            return ProductAvailability(
                product_id=product_id,
                product_name=product.name,
                quantity_requested=quantity_requested,
                available=False,
                max_quantity=0,
                ingredients=[]
            )

        # Get recipes with warehouse items
        recipes_result = await session.execute(
            select(ProductRecipe, WarehouseItem)
            .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
            .where(ProductRecipe.product_id == product_id)
        )

        recipes_with_items = recipes_result.all()

        if not recipes_with_items:
            # Product has no recipe, assume it's available if enabled
            return ProductAvailability(
                product_id=product_id,
                product_name=product.name,
                quantity_requested=quantity_requested,
                available=True,
                max_quantity=9999,  # Arbitrary high number for products without recipes
                ingredients=[]
            )

        # Get warehouse item IDs for reservation lookup
        warehouse_item_ids = [recipe.warehouse_item_id for recipe, _ in recipes_with_items]
        reserved_quantities = await InventoryService.get_reserved_quantities(
            session, warehouse_item_ids
        )

        # Calculate availability for each ingredient
        ingredients = []
        max_quantity = float('inf')
        all_sufficient = True

        for recipe, warehouse_item in recipes_with_items:
            required_per_product = recipe.quantity
            total_required = required_per_product * quantity_requested
            available_quantity = warehouse_item.quantity
            reserved_quantity = reserved_quantities.get(warehouse_item.id, 0)
            effective_available = available_quantity - reserved_quantity

            # Calculate maximum possible quantity for this ingredient
            if required_per_product > 0:
                max_for_ingredient = effective_available // required_per_product
                max_quantity = min(max_quantity, max_for_ingredient)

            # Check if we have enough for the requested quantity
            sufficient = effective_available >= total_required or recipe.is_optional

            if not sufficient and not recipe.is_optional:
                all_sufficient = False

            ingredients.append(IngredientAvailability(
                warehouse_item_id=warehouse_item.id,
                name=warehouse_item.name,
                required=total_required,
                available=effective_available,
                reserved=reserved_quantity,
                sufficient=sufficient
            ))

        # Handle infinite case
        if max_quantity == float('inf'):
            max_quantity = 0

        return ProductAvailability(
            product_id=product_id,
            product_name=product.name,
            quantity_requested=quantity_requested,
            available=all_sufficient and max_quantity >= quantity_requested,
            max_quantity=int(max_quantity),
            ingredients=ingredients
        )

    @staticmethod
    async def check_batch_availability(
        session: AsyncSession,
        order_items: List[OrderItemRequest]
    ) -> AvailabilityResponse:
        """
        Check availability for multiple products using optimized batched queries.

        Args:
            session: Database session
            order_items: List of order item requests

        Returns:
            AvailabilityResponse with detailed availability for all items
        """
        if not order_items:
            return AvailabilityResponse(
                available=True,
                items=[],
                warnings=[]
            )

        warnings = []

        # Group items by product to handle duplicates
        product_quantities = {}
        for item in order_items:
            if item.product_id in product_quantities:
                product_quantities[item.product_id] += item.quantity
                warnings.append(f"Duplicate product {item.product_id} found in order, quantities combined")
            else:
                product_quantities[item.product_id] = item.quantity

        product_ids = list(product_quantities.keys())

        # Batch query 1: Load all products at once
        products_result = await session.execute(
            select(Product).where(Product.id.in_(product_ids))
        )
        products_cache = {p.id: p for p in products_result.scalars()}

        # Batch query 2: Load all recipes with warehouse items for all products
        recipes_result = await session.execute(
            select(ProductRecipe, WarehouseItem)
            .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
            .where(ProductRecipe.product_id.in_(product_ids))
        )

        # Group recipes by product_id
        recipes_cache = defaultdict(list)
        all_warehouse_item_ids = set()
        for recipe, warehouse_item in recipes_result.all():
            recipes_cache[recipe.product_id].append((recipe, warehouse_item))
            all_warehouse_item_ids.add(warehouse_item.id)

        # Batch query 3: Get all reservations for all warehouse items at once
        reservations_cache = {}
        if all_warehouse_item_ids:
            reservations_cache = await InventoryService.get_reserved_quantities(
                session, list(all_warehouse_item_ids)
            )

        # Process each product using cached data
        product_availabilities = []
        all_available = True

        for product_id, total_quantity in product_quantities.items():
            product = products_cache.get(product_id)

            if not product:
                availability = ProductAvailability(
                    product_id=product_id,
                    product_name="Unknown Product",
                    quantity_requested=total_quantity,
                    available=False,
                    max_quantity=0,
                    ingredients=[]
                )
                warnings.append(f"Product {product_id} not found")
            elif not product.enabled:
                availability = ProductAvailability(
                    product_id=product_id,
                    product_name=product.name,
                    quantity_requested=total_quantity,
                    available=False,
                    max_quantity=0,
                    ingredients=[]
                )
                warnings.append(f"Product '{product.name}' is disabled")
            else:
                recipes_with_items = recipes_cache.get(product_id, [])

                if not recipes_with_items:
                    # Product has no recipe, assume it's available
                    availability = ProductAvailability(
                        product_id=product_id,
                        product_name=product.name,
                        quantity_requested=total_quantity,
                        available=True,
                        max_quantity=9999,
                        ingredients=[]
                    )
                else:
                    # Calculate availability using cached data
                    ingredients = []
                    max_quantity = float('inf')
                    all_sufficient = True

                    for recipe, warehouse_item in recipes_with_items:
                        required_per_product = recipe.quantity
                        total_required = required_per_product * total_quantity
                        available_quantity = warehouse_item.quantity
                        reserved_quantity = reservations_cache.get(warehouse_item.id, 0)
                        effective_available = available_quantity - reserved_quantity

                        # Calculate maximum possible quantity for this ingredient
                        if required_per_product > 0:
                            max_for_ingredient = effective_available // required_per_product
                            max_quantity = min(max_quantity, max_for_ingredient)

                        # Check if we have enough for the requested quantity
                        sufficient = effective_available >= total_required or recipe.is_optional

                        if not sufficient and not recipe.is_optional:
                            all_sufficient = False

                        ingredients.append(IngredientAvailability(
                            warehouse_item_id=warehouse_item.id,
                            name=warehouse_item.name,
                            required=total_required,
                            available=effective_available,
                            reserved=reserved_quantity,
                            sufficient=sufficient
                        ))

                    # Handle infinite case
                    if max_quantity == float('inf'):
                        max_quantity = 0

                    availability = ProductAvailability(
                        product_id=product_id,
                        product_name=product.name,
                        quantity_requested=total_quantity,
                        available=all_sufficient and max_quantity >= total_quantity,
                        max_quantity=int(max_quantity),
                        ingredients=ingredients
                    )

            product_availabilities.append(availability)

            if not availability.available:
                all_available = False
                if availability.max_quantity > 0:
                    warnings.append(
                        f"Product '{availability.product_name}' requested: {total_quantity}, "
                        f"maximum available: {availability.max_quantity}"
                    )
                else:
                    warnings.append(f"Product '{availability.product_name}' is out of stock")

        return AvailabilityResponse(
            available=all_available,
            items=product_availabilities,
            warnings=warnings
        )

    # ===============================
    # Reservation Management
    # ===============================

    @staticmethod
    async def create_reservation(
        session: AsyncSession,
        order_id: int,
        order_items: List[OrderItemRequest],
        validate_availability: bool = True
    ) -> bool:
        """
        Create reservations for an order.

        Args:
            session: Database session
            order_id: Order ID to create reservations for
            order_items: List of order items to reserve
            validate_availability: Whether to validate availability before creating reservations

        Returns:
            True if successful, False if insufficient stock

        Raises:
            ReservationError: If reservation creation fails
            InsufficientStockError: If stock is insufficient (when validate_availability=True)
        """
        try:
            # Check if order exists
            order = await session.get(Order, order_id)
            if not order:
                raise ReservationError(f"Order {order_id} not found")

            # Check availability first if requested
            if validate_availability:
                availability = await InventoryService.check_batch_availability(session, order_items)
                if not availability.available:
                    warnings_str = "; ".join(availability.warnings)
                    raise InsufficientStockError(f"Insufficient stock: {warnings_str}")

            # Group items by product to handle duplicates
            product_quantities = {}
            for item in order_items:
                if item.product_id in product_quantities:
                    product_quantities[item.product_id] += item.quantity
                else:
                    product_quantities[item.product_id] = item.quantity

            # Create reservations for each ingredient
            reservations_created = []

            for product_id, total_quantity in product_quantities.items():
                # Get product recipes
                recipes_result = await session.execute(
                    select(ProductRecipe, WarehouseItem)
                    .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
                    .where(ProductRecipe.product_id == product_id)
                )

                recipes_with_items = recipes_result.all()

                for recipe, warehouse_item in recipes_with_items:
                    if recipe.is_optional:
                        continue  # Skip optional ingredients

                    required_quantity = recipe.quantity * total_quantity

                    if required_quantity > 0:
                        reservation = OrderReservation(
                            order_id=order_id,
                            warehouse_item_id=warehouse_item.id,
                            reserved_quantity=required_quantity
                        )
                        session.add(reservation)
                        reservations_created.append(reservation)

            await session.commit()
            return True

        except (InsufficientStockError, ReservationError):
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise ReservationError(f"Failed to create reservations: {str(e)}")

    @staticmethod
    async def release_reservations(
        session: AsyncSession,
        order_id: int
    ) -> int:
        """
        Release all reservations for an order.

        Args:
            session: Database session
            order_id: Order ID to release reservations for

        Returns:
            Number of reservations released
        """
        try:
            reservations_result = await session.execute(
                select(OrderReservation).where(OrderReservation.order_id == order_id)
            )
            reservations = reservations_result.scalars().all()

            count = len(reservations)
            for reservation in reservations:
                await session.delete(reservation)

            await session.commit()
            return count

        except Exception as e:
            await session.rollback()
            raise ReservationError(f"Failed to release reservations: {str(e)}")

    @staticmethod
    async def get_order_reservations(
        session: AsyncSession,
        order_id: int
    ) -> List[Dict]:
        """
        Get all reservations for an order with detailed information.

        Args:
            session: Database session
            order_id: Order ID

        Returns:
            List of reservation dictionaries with warehouse item details
        """
        reservations_result = await session.execute(
            select(OrderReservation, WarehouseItem)
            .join(WarehouseItem, OrderReservation.warehouse_item_id == WarehouseItem.id)
            .where(OrderReservation.order_id == order_id)
        )

        reservations_data = []
        for reservation, warehouse_item in reservations_result.all():
            reservations_data.append({
                "reservation_id": reservation.id,
                "warehouse_item_id": warehouse_item.id,
                "warehouse_item_name": warehouse_item.name,
                "reserved_quantity": reservation.reserved_quantity,
                "created_at": reservation.created_at
            })

        return reservations_data

    # ===============================
    # Warehouse Operations
    # ===============================

    @staticmethod
    async def convert_reservations_to_deductions(
        session: AsyncSession,
        order_id: int,
        commit: bool = True
    ) -> List[WarehouseOperation]:
        """
        Convert order reservations to actual warehouse deductions.
        Used when an order is assembled.

        Args:
            session: Database session
            order_id: Order ID to process
            commit: Whether to commit the transaction (default True for backward compatibility)

        Returns:
            List of created warehouse operations

        Raises:
            InsufficientStockError: If insufficient stock for any reservation
        """
        try:
            # Get order
            order = await session.get(Order, order_id)
            if not order:
                raise InventoryError(f"Order {order_id} not found")

            # Get all reservations for this order with warehouse items
            reservations_result = await session.execute(
                select(OrderReservation, WarehouseItem)
                .join(WarehouseItem, OrderReservation.warehouse_item_id == WarehouseItem.id)
                .where(OrderReservation.order_id == order_id)
            )

            reservations_with_items = reservations_result.all()

            if not reservations_with_items:
                # No reservations found, try fallback legacy deduction
                return await InventoryService._process_legacy_warehouse_deductions(session, order)

            operations_created = []

            # Process each reservation
            for reservation, warehouse_item in reservations_with_items:
                # Safety check - ensure we still have enough stock
                if warehouse_item.quantity < reservation.reserved_quantity:
                    raise InsufficientStockError(
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
                    description=f"Order Assembly - #{order.orderNumber} (from reservation)",
                    order_id=order.id
                )

                session.add(operation)
                operations_created.append(operation)

                # Delete the reservation since it's now converted to actual deduction
                await session.delete(reservation)

            # Only commit if requested (allows caller to control transaction)
            if commit:
                await session.commit()
            return operations_created

        except (InsufficientStockError, InventoryError):
            if commit:
                await session.rollback()
            raise
        except Exception as e:
            if commit:
                await session.rollback()
            raise InventoryError(f"Failed to convert reservations to deductions: {str(e)}")

    @staticmethod
    async def _process_legacy_warehouse_deductions(
        session: AsyncSession,
        order: Order
    ) -> List[WarehouseOperation]:
        """
        Legacy warehouse deductions for orders without reservations.
        Used for backward compatibility.

        Args:
            session: Database session
            order: Order object

        Returns:
            List of created warehouse operations
        """
        # Get all order items
        items_result = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order_items = items_result.scalars().all()

        if not order_items:
            raise InventoryError("Order has no items to assemble")

        # Collect all warehouse deductions needed
        warehouse_deductions = {}

        for item in order_items:
            # Get product recipes for this item
            recipes_result = await session.execute(
                select(ProductRecipe, WarehouseItem)
                .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
                .where(ProductRecipe.product_id == item.product_id)
            )

            recipes_with_items = recipes_result.all()

            if not recipes_with_items:
                # Product has no recipe - skip deduction for this item
                continue

            # Calculate total deductions for this item quantity
            for recipe, warehouse_item in recipes_with_items:
                if recipe.is_optional:
                    continue  # Skip optional ingredients

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
        operations_created = []

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

                raise InsufficientStockError(
                    f"Insufficient stock for {warehouse_item.name}. "
                    f"Required: {total_quantity}, Available: {warehouse_item.quantity}. "
                    f"Needed for products: {products_str}"
                )

            # Update warehouse quantity
            warehouse_item.quantity -= total_quantity

            # Create detailed description
            products_detail = "; ".join([
                f"{detail['product_name']} x{detail['order_quantity']} (needs {detail['total_needed']})"
                for detail in product_details
            ])

            # Create warehouse operation record
            operation = WarehouseOperation(
                warehouse_item_id=warehouse_item_id,
                operation_type=WarehouseOperationType.SALE,
                quantity_change=-total_quantity,
                balance_after=warehouse_item.quantity,
                description=f"Order Assembly - #{order.orderNumber} - {products_detail}",
                order_id=order.id
            )

            session.add(operation)
            operations_created.append(operation)

        return operations_created

    # ===============================
    # Cleanup and Maintenance
    # ===============================

    @staticmethod
    async def cleanup_expired_reservations(
        session: AsyncSession,
        max_age_hours: int = 72,
        dry_run: bool = True
    ) -> Dict[str, int]:
        """
        Clean up expired reservations based on order age and status.

        Args:
            session: Database session
            max_age_hours: Age threshold in hours for considering reservations expired
            dry_run: If True, only report what would be cleaned, don't actually delete

        Returns:
            Dictionary with cleanup statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Find orders with reservations that meet cleanup criteria
        query = select(Order, OrderReservation).join(
            OrderReservation, Order.id == OrderReservation.order_id
        ).where(
            Order.created_at < cutoff_time
        ).where(
            # Clean up reservations for:
            # 1. NEW orders that haven't been paid (likely abandoned)
            # 2. CANCELLED orders (should have been cleaned already, but failsafe)
            Order.status.in_([OrderStatus.NEW, OrderStatus.CANCELLED])
        )

        result = await session.execute(query)
        orders_with_reservations = result.all()

        stats = {
            "orders_found": 0,
            "reservations_found": 0,
            "reservations_deleted": 0
        }

        if not orders_with_reservations:
            return stats

        # Group by order for processing
        orders_to_clean = {}

        for order, reservation in orders_with_reservations:
            if order.id not in orders_to_clean:
                orders_to_clean[order.id] = {
                    'order': order,
                    'reservations': []
                }
            orders_to_clean[order.id]['reservations'].append(reservation)

        stats["orders_found"] = len(orders_to_clean)
        stats["reservations_found"] = len(orders_with_reservations)

        if not dry_run:
            # Actually delete the reservations
            deleted_count = 0
            for order_id, data in orders_to_clean.items():
                for reservation in data['reservations']:
                    await session.delete(reservation)
                    deleted_count += 1

            await session.commit()
            stats["reservations_deleted"] = deleted_count

        return stats

    @staticmethod
    async def get_inventory_summary(
        session: AsyncSession
    ) -> Dict:
        """
        Get comprehensive inventory summary with reservations.

        Args:
            session: Database session

        Returns:
            Dictionary with inventory statistics
        """
        # Get all warehouse items with their reservations
        warehouse_items_result = await session.execute(
            select(WarehouseItem)
        )
        warehouse_items = warehouse_items_result.scalars().all()

        # Get all warehouse item IDs for batch reservation lookup
        warehouse_item_ids = [item.id for item in warehouse_items]
        reserved_quantities = await InventoryService.get_reserved_quantities(
            session, warehouse_item_ids
        )

        # Calculate summary statistics
        total_items = len(warehouse_items)
        total_stock_value = 0
        low_stock_items = 0
        items_with_reservations = 0
        total_reserved_quantity = 0

        detailed_items = []

        for item in warehouse_items:
            reserved_qty = reserved_quantities.get(item.id, 0)
            available_qty = item.quantity - reserved_qty
            item_value = item.quantity * item.cost_price

            total_stock_value += item_value
            total_reserved_quantity += reserved_qty

            if reserved_qty > 0:
                items_with_reservations += 1

            if available_qty <= (item.min_quantity or 10):
                low_stock_items += 1

            detailed_items.append({
                "id": item.id,
                "name": item.name,
                "total_quantity": item.quantity,
                "reserved_quantity": reserved_qty,
                "available_quantity": available_qty,
                "min_quantity": item.min_quantity,
                "is_low_stock": available_qty <= (item.min_quantity or 10),
                "cost_price": item.cost_price,
                "retail_price": item.retail_price,
                "total_value": item_value
            })

        return {
            "summary": {
                "total_items": total_items,
                "total_stock_value": total_stock_value,
                "low_stock_items": low_stock_items,
                "items_with_reservations": items_with_reservations,
                "total_reserved_quantity": total_reserved_quantity
            },
            "items": detailed_items
        }

    # ===============================
    # Utility Methods
    # ===============================

    @staticmethod
    async def validate_order_items_stock(
        session: AsyncSession,
        order_items: List[OrderItemRequest]
    ) -> List[str]:
        """
        Validate that all order items have sufficient stock.
        Returns list of error messages for insufficient items.

        Args:
            session: Database session
            order_items: List of order items to validate

        Returns:
            List of error messages (empty if all valid)
        """
        availability = await InventoryService.check_batch_availability(session, order_items)

        errors = []
        if not availability.available:
            errors.extend(availability.warnings)

        return errors

    @staticmethod
    async def get_product_max_quantity(
        session: AsyncSession,
        product_id: int
    ) -> int:
        """
        Get maximum quantity that can be produced for a product.

        Args:
            session: Database session
            product_id: Product ID

        Returns:
            Maximum quantity that can be produced
        """
        availability = await InventoryService.check_product_availability(
            session, product_id, 1  # Check for 1 to get max_quantity
        )
        return availability.max_quantity