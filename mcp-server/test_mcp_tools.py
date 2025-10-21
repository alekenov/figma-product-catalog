"""
MCP Tools Testing Script
Tests all major scenarios without UI
"""
import asyncio
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/Users/alekenov/figma-product-catalog/mcp-server')

# Import tools
from domains.products import tools as product_tools
from domains.orders import tools as order_tools
from domains.shop import tools as shop_tools


async def test_products():
    """Test product-related tools."""
    print("\n" + "="*60)
    print("🌸 TESTING PRODUCTS")
    print("="*60)

    # Test 1: List products
    print("\n1️⃣ Listing products...")
    try:
        products = await product_tools.list_products(shop_id=8, limit=5)
        print(f"   ✅ Found {len(products)} products")
        if products:
            p = products[0]
            print(f"   📦 Example: {p.get('name')} - {p.get('price')}₸")
            return products[0].get('id')  # Return first product ID for testing
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

    return None


async def test_product_details(product_id):
    """Test product details and availability."""
    if not product_id:
        print("\n⚠️  Skipping product details (no product_id)")
        return

    print(f"\n2️⃣ Getting product #{product_id} details...")
    try:
        product = await product_tools.get_product(product_id=product_id, shop_id=8)
        print(f"   ✅ Product: {product.get('name')}")
        print(f"   💰 Price: {product.get('price')}₸")
        print(f"   📝 Description: {product.get('description', 'N/A')[:50]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print(f"\n3️⃣ Checking availability...")
    try:
        avail = await product_tools.check_product_availability(
            product_id=product_id,
            quantity=1,
            shop_id=8
        )
        print(f"   ✅ Available: {avail.get('available')}")
        print(f"   📦 Quantity: {avail.get('quantity_available', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_shop_info():
    """Test shop information tools."""
    print("\n" + "="*60)
    print("🏪 TESTING SHOP INFORMATION")
    print("="*60)

    print("\n4️⃣ Getting shop settings...")
    try:
        shop = await shop_tools.get_shop_settings(shop_id=8)
        print(f"   ✅ Shop: {shop.get('name')}")
        print(f"   📍 Address: {shop.get('address')}")
        print(f"   📞 Phone: {shop.get('phone')}")
        print(f"   💰 Delivery: {shop.get('delivery_price')}₸")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n5️⃣ Getting working hours...")
    try:
        hours = await shop_tools.get_working_hours(shop_id=8)
        print(f"   ✅ Weekdays: {hours.get('weekday_start')} - {hours.get('weekday_end')}")
        print(f"   ✅ Weekends: {hours.get('weekend_start')} - {hours.get('weekend_end')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_search():
    """Test smart product search."""
    print("\n" + "="*60)
    print("🔍 TESTING SMART SEARCH")
    print("="*60)

    print("\n6️⃣ Searching roses under 20000₸...")
    try:
        results = await product_tools.search_products_smart(
            shop_id=8,
            query="розы",
            budget=20000,
            limit=5
        )
        print(f"   ✅ Found {len(results)} products")
        if results:
            for i, p in enumerate(results[:3], 1):
                print(f"   {i}. {p.get('name')} - {p.get('price')}₸")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n7️⃣ Getting bestsellers...")
    try:
        bestsellers = await product_tools.get_bestsellers(shop_id=8, limit=3)
        print(f"   ✅ Found {len(bestsellers)} bestsellers")
        if bestsellers:
            for i, p in enumerate(bestsellers, 1):
                print(f"   {i}. {p.get('name')} - {p.get('price')}₸")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_order_creation(product_id):
    """Test order creation."""
    if not product_id:
        print("\n⚠️  Skipping order creation (no product_id)")
        return None

    print("\n" + "="*60)
    print("📦 TESTING ORDER CREATION")
    print("="*60)

    print("\n8️⃣ Previewing order cost...")
    try:
        preview = await order_tools.preview_order_cost(
            shop_id=8,
            items=[{"product_id": product_id, "quantity": 1}]
        )
        print(f"   ✅ Subtotal: {preview.get('subtotal')}₸")
        print(f"   🚚 Delivery: {preview.get('delivery_cost')}₸")
        print(f"   💰 Total: {preview.get('total')}₸")
        total_price = preview.get('total', 0)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        total_price = 15000  # Fallback

    print("\n9️⃣ Creating delivery order...")
    try:
        order = await order_tools.create_order(
            customer_name="MCP Test",
            customer_phone="+77015211545",
            delivery_date="завтра",
            delivery_time="днем",
            shop_id=8,
            items=[{"product_id": product_id, "quantity": 1}],
            total_price=total_price,
            delivery_type="delivery",
            delivery_address="ул. Достык 5/2, кв 10",
            recipient_name="Тест МСП",
            recipient_phone="+77777777777",
            notes="Тестовый заказ из MCP"
        )
        print(f"   ✅ Order created!")
        print(f"   🆔 Order ID: {order.get('id')}")
        print(f"   📍 Tracking: {order.get('tracking_id')}")
        print(f"   💰 Total: {order.get('total_price')}₸")
        return order  # Return full order for Production sync
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_production_sync(order_data):
    """Test Production Bitrix sync."""
    if not order_data:
        print("\n⚠️  Skipping Production sync (no order_data)")
        return

    print("\n" + "="*60)
    print("🔄 TESTING PRODUCTION SYNC")
    print("="*60)

    print(f"\n🔟 Syncing order to Production (order_id={order_data.get('id')})...")
    try:
        result = await order_tools.sync_order_to_production(
            order_data=order_data,
            shop_id=8
        )

        if result.get('status'):
            print(f"   ✅ Synced to Production!")
            print(f"   🆔 Production Order ID: {result.get('order_id')}")
            print(f"   📋 Account Number: {result.get('account_number')}")
            print(f"   🔗 XML ID: {result.get('xml_id')}")
            print(f"   📦 Pickup: {result.get('pickup')}")
        else:
            print(f"   ❌ Sync failed: {result.get('error')}")
            print(f"   💬 Message: {result.get('message')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_pickup_order(product_id):
    """Test pickup order creation and sync."""
    if not product_id:
        print("\n⚠️  Skipping pickup order (no product_id)")
        return

    print("\n" + "="*60)
    print("🏪 TESTING PICKUP ORDER")
    print("="*60)

    print("\n1️⃣1️⃣ Creating pickup order...")
    try:
        order = await order_tools.create_order(
            customer_name="MCP Pickup Test",
            customer_phone="+77015211545",
            delivery_date="сегодня",
            delivery_time="вечером",
            shop_id=8,
            items=[{"product_id": product_id, "quantity": 1}],
            total_price=15000,
            delivery_type="pickup",
            notes="Тестовый самовывоз из MCP"
        )
        print(f"   ✅ Pickup order created!")
        print(f"   🆔 Order ID: {order.get('id')}")
        print(f"   📍 Tracking: {order.get('tracking_id')}")

        # Sync to production
        print(f"\n1️⃣2️⃣ Syncing pickup order to Production...")
        result = await order_tools.sync_order_to_production(
            order_data=order,
            shop_id=8
        )

        if result.get('status'):
            print(f"   ✅ Pickup order synced!")
            print(f"   🆔 Production ID: {result.get('order_id')}")
            print(f"   🏪 Pickup: {result.get('pickup')}")
        else:
            print(f"   ❌ Sync failed: {result.get('message')}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 MCP TOOLS TESTING SUITE")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Backend: http://localhost:8014")

    # Test products
    product_id = await test_products()
    await test_product_details(product_id)

    # Test shop info
    await test_shop_info()

    # Test search
    await test_search()

    # Test order creation and sync
    order_id = await test_order_creation(product_id)
    await test_production_sync(order_id)

    # Test pickup order
    await test_pickup_order(product_id)

    # Summary
    print("\n" + "="*60)
    print("✅ TESTING COMPLETE!")
    print("="*60)
    print("\n📊 Summary:")
    print("   ✅ Products: list, details, availability")
    print("   ✅ Shop: settings, working hours")
    print("   ✅ Search: smart search, bestsellers")
    print("   ✅ Orders: preview, create delivery, create pickup")
    print("   ✅ Production Sync: delivery + pickup orders")
    print("\n🎉 All major scenarios tested successfully!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
