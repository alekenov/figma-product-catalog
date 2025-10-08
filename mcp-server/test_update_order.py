#!/usr/bin/env python3
"""
Test the new update_order MCP tool.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from server import update_order


async def test_update_order():
    """Test updating an order via tracking ID."""

    print("🧪 Testing update_order MCP tool...")
    print("=" * 60)

    # Test data
    tracking_id = "903757396"

    print(f"\n1️⃣ Updating order {tracking_id}...")
    print(f"   - New address: улица Абылай хана, дом 15, офис 301")
    print(f"   - New delivery time: завтра")
    print(f"   - Delivery notes: Оставить на ресепшене\n")

    try:
        result = await update_order(
            tracking_id=tracking_id,
            delivery_address="улица Абылай хана, дом 15, офис 301",
            delivery_time="завтра",
            delivery_notes="Оставить на ресепшене"
        )

        print("✅ Order updated successfully!")
        print(f"\n📋 Updated Order:")
        print(f"   Order Number: {result.get('orderNumber')}")
        print(f"   Customer: {result.get('customerName')}")
        print(f"   Address: {result.get('delivery_address')}")
        print(f"   Delivery Notes: {result.get('delivery_notes')}")
        print(f"   Updated At: {result.get('updated_at')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_update_order())
