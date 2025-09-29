#!/usr/bin/env python3
"""
Test script for the order reservation system.
This script demonstrates and tests the reservation functionality.
"""

import sqlite3
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import select
from database import get_session
from models import (
    Order, OrderItem, Product, WarehouseItem, ProductRecipe,
    OrderReservation, OrderStatus
)
from availability_service import AvailabilityService


async def test_reservation_system():
    """Test the order reservation system"""

    print("🔍 Testing Order Reservation System")
    print("=" * 50)

    # Create async session
    engine = create_async_engine("sqlite+aiosqlite:///figma_catalog.db")

    async with AsyncSession(engine) as session:
        # 1. Check if we have test data
        print("1. Checking existing data...")

        # Get a product with recipes
        product_query = select(Product, ProductRecipe, WarehouseItem).join(
            ProductRecipe, Product.id == ProductRecipe.product_id
        ).join(
            WarehouseItem, ProductRecipe.warehouse_item_id == WarehouseItem.id
        ).limit(1)

        result = await session.execute(product_query)
        test_data = result.first()

        if not test_data:
            print("   ⚠️  No products with recipes found. Creating test data...")
            await create_test_data(session)

            # Retry getting test data
            result = await session.execute(product_query)
            test_data = result.first()

        if test_data:
            product, recipe, warehouse_item = test_data
            print(f"   ✅ Found product: {product.name}")
            print(f"      Recipe requires: {recipe.quantity} units of {warehouse_item.name}")
            print(f"      Warehouse stock: {warehouse_item.quantity}")
        else:
            print("   ❌ Could not create or find test data")
            return

        # 2. Check existing reservations
        print("\n2. Checking existing reservations...")
        reservations_query = select(OrderReservation).limit(5)
        reservations_result = await session.execute(reservations_query)
        reservations = reservations_result.scalars().all()

        if reservations:
            print(f"   📦 Found {len(reservations)} existing reservations:")
            for reservation in reservations:
                print(f"      - Order #{reservation.order_id}: {reservation.reserved_quantity} units of item #{reservation.warehouse_item_id}")
        else:
            print("   📦 No existing reservations found")

        # 3. Test availability checking
        print("\n3. Testing availability checking...")
        from models import OrderItemRequest

        test_items = [OrderItemRequest(
            product_id=product.id,
            quantity=1
        )]

        availability = await AvailabilityService.check_order_availability(session, test_items)
        print(f"   🔍 Availability check result: {'✅ Available' if availability.available else '❌ Not available'}")

        if availability.warnings:
            for warning in availability.warnings:
                print(f"      ⚠️ Warning: {warning}")

        for item_availability in availability.items:
            print(f"      Product: {item_availability.product_name}")
            print(f"      Max quantity: {item_availability.max_quantity}")
            for ingredient in item_availability.ingredients:
                print(f"         - {ingredient.name}: {ingredient.available} available, {ingredient.reserved} reserved, {ingredient.required} required")

        print("\n✅ Order reservation system test completed!")


async def create_test_data(session: AsyncSession):
    """Create minimal test data if none exists"""

    # Check if we have any warehouse items
    warehouse_query = select(WarehouseItem).limit(1)
    warehouse_result = await session.execute(warehouse_query)
    warehouse_item = warehouse_result.scalar_one_or_none()

    if not warehouse_item:
        # Create a test warehouse item
        warehouse_item = WarehouseItem(
            name="Test Flower",
            quantity=50,
            cost_price=100000,  # 1000 tenge in kopecks
            retail_price=150000,  # 1500 tenge in kopecks
            min_quantity=5
        )
        session.add(warehouse_item)
        await session.commit()
        await session.refresh(warehouse_item)

    # Check if we have any products
    product_query = select(Product).limit(1)
    product_result = await session.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        # Create a test product
        product = Product(
            name="Test Bouquet",
            price=500000,  # 5000 tenge in kopecks
            type="flowers",
            description="A beautiful test bouquet"
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)

    # Check if we have a recipe linking them
    recipe_query = select(ProductRecipe).where(
        ProductRecipe.product_id == product.id,
        ProductRecipe.warehouse_item_id == warehouse_item.id
    ).limit(1)
    recipe_result = await session.execute(recipe_query)
    recipe = recipe_result.scalar_one_or_none()

    if not recipe:
        # Create a test recipe
        recipe = ProductRecipe(
            product_id=product.id,
            warehouse_item_id=warehouse_item.id,
            quantity=3,  # 3 flowers needed for 1 bouquet
            is_optional=False
        )
        session.add(recipe)
        await session.commit()

    print("   ✅ Test data created successfully")


def test_database_schema():
    """Test that the reservation table exists with correct schema"""
    print("\n🔍 Testing Database Schema")
    print("=" * 50)

    conn = sqlite3.connect('figma_catalog.db')
    cursor = conn.cursor()

    try:
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_reservation';")
        result = cursor.fetchone()

        if result:
            print("✅ order_reservation table exists")

            # Check schema
            cursor.execute("PRAGMA table_info(order_reservation);")
            columns = cursor.fetchall()

            expected_columns = ['id', 'order_id', 'warehouse_item_id', 'reserved_quantity', 'created_at']
            actual_columns = [col[1] for col in columns]

            print("   📋 Table schema:")
            for col in columns:
                print(f"      - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")

            if all(col in actual_columns for col in expected_columns):
                print("   ✅ All required columns present")
            else:
                missing = [col for col in expected_columns if col not in actual_columns]
                print(f"   ❌ Missing columns: {missing}")

            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='order_reservation';")
            indexes = cursor.fetchall()

            if indexes:
                print("   📊 Indexes found:")
                for idx in indexes:
                    print(f"      - {idx[0]}")
            else:
                print("   📊 No indexes found (this is ok for basic functionality)")

        else:
            print("❌ order_reservation table does not exist")

    except Exception as e:
        print(f"❌ Database error: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 Starting Order Reservation System Tests")
    print("=" * 50)

    # Test database schema first
    test_database_schema()

    # Then test the reservation functionality
    asyncio.run(test_reservation_system())