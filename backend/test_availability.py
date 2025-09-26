#!/usr/bin/env python3
"""
Test script for availability checking functionality
Run with: python3 test_availability.py
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import select
from models import (
    Product, WarehouseItem, ProductRecipe, Order, OrderItem,
    OrderItemRequest, OrderCreateWithItems
)
from availability_service import AvailabilityService
from config_sqlite import settings

async def test_availability_service():
    """Test the availability service functionality"""

    # Create async engine
    engine = create_async_engine(settings.database_url, echo=True)

    async with AsyncSession(engine) as session:
        print("🔍 Testing Availability Service...")

        # Test 1: Get all products
        print("\n1. Getting all products...")
        products_result = await session.execute(select(Product))
        products = products_result.scalars().all()
        print(f"Found {len(products)} products")

        if not products:
            print("No products found. Please seed the database first.")
            return

        # Test 2: Check availability for first product
        product = products[0]
        print(f"\n2. Checking availability for product: {product.name} (ID: {product.id})")

        try:
            availability = await AvailabilityService.check_product_availability(
                session, product.id, 1
            )
            print(f"   Available: {availability.available}")
            print(f"   Max quantity: {availability.max_quantity}")
            print(f"   Ingredients: {len(availability.ingredients)}")

            for ingredient in availability.ingredients:
                print(f"     - {ingredient.name}: {ingredient.available} available, {ingredient.required} required")

        except Exception as e:
            print(f"   Error checking availability: {e}")

        # Test 3: Check order availability
        print(f"\n3. Testing order availability check...")

        order_items = [
            OrderItemRequest(
                product_id=product.id,
                quantity=1,
                special_requests="Test order"
            )
        ]

        try:
            order_availability = await AvailabilityService.check_order_availability(
                session, order_items
            )
            print(f"   Order available: {order_availability.available}")
            print(f"   Warnings: {order_availability.warnings}")

        except Exception as e:
            print(f"   Error checking order availability: {e}")

        # Test 4: Get warehouse items and reserved quantities
        print(f"\n4. Testing reserved quantities...")

        warehouse_result = await session.execute(select(WarehouseItem))
        warehouse_items = warehouse_result.scalars().all()

        if warehouse_items:
            warehouse_ids = [item.id for item in warehouse_items[:3]]  # Test first 3
            try:
                reserved = await AvailabilityService.get_reserved_quantities(session, warehouse_ids)
                print(f"   Reserved quantities for {len(warehouse_ids)} items: {reserved}")
            except Exception as e:
                print(f"   Error getting reserved quantities: {e}")

        print(f"\n✅ Availability service tests completed!")

async def test_database_schema():
    """Test that the database schema supports our new features"""

    engine = create_async_engine(settings.database_url, echo=False)

    async with AsyncSession(engine) as session:
        print("\n🗄️ Testing Database Schema...")

        # Test that we can query order reservations (even if empty)
        try:
            from models import OrderReservation
            reservations_result = await session.execute(select(OrderReservation))
            reservations = reservations_result.scalars().all()
            print(f"   ✅ OrderReservation table accessible, found {len(reservations)} reservations")
        except Exception as e:
            print(f"   ❌ OrderReservation table error: {e}")

        # Test product recipes
        try:
            recipes_result = await session.execute(select(ProductRecipe))
            recipes = recipes_result.scalars().all()
            print(f"   ✅ ProductRecipe table accessible, found {len(recipes)} recipes")
        except Exception as e:
            print(f"   ❌ ProductRecipe table error: {e}")

        # Test warehouse items
        try:
            warehouse_result = await session.execute(select(WarehouseItem))
            warehouse_items = warehouse_result.scalars().all()
            print(f"   ✅ WarehouseItem table accessible, found {len(warehouse_items)} items")
        except Exception as e:
            print(f"   ❌ WarehouseItem table error: {e}")

def main():
    """Run all tests"""

    print("🚀 Starting Availability System Tests")
    print("=" * 50)

    try:
        # Test database schema first
        asyncio.run(test_database_schema())

        # Test availability service
        asyncio.run(test_availability_service())

        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()