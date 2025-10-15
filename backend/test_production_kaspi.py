#!/usr/bin/env python3
"""Test Kaspi Pay integration on production"""
import requests
import json

BASE_URL = "https://figma-product-catalog-production.up.railway.app/api/v1"

def create_test_order():
    """Create test order with Kaspi payment"""
    print("🚀 Creating test order with Kaspi payment on production...")

    order_data = {
        "customerName": "+77015211545",
        "phone": "+77015211545",
        "delivery_date": "2025-10-20",
        "delivery_time": "15:00",
        "delivery_address": "Production Test Address, Almaty",
        "recipient_name": "Production Test Recipient",
        "items": [{"product_id": 1, "quantity": 1}],
        "total_kopecks": 900000,  # 9000 tenge
        "delivery_type": "delivery",
        "payment_method": "kaspi",
        "check_availability": False
    }

    response = requests.post(
        f"{BASE_URL}/orders/public/create?shop_id=8",
        json=order_data
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Order created successfully!")
        print(f"   Order Number: {data.get('orderNumber')}")
        print(f"   Tracking ID: {data.get('tracking_id')}")
        print(f"   Kaspi Payment ID: {data.get('kaspi_payment_id')}")
        print(f"   Total: {data.get('total', 0)/100} тенге")

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def check_order_status(tracking_id):
    """Check order status"""
    print(f"\n📋 Checking order status...")

    response = requests.get(f"{BASE_URL}/orders/track/{tracking_id}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Order Status: {data.get('status')}")
        print(f"   Kaspi Payment Status: {data.get('kaspi_payment_status')}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def main():
    print("="*60)
    print("PRODUCTION KASPI PAY INTEGRATION TEST")
    print("="*60)

    # Create order
    order = create_test_order()

    if not order:
        print("❌ Failed to create order")
        return

    tracking_id = order.get('tracking_id')
    kaspi_payment_id = order.get('kaspi_payment_id')

    if not kaspi_payment_id:
        print("❌ No Kaspi Payment ID generated")
        return

    # Check order status
    check_order_status(tracking_id)

    print("\n" + "="*60)
    print(f"✅ Test completed!")
    print(f"   Next steps:")
    print(f"   1. Pay via Kaspi mobile app (Payment ID: {kaspi_payment_id})")
    print(f"   2. Wait 2 minutes for polling service to detect payment")
    print(f"   3. Check order status: {BASE_URL}/orders/track/{tracking_id}")
    print("="*60)

if __name__ == "__main__":
    main()
