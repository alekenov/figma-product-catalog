#!/usr/bin/env python3
"""Initialize warehouse with sample data"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlmodel import select
from database import get_session
from models import WarehouseItem, WarehouseOperation, WarehouseOperationType
from datetime import datetime, timedelta
from utils import tenge_to_kopecks


async def init_warehouse():
    """Initialize warehouse with sample items"""

    async for session in get_session():
        # Check if warehouse already has items
        result = await session.execute(select(WarehouseItem))
        existing_items = result.scalars().all()

        if existing_items:
            print("✅ Warehouse already has items")
            return

        # Create sample warehouse items
        items_data = [
            {
                "name": "Красная роза",
                "quantity": 150,
                "cost_price": 150,
                "retail_price": 200,
                "image": "https://images.unsplash.com/photo-1518621736915-f3b1c41bfd00?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=2),
                "min_quantity": 20
            },
            {
                "name": "Белая роза",
                "quantity": 75,
                "cost_price": 170,
                "retail_price": 220,
                "image": "https://images.unsplash.com/photo-1560717789-0ac7c58ac90a?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=2),
                "min_quantity": 20
            },
            {
                "name": "Розовая роза",
                "quantity": 120,
                "cost_price": 140,
                "retail_price": 180,
                "image": "https://images.unsplash.com/photo-1576668576260-db31b601ab13?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=3),
                "min_quantity": 20
            },
            {
                "name": "Белая орхидея",
                "quantity": 25,
                "cost_price": 1200,
                "retail_price": 1500,
                "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=4),
                "min_quantity": 5
            },
            {
                "name": "Розовая лилия",
                "quantity": 40,
                "cost_price": 350,
                "retail_price": 450,
                "image": "https://images.unsplash.com/photo-1530426509291-d831d721c7b2?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=4),
                "min_quantity": 10
            },
            {
                "name": "Белая хризантема",
                "quantity": 60,
                "cost_price": 250,
                "retail_price": 300,
                "image": "https://images.unsplash.com/photo-1606418251192-78f9715c3aa3?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=5),
                "min_quantity": 15
            },
            {
                "name": "Эвкалипт (ветка)",
                "quantity": 200,
                "cost_price": 100,
                "retail_price": 150,
                "image": "https://images.unsplash.com/photo-1565011523534-747a8601f10a?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=3),
                "min_quantity": 30
            },
            {
                "name": "Желтая роза",
                "quantity": 50,
                "cost_price": 160,
                "retail_price": 210,
                "image": "https://images.unsplash.com/photo-1560717845-cdc3f7b3b923?w=200&h=240&fit=crop",
                "last_delivery_date": datetime.now() - timedelta(days=2),
                "min_quantity": 15
            }
        ]

        print("📦 Creating warehouse items...")

        for item_data in items_data:
            # Convert tenge prices to kopecks for storage
            item_data_kopecks = item_data.copy()
            item_data_kopecks['cost_price'] = tenge_to_kopecks(item_data['cost_price'])
            item_data_kopecks['retail_price'] = tenge_to_kopecks(item_data['retail_price'])

            # Create warehouse item
            item = WarehouseItem(**item_data_kopecks)
            session.add(item)
            await session.commit()
            await session.refresh(item)

            # Create initial delivery operation
            operation = WarehouseOperation(
                warehouse_item_id=item.id,
                operation_type=WarehouseOperationType.DELIVERY,
                quantity_change=item.quantity,
                balance_after=item.quantity,
                description=f"Начальная поставка: {item.quantity} шт"
            )
            session.add(operation)

            print(f"  ✅ Created: {item.name} - {item.quantity} шт")

        await session.commit()
        print("\n🎉 Warehouse initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_warehouse())