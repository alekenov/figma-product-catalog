"""Quick test script for Production API without MCP."""

import asyncio
import sys
sys.path.append('../mcp-shared')

from client import CvetyProductionClient
from mcp_shared.utils.logging import setup_logging, get_logger

setup_logging(level="INFO")
logger = get_logger(__name__)


async def test_api():
    """Test Production API endpoints."""

    client = CvetyProductionClient()

    print("\n" + "="*60)
    print("Testing cvety.kz Production API")
    print("="*60 + "\n")

    # Test 1: List products
    print("1️⃣ Testing GET /products...")
    try:
        response = await client.get("/products", {"limit": 5, "cityId": 2})
        products = response.get("data", [])
        print(f"   ✅ SUCCESS: Found {len(products)} products")
        if products:
            first = products[0]
            print(f"   📦 Example: {first.get('title')} - {first.get('price')}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print()

    # Test 2: List orders
    print("2️⃣ Testing GET /orders...")
    try:
        response = await client.get("/orders", {"limit": 5})
        orders = response.get("data", [])
        print(f"   ✅ SUCCESS: Found {len(orders)} orders")
        if orders:
            first = orders[0]
            print(f"   📋 Example: Order #{first.get('number')} - {first.get('status_name')}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print()

    # Test 3: Shop info
    print("3️⃣ Testing GET /shop-info...")
    try:
        response = await client.get("/shop-info")
        shop = response.get("data", {})
        print(f"   ✅ SUCCESS: Shop '{shop.get('name')}'")
        print(f"   🏪 Address: {shop.get('address')}")
        print(f"   📞 Phone: {shop.get('phone')}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print()

    # Test 4: Inventory
    print("4️⃣ Testing GET /inventory...")
    try:
        response = await client.get("/inventory")
        items = response.get("data", [])
        print(f"   ✅ SUCCESS: Found {len(items)} inventory items")
        if items:
            first = items[0]
            print(f"   📦 Example: {first.get('name')} - qty: {first.get('quantity')}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print()

    # Test 5: Customers
    print("5️⃣ Testing GET /customers...")
    try:
        response = await client.get("/customers", {"limit": 3})
        customers = response.get("data", [])
        print(f"   ✅ SUCCESS: Found {len(customers)} customers")
        if customers:
            first = customers[0]
            print(f"   👤 Example: {first.get('NAME')} - {first.get('total_orders')} orders")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("\n" + "="*60)
    print("API Test Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_api())
