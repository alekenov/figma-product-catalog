"""
Test script to create an order and verify update_order functionality
"""
import httpx
import asyncio
from datetime import datetime, timedelta

MCP_URL = "http://localhost:8000"

async def test_order_flow():
    """Test creating and updating an order via MCP"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 60)
        print("Test: Create Order and Update Order Flow")
        print("=" * 60)

        # Step 1: Create a public order (no auth needed)
        print("\n📝 Step 1: Creating test order for shop_id=8...")

        # Get tomorrow's date for delivery
        # Note: MCP create_order supports natural language dates
        create_response = await client.post(
            f"{MCP_URL}/call-tool",
            json={
                "name": "create_order",
                "arguments": {
                    "shop_id": 8,
                    "customer_name": "Айгуль Тестовая",
                    "customer_phone": "77012345678",
                    "delivery_address": "ул. Абая, дом 10, кв. 5",
                    "delivery_date": "завтра",  # Natural language: "tomorrow"
                    "delivery_time": "днем",     # Natural language: "afternoon" (14:00)
                    "items": [
                        {
                            "product_id": 21,
                            "quantity": 1
                        }
                    ],
                    "total_price": 1800000,  # Product 21 costs 1,800,000 tiyins (18,000 tenge)
                    "notes": "Тестовый заказ для проверки update_order"
                }
            }
        )

        if create_response.status_code != 200:
            print(f"❌ Failed to create order: {create_response.status_code}")
            print(create_response.text)
            return

        result = create_response.json()
        if "result" not in result:
            print(f"❌ Unexpected response format: {result}")
            return

        order_data = result["result"]
        tracking_id = order_data.get("tracking_id")
        order_id = order_data.get("id")

        print(f"✅ Order created successfully!")
        print(f"   Order ID: {order_id}")
        print(f"   Tracking ID: {tracking_id}")
        print(f"   Customer: {order_data.get('customerName')}")
        print(f"   Delivery: {order_data.get('delivery_date')} at {order_data.get('scheduled_time')}")
        print(f"   Address: {order_data.get('delivery_address')}")

        # Step 2: Login to get admin token
        print("\n🔐 Step 2: Logging in as admin...")
        login_response = await client.post(
            f"{MCP_URL}/call-tool",
            json={
                "name": "login",
                "arguments": {
                    "phone": "77015211545",
                    "password": "password"
                }
            }
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return

        login_result = login_response.json()
        token = login_result["result"]["access_token"]
        print(f"✅ Logged in successfully")

        # Step 3: Update the order (change delivery address)
        print(f"\n🔄 Step 3: Updating order {tracking_id}...")
        new_address = "ул. Сатпаева, дом 45, кв. 12"

        update_response = await client.post(
            f"{MCP_URL}/call-tool",
            json={
                "name": "update_order",
                "arguments": {
                    "token": token,
                    "order_id": order_id,
                    "delivery_address": new_address
                }
            }
        )

        if update_response.status_code != 200:
            print(f"❌ Failed to update order: {update_response.status_code}")
            print(update_response.text)
            return

        update_result = update_response.json()
        if "result" not in update_result:
            print(f"❌ Unexpected response format: {update_result}")
            return

        updated_order = update_result["result"]
        print(f"✅ Order updated successfully!")
        print(f"   New address: {updated_order.get('delivery_address')}")

        # Step 4: Verify the update by tracking the order
        print(f"\n🔍 Step 4: Verifying update by tracking order...")
        track_response = await client.post(
            f"{MCP_URL}/call-tool",
            json={
                "name": "track_order_by_phone",
                "arguments": {
                    "shop_id": 8,
                    "customer_phone": "77012345678",
                    "tracking_id": tracking_id
                }
            }
        )

        if track_response.status_code != 200:
            print(f"❌ Failed to track order: {track_response.status_code}")
            return

        track_result = track_response.json()
        tracked_order = track_result["result"]

        print(f"✅ Order tracked successfully!")
        print(f"   Current address: {tracked_order.get('delivery_address')}")
        print(f"   Status: {tracked_order.get('status')}")

        # Verify address was actually updated
        if tracked_order.get('delivery_address') == new_address:
            print("\n" + "=" * 60)
            print("🎉 SUCCESS: update_order is working correctly!")
            print(f"   Tracking ID to use in tests: {tracking_id}")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  WARNING: Address was not updated")
            print(f"   Expected: {new_address}")
            print(f"   Got: {tracked_order.get('delivery_address')}")
            print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_order_flow())
