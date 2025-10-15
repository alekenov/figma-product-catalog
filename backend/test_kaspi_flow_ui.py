#!/usr/bin/env python3
"""
Manual UI Test for Kaspi Pay Integration

This script creates test orders with Kaspi Pay and provides URLs for manual UI testing.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8014/api/v1"

def print_separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f"  {title}")
        print("="*60)

def create_order_with_kaspi():
    """Create test order with Kaspi Pay"""
    print_separator("Creating Order with Kaspi Pay")

    order_data = {
        "customerName": "UI Test Customer",
        "phone": "+77015211545",  # Admin phone - registered in Kaspi
        "delivery_date": "2025-10-20",
        "delivery_time": "15:00",
        "delivery_address": "Test Address for Kaspi UI Test",
        "recipient_name": "Test Recipient",
        "items": [{"product_id": 1, "quantity": 1}],
        "total_kopecks": 900000,  # 9000 tenge
        "delivery_type": "delivery",
        "payment_method": "kaspi",
        "check_availability": False
    }

    response = requests.post(
        f"{BASE_URL}/orders/public/create",
        params={"shop_id": 8},
        json=order_data
    )

    if response.status_code == 200:
        order = response.json()
        print("✅ Order created successfully!")
        print(f"   Order Number: {order.get('orderNumber')}")
        print(f"   Tracking ID: {order.get('tracking_id')}")
        print(f"   Order ID: {order.get('id')}")
        print(f"   Status: {order.get('status')}")
        print(f"   Payment Method: {order.get('payment_method')}")
        print(f"   Kaspi Payment ID: {order.get('kaspi_payment_id')}")

        # Save to file for later use
        with open('/tmp/test_order_tracking_id_ui.txt', 'w') as f:
            f.write(order.get('tracking_id', ''))
        with open('/tmp/test_kaspi_payment_id_ui.txt', 'w') as f:
            f.write(order.get('kaspi_payment_id', ''))

        return order
    else:
        print(f"❌ Failed to create order: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def get_admin_token():
    """Get admin JWT token"""
    print_separator("Getting Admin Token")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": "+77015211545", "password": "testpass123"}
    )

    if response.status_code == 200:
        token_data = response.json()
        print("✅ Admin login successful!")
        print(f"   User ID: {token_data.get('user', {}).get('id')}")
        print(f"   Role: {token_data.get('user', {}).get('role')}")
        return token_data.get('access_token')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def check_kaspi_payment_status(payment_id):
    """Check Kaspi payment status"""
    print_separator("Checking Kaspi Payment Status")

    response = requests.get(f"{BASE_URL}/kaspi/status/{payment_id}")

    if response.status_code == 200:
        status_data = response.json()
        print("✅ Payment status retrieved!")
        print(f"   External ID: {status_data.get('external_id')}")
        print(f"   Status: {status_data.get('status')}")
        return status_data
    else:
        print(f"❌ Failed to check status: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def print_ui_test_instructions(order):
    """Print manual UI testing instructions"""
    print_separator("Manual UI Testing Instructions")

    tracking_id = order.get('tracking_id')
    order_id = order.get('id')
    kaspi_payment_id = order.get('kaspi_payment_id')
    order_number = order.get('orderNumber')

    print("\n📱 SHOP FRONTEND (Customer View)")
    print(f"   URL: http://localhost:5180/order-status/{tracking_id}")
    print("   Tasks:")
    print("   1. Open URL in browser")
    print("   2. Check order details are correct")
    print("   3. See Kaspi Pay QR code or payment button")
    print(f"   4. Note Kaspi Payment ID: {kaspi_payment_id}")

    print("\n💳 KASPI PAY (Mobile App)")
    print("   Tasks:")
    print("   1. Open Kaspi mobile app")
    print("   2. Go to Payments section")
    print(f"   3. Enter Payment ID: {kaspi_payment_id}")
    print("   4. Pay 9000 tenge (test amount)")
    print("   5. Wait for confirmation")

    print("\n⏱️ POLLING SERVICE (Automatic)")
    print("   Tasks:")
    print("   1. Wait 2 minutes for polling service to run")
    print("   2. Or manually trigger:")
    print("   python3 -c \"from services.kaspi_polling_service import KaspiPollingService; import asyncio; asyncio.run(KaspiPollingService.check_payments_job())\"")

    print("\n🖥️ ADMIN PANEL (Staff View)")
    print(f"   URL: http://localhost:5176/orders/{order_id}")
    print("   Login: +77015211545 / testpass123")
    print("   Tasks:")
    print(f"   1. Find order {order_number}")
    print("   2. Check Kaspi Payment ID is visible")
    print("   3. Wait for status to change to PAID")
    print("   4. Change status: PAID → ACCEPTED")
    print("   5. Change status: ACCEPTED → ASSEMBLED")
    print("   6. Change status: ASSEMBLED → IN_DELIVERY")
    print("   7. Change status: IN_DELIVERY → DELIVERED")

    print("\n💰 REFUND TESTING (Admin Panel)")
    print("   Tasks:")
    print("   1. Click 'Refund' button in order details")
    print("   2. Enter 4500 tenge (50% refund)")
    print("   3. Confirm refund → Should succeed")
    print("   4. Try second refund: 4500 tenge (remaining 50%)")
    print("   5. Confirm refund → Should succeed")
    print("   6. Try third refund: 1000 tenge (excess)")
    print("   7. Should show error: Insufficient funds")

    print("\n✅ VERIFICATION CHECKLIST")
    checklist = [
        "[ ] Order created with Kaspi payment_method",
        "[ ] kaspi_payment_id is not None",
        "[ ] Payment ID visible in shop frontend",
        "[ ] Can pay via Kaspi mobile app",
        "[ ] Polling service updates status to PAID after 2 min",
        "[ ] Admin can see order in panel",
        "[ ] Admin can change statuses: PAID→ACCEPTED→ASSEMBLED→IN_DELIVERY→DELIVERED",
        "[ ] First refund (50%) succeeds",
        "[ ] Second refund (50%) succeeds",
        "[ ] Excess refund shows error",
        "[ ] All changes visible in both frontends"
    ]
    for item in checklist:
        print(f"   {item}")

    print()

def main():
    print("\n🚀 Kaspi Pay UI Integration Test")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Create order
    order = create_order_with_kaspi()
    if not order:
        print("\n❌ Test failed: Could not create order")
        return

    # Step 2: Check Kaspi payment status
    kaspi_payment_id = order.get('kaspi_payment_id')
    if kaspi_payment_id:
        check_kaspi_payment_status(kaspi_payment_id)
    else:
        print("\n⚠️  Warning: No Kaspi Payment ID created!")

    # Step 3: Get admin token (for reference)
    admin_token = get_admin_token()
    if admin_token:
        print(f"   Token (first 50 chars): {admin_token[:50]}...")

    # Step 4: Print UI test instructions
    print_ui_test_instructions(order)

    print_separator("Test Setup Complete")
    print("\n✅ Ready for manual UI testing!")
    print("   Follow the instructions above to complete the test.\n")

if __name__ == "__main__":
    main()
