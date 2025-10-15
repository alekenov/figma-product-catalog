#!/usr/bin/env python3
"""
Test Order Status Changes and Kaspi Pay Refund
"""
import requests
import json

BASE_URL = "http://localhost:8014/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicGhvbmUiOiI3NzAxNTIxMTU0NSIsInJvbGUiOiJBRE1JTiIsInNob3BfaWQiOjgsImV4cCI6MTc2MTEyNzA1Mn0.G5-4WjZtuGVkaP_S-wp43xf8EGihCJRY4DUKZiFjxaY"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. List all orders to find Order #00091
print("🔍 Finding Order #00091...")
response = requests.get(f"{BASE_URL}/orders/", headers=headers)
if response.status_code == 200:
    orders = response.json()
    print(f"📋 Total orders found: {len(orders)}")

    # Print all order numbers for debugging
    if orders:
        print("   Available orders:")
        for order in orders[:10]:  # Show first 10
            print(f"     - {order.get('orderNumber')} (ID: {order.get('id')}, Status: {order.get('status')})")

    target_order = None
    for order in orders:
        if order.get("orderNumber") in ["00091", "#00091"]:  # Handle both formats
            target_order = order
            break

    if target_order:
        print(f"✅ Found Order #00091")
        print(f"   ID: {target_order['id']}")
        print(f"   Status: {target_order['status']}")
        print(f"   Kaspi Payment ID: {target_order.get('kaspi_payment_id')}")
        print(f"   Kaspi Payment Status: {target_order.get('kaspi_payment_status')}")

        order_id = target_order['id']

        # 2. Update order status to accepted (lowercase!)
        print(f"\n📝 Updating order status to accepted...")
        update_response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            headers=headers,
            params={"status": "accepted"}  # Lowercase status value
        )

        if update_response.status_code == 200:
            updated_order = update_response.json()
            print(f"✅ Order status updated to: {updated_order['status']}")
        else:
            print(f"❌ Failed to update status: {update_response.status_code}")
            print(f"   Response: {update_response.text}")

        # 3. Check Kaspi payment details
        kaspi_payment_id = target_order.get('kaspi_payment_id')
        if kaspi_payment_id:
            print(f"\n💳 Checking Kaspi payment details...")
            kaspi_response = requests.get(
                f"{BASE_URL}/kaspi/details/{kaspi_payment_id}"
            )

            if kaspi_response.status_code == 200:
                payment_details = kaspi_response.json()
                print(f"✅ Payment Details:")
                print(f"   External ID: {payment_details.get('ExternalId')}")
                print(f"   Status: {payment_details.get('Status')}")
                print(f"   Total Amount: {payment_details.get('TotalAmount')} tenge")
                print(f"   Available Return Amount: {payment_details.get('AvailableReturnAmount')} tenge")
            else:
                print(f"❌ Failed to get payment details: {kaspi_response.status_code}")
                print(f"   Response: {kaspi_response.text}")
    else:
        print("❌ Order #00091 not found")
else:
    print(f"❌ Failed to list orders: {response.status_code}")
    print(f"   Response: {response.text}")
