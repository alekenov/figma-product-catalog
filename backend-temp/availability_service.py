"""
Availability checking service for order management.
Handles recipe calculations and stock validation.
"""

from typing import List, Dict
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from models import (
    Product, ProductRecipe, WarehouseItem, OrderReservation,
    OrderItemRequest, ProductAvailability, IngredientAvailability, AvailabilityResponse
)


class AvailabilityService:
    """Service for checking product availability based on warehouse stock and recipes"""

    @staticmethod
    async def get_reserved_quantities(session: AsyncSession, warehouse_item_ids: List[int]) -> Dict[int, int]:
        """Get currently reserved quantities for warehouse items"""
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
    async def check_product_availability(
        session: AsyncSession,
        product_id: int,
        quantity_requested: int
    ) -> ProductAvailability:
        """Check availability for a single product"""

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

        # Get recipes with warehouse items
        recipes_result = await session.execute(
            select(ProductRecipe, WarehouseItem)
            .join(WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id)
            .where(ProductRecipe.product_id == product_id)
        )

        recipes_with_items = recipes_result.all()

        if not recipes_with_items:
            # Product has no recipe, assume it's available
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
        reserved_quantities = await AvailabilityService.get_reserved_quantities(
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
    async def check_order_availability(
        session: AsyncSession,
        order_items: List[OrderItemRequest]
    ) -> AvailabilityResponse:
        """Check availability for multiple order items using batched queries"""

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
            reservations_cache = await AvailabilityService.get_reserved_quantities(
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

    @staticmethod
    async def reserve_ingredients_for_order(
        session: AsyncSession,
        order_id: int,
        order_items: List[OrderItemRequest]
    ) -> bool:
        """Reserve warehouse items for an order"""

        # First check if everything is available
        availability = await AvailabilityService.check_order_availability(session, order_items)

        if not availability.available:
            return False

        # Create reservations for each ingredient
        for product_availability in availability.items:
            for ingredient in product_availability.ingredients:
                if ingredient.required > 0:
                    reservation = OrderReservation(
                        order_id=order_id,
                        warehouse_item_id=ingredient.warehouse_item_id,
                        reserved_quantity=ingredient.required
                    )
                    session.add(reservation)

        await session.commit()
        return True

    @staticmethod
    async def release_order_reservations(session: AsyncSession, order_id: int) -> None:
        """Release all reservations for an order"""

        reservations_result = await session.execute(
            select(OrderReservation).where(OrderReservation.order_id == order_id)
        )
        reservations = reservations_result.scalars().all()

        for reservation in reservations:
            await session.delete(reservation)

        await session.commit()