"""
Kaspi Pay Integration Test

Simple test script to verify Kaspi payment integration.
Creates a test order with 17 KZT payment via Kaspi Pay.

Usage:
    python3 test_kaspi_payment.py

Test parameters:
    - Phone: 77015211545
    - Amount: 17 KZT (1700 kopecks)
    - Payment method: kaspi
"""
import asyncio
import httpx
from datetime import datetime, timedelta


async def create_test_order():
    """Create test order with Kaspi payment"""
    print("=" * 70)
    print("Kaspi Pay Integration Test - Creating Order")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Step 1: Login to get token
            print("\n[1/2] Logging in...")
            login_response = await client.post(
                "http://localhost:8014/api/v1/auth/login",
                json={
                    "phone": "+77015211545",  # Note: phone with + prefix
                    "password": "1234"  # Test password from seeds
                }
            )

            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return None

            token = login_response.json()["access_token"]
            print("✅ Logged in successfully")

            # Step 2: Create order
            print("\n[2/2] Creating test order...")
            order_response = await client.post(
                "http://localhost:8014/api/v1/orders/with-items",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "customerName": "Test Kaspi Customer",
                    "phone": "77015211545",
                    "delivery_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "delivery_address": "Almaty, Test Street 1",
                    "delivery_type": "delivery",
                    "payment_method": "kaspi",
                    "items": [
                        {
                            "product_id": 1,  # snake_case, backend will look up price
                            "quantity": 1
                        }
                    ],
                    "notes": "Test order for Kaspi Pay integration (17 KZT)"
                }
            )

            if order_response.status_code not in [200, 201]:
                print(f"❌ Order creation failed: {order_response.status_code}")
                print(f"   Response: {order_response.text}")
                return None

            order_data = order_response.json()

            # Display order details
            print("\n" + "=" * 70)
            print("✅ Order Created Successfully!")
            print("=" * 70)
            print(f"\n📦 Order Details:")
            print(f"   Order Number: {order_data['orderNumber']}")
            print(f"   Order ID: {order_data['id']}")
            print(f"   Status: {order_data['status']}")
            print(f"   Total: {order_data['total'] / 100:.2f} KZT")

            print(f"\n💳 Kaspi Payment Details:")
            kaspi_payment_id = order_data.get('kaspi_payment_id')
            if kaspi_payment_id:
                print(f"   Payment ID: {kaspi_payment_id}")
                print(f"   Payment Status: {order_data.get('kaspi_payment_status', 'N/A')}")
                print(f"   Created At: {order_data.get('kaspi_payment_created_at', 'N/A')}")
            else:
                print("   ⚠️ Payment ID not created (check logs for errors)")

            print(f"\n📱 Customer:")
            print(f"   Name: {order_data.get('customerName', 'N/A')}")
            print(f"   Phone: {order_data.get('phone', 'N/A')}")

            print(f"\n📅 Delivery:")
            print(f"   Date: {order_data.get('delivery_date', 'N/A')}")
            print(f"   Type: {order_data.get('delivery_type', 'N/A')}")
            print(f"   Address: {order_data.get('delivery_address', 'N/A')}")

            print("\n" + "=" * 70)
            print("Next Steps:")
            print("=" * 70)
            print(f"1. Payment created with ID: {kaspi_payment_id}")
            print(f"2. Polling service will check status every 2 minutes")
            print(f"3. To pay: Use Kaspi app with phone 77015211545")
            print(f"4. Amount to pay: 17 KZT")
            print(f"\n5. Monitor logs:")
            print(f"   tail -f backend.log | grep kaspi")
            print(f"\n6. Check order status after payment:")
            print(f"   curl http://localhost:8014/api/v1/orders/{order_data['id']}")
            print("=" * 70)

            return order_data

        except httpx.RequestError as e:
            print(f"❌ Request failed: {e}")
            print("   Make sure backend is running on http://localhost:8014")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None


async def check_order_status(order_id: int):
    """Check order status"""
    print(f"\n🔍 Checking order status (ID: {order_id})...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Login first
            login_response = await client.post(
                "http://localhost:8014/api/v1/auth/login",
                json={"phone": "+77015211545", "password": "1234"}  # Note: + prefix
            )
            token = login_response.json()["access_token"]

            # Get order
            order_response = await client.get(
                f"http://localhost:8014/api/v1/orders/{order_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            if order_response.status_code == 200:
                order = order_response.json()
                print(f"   Order Status: {order['status']}")
                print(f"   Payment Status: {order.get('kaspi_payment_status', 'N/A')}")
                if order.get('kaspi_payment_completed_at'):
                    print(f"   Payment Completed: {order['kaspi_payment_completed_at']}")
                return order
            else:
                print(f"   ❌ Failed to get order: {order_response.status_code}")
                return None

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None


async def monitor_order(order_id: int, duration_seconds: int = 300):
    """Monitor order for specified duration"""
    print("\n" + "=" * 70)
    print(f"Monitoring Order {order_id}")
    print("=" * 70)
    print(f"Duration: {duration_seconds} seconds ({duration_seconds // 60} minutes)")
    print(f"Checking every 15 seconds...")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 70)

    start_time = datetime.now()
    last_payment_status = None
    last_order_status = None
    checks = 0

    try:
        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            checks += 1
            elapsed = int((datetime.now() - start_time).total_seconds())

            print(f"\n[Check #{checks}] Elapsed: {elapsed}s / {duration_seconds}s")

            order = await check_order_status(order_id)

            if order:
                current_payment_status = order.get('kaspi_payment_status')
                current_order_status = order['status']

                # Check for status changes
                if current_payment_status != last_payment_status:
                    print(f"\n   🔄 Payment Status Changed:")
                    print(f"      {last_payment_status} → {current_payment_status}")
                    last_payment_status = current_payment_status

                if current_order_status != last_order_status:
                    print(f"\n   🔄 Order Status Changed:")
                    print(f"      {last_order_status} → {current_order_status}")
                    last_order_status = current_order_status

                # Check if payment is complete
                if current_payment_status == "Processed":
                    print("\n" + "=" * 70)
                    print("✅ PAYMENT CONFIRMED!")
                    print("=" * 70)
                    print(f"   Order Status: {current_order_status}")
                    print(f"   Payment Status: {current_payment_status}")
                    if order.get('kaspi_payment_completed_at'):
                        print(f"   Completed At: {order['kaspi_payment_completed_at']}")
                    print("=" * 70)
                    return True
                elif current_payment_status == "Error":
                    print("\n" + "=" * 70)
                    print("❌ PAYMENT ERROR")
                    print("=" * 70)
                    return False

            await asyncio.sleep(15)

        print("\n" + "=" * 70)
        print(f"⏱️ Monitoring timeout ({duration_seconds}s)")
        print(f"   Final payment status: {last_payment_status}")
        print(f"   Final order status: {last_order_status}")
        print("=" * 70)
        return False

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("⚠️ Monitoring stopped by user")
        print("=" * 70)
        return False


async def main():
    """Main test flow"""
    # Create test order
    order = await create_test_order()

    if not order:
        print("\n❌ Test failed: Could not create order")
        return

    order_id = order['id']

    # Ask user if they want to monitor
    print("\n" + "=" * 70)
    response = input("Do you want to monitor this order? (y/n): ").lower()

    if response == 'y':
        # Monitor for 5 minutes
        await monitor_order(order_id, duration_seconds=300)
    else:
        print("\nTest completed. Order created successfully.")
        print(f"You can manually check order status with:")
        print(f"  python3 test_kaspi_payment.py --check {order_id}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        # Check specific order
        order_id = int(sys.argv[2])
        asyncio.run(check_order_status(order_id))
    else:
        # Run full test
        asyncio.run(main())
