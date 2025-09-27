#!/usr/bin/env python3
"""Test script for batched availability checking"""

import asyncio
import json
from sqlmodel import select
from database import get_session
from services.inventory_service import InventoryService
from models import OrderItemRequest

async def test_batch_availability():
    """Test availability check with multiple products"""
    
    # Test with multiple products
    order_items = [
        OrderItemRequest(product_id=1, quantity=2),
        OrderItemRequest(product_id=2, quantity=1),
        OrderItemRequest(product_id=3, quantity=3),
        OrderItemRequest(product_id=4, quantity=1),
        OrderItemRequest(product_id=5, quantity=2)
    ]
    
    async for session in get_session():
        print("Testing batched availability check with 5 products...")
        print("=" * 50)
        
        # Check availability
        result = await InventoryService.check_batch_availability(
            session, order_items
        )
        
        # Display results
        print(f"Overall Available: {result.available}")
        print(f"Warnings: {result.warnings}")
        print("\nProduct Details:")
        for item in result.items:
            print(f"  - {item.product_name} (ID: {item.product_id})")
            print(f"    Requested: {item.quantity_requested}")
            print(f"    Available: {item.available}")
            print(f"    Max Quantity: {item.max_quantity}")
            if item.ingredients:
                print(f"    Ingredients: {len(item.ingredients)} items")
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        
        break

if __name__ == "__main__":
    asyncio.run(test_batch_availability())
