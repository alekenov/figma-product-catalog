#!/usr/bin/env python3
"""
Comprehensive test script for all 7 Telegram notification types.
Tests Product Analytics & Monitoring system end-to-end.

Usage:
    python3 test_notifications.py
"""
import requests
import time
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8014/api/v1"
SUPERADMIN_PHONE = "+77015211545"
SUPERADMIN_PASSWORD = "1234"  # Superadmin password from seeds/superadmin.py

# Test data - use timestamp to ensure unique phone
import random
timestamp = int(time.time()) % 10000
test_phone = f"+77777{timestamp:03d}99"  # Unique phone: +77777XXXYYY
TEST_USER = {
    "name": "Test Notification Shop",
    "phone": test_phone,
    "password": "test123456",
    "city": "Astana"
}


def print_step(step_num, description):
    """Print formatted test step"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}\n")


def wait_for_notification():
    """Wait between notifications for readability"""
    print("⏳ Waiting 2 seconds for notification to arrive...")
    time.sleep(2)


def test_1_registration():
    """Test 1: New registration notification"""
    print_step(1, "NEW REGISTRATION NOTIFICATION")

    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)

    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ User registered successfully")
        print(f"   User ID: {user_data['id']}")
        print(f"   Name: {user_data['name']}")
        print(f"   Phone: {user_data['phone']}")
        wait_for_notification()

        # Now login to get token and shop_id
        print("   Logging in to get access token...")
        login_payload = {"phone": TEST_USER["phone"], "password": TEST_USER["password"]}
        print(f"   Login payload: {login_payload}")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_payload
        )

        print(f"   Login status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"   Login data keys: {list(login_data.keys())}")

            # Extract shop_id from JWT token payload
            import base64
            token = login_data["access_token"]
            payload = token.split('.')[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.b64decode(payload))
            shop_id = decoded.get("shop_id")
            print(f"   Shop ID from token: {shop_id}")

            return {
                "token": token,
                "shop_id": shop_id
            }
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return None
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return None


def test_2_name_change(token, shop_id):
    """Test 2: Shop name changed notification"""
    print_step(2, "SHOP NAME CHANGED NOTIFICATION")

    response = requests.put(
        f"{BASE_URL}/shop/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "🌸 Notification Test Flowers"}
    )

    if response.status_code == 200:
        print(f"✅ Shop name changed successfully")
        wait_for_notification()
        return True
    else:
        print(f"❌ Name change failed: {response.status_code}")
        print(response.text)
        return False


def test_3_first_product(token):
    """Test 3: First product added notification"""
    print_step(3, "FIRST PRODUCT ADDED NOTIFICATION")

    product_data = {
        "name": "Тестовый букет роз",
        "type": "flowers",
        "price": 5000,
        "description": "Красивые красные розы для теста",
        "enabled": True
    }

    response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        json=product_data
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ First product added successfully")
        print(f"   Product ID: {data['id']}")
        print(f"   Name: {data['name']}")
        print(f"   Price: {data['price']} ₸")
        wait_for_notification()
        return data['id']
    else:
        print(f"❌ Product creation failed: {response.status_code}")
        print(response.text)
        return None


def test_4_additional_product(token):
    """Test 4: Additional product added notification"""
    print_step(4, "ADDITIONAL PRODUCT ADDED NOTIFICATION")

    product_data = {
        "name": "Тестовый букет тюльпанов",
        "type": "flowers",
        "price": 6000,
        "description": "Яркие тюльпаны для теста",
        "enabled": True
    }

    response = requests.post(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        json=product_data
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Additional product added successfully")
        print(f"   Product ID: {data['id']}")
        print(f"   Name: {data['name']}")
        wait_for_notification()
        return True
    else:
        print(f"❌ Product creation failed: {response.status_code}")
        return False


def test_5_shop_opened(shop_id):
    """Test 5: Shop opened notification (via superadmin unblock)"""
    print_step(5, "SHOP OPENED NOTIFICATION")

    # First, login as superadmin
    print("   Logging in as superadmin...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": SUPERADMIN_PHONE, "password": SUPERADMIN_PASSWORD}
    )

    if login_response.status_code != 200:
        print(f"❌ Superadmin login failed: {login_response.status_code}")
        return False

    superadmin_token = login_response.json()["access_token"]

    # Block shop first (to be able to unblock it)
    print(f"   Blocking shop {shop_id}...")
    block_response = requests.put(
        f"{BASE_URL}/superadmin/shops/{shop_id}/block",
        headers={"Authorization": f"Bearer {superadmin_token}"}
    )

    if block_response.status_code != 200:
        print(f"⚠️  Block failed (might already be blocked): {block_response.status_code}")

    time.sleep(1)

    # Unblock shop (this triggers shop_opened notification)
    print(f"   Unblocking shop {shop_id}...")
    unblock_response = requests.put(
        f"{BASE_URL}/superadmin/shops/{shop_id}/unblock",
        headers={"Authorization": f"Bearer {superadmin_token}"}
    )

    if unblock_response.status_code == 200:
        print(f"✅ Shop unblocked (opened) successfully")
        wait_for_notification()
        return True
    else:
        print(f"❌ Shop unblock failed: {unblock_response.status_code}")
        print(unblock_response.text)
        return False


def test_6_onboarding_complete(token):
    """Test 6: Onboarding completed notification"""
    print_step(6, "ONBOARDING COMPLETED NOTIFICATION")

    # Add city to complete onboarding
    # Onboarding requires: name changed, city added, first product, shop opened
    response = requests.put(
        f"{BASE_URL}/shop/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"city": "Astana", "address": "Test Street 123"}
    )

    if response.status_code == 200:
        print(f"✅ City and address added - onboarding should be complete")
        wait_for_notification()
        return True
    else:
        print(f"❌ City update failed: {response.status_code}")
        print(response.text)
        return False


def test_7_first_order(shop_id, product_id):
    """Test 7: First order received notification"""
    print_step(7, "FIRST ORDER RECEIVED NOTIFICATION")

    # Create order via public API (no auth required)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    order_data = {
        "customerName": "Тестовый клиент",
        "phone": "+77771234567",
        "delivery_date": tomorrow,
        "scheduled_time": "14:00",
        "delivery_type": "delivery",
        "delivery_address": "Test delivery address, apt 42",
        "items": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ],
        "notes": "Тестовый заказ для проверки уведомлений"
    }

    response = requests.post(
        f"{BASE_URL}/orders/public/create?shop_id={shop_id}",
        json=order_data
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ First order created successfully")
        print(f"   Order Number: {data.get('orderNumber')}")
        print(f"   Tracking ID: {data.get('tracking_id')}")
        print(f"   Total: {data.get('total')} ₸")
        wait_for_notification()
        return True
    else:
        print(f"❌ Order creation failed: {response.status_code}")
        print(response.text)
        return False


def cleanup(shop_id):
    """Cleanup test data (optional)"""
    print_step("CLEANUP", "Removing test shop (optional)")

    # Login as superadmin
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": SUPERADMIN_PHONE, "password": SUPERADMIN_PASSWORD}
    )

    if login_response.status_code == 200:
        superadmin_token = login_response.json()["access_token"]

        # Block the test shop
        block_response = requests.put(
            f"{BASE_URL}/superadmin/shops/{shop_id}/block",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )

        if block_response.status_code == 200:
            print(f"✅ Test shop {shop_id} blocked for cleanup")
        else:
            print(f"⚠️  Failed to block shop: {block_response.status_code}")
    else:
        print(f"⚠️  Superadmin login failed for cleanup")


def main():
    """Run all notification tests"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   TELEGRAM NOTIFICATIONS COMPREHENSIVE TEST SUITE         ║
║                                                           ║
║   Testing all 7 notification types:                      ║
║   1. New Registration                                    ║
║   2. Shop Name Changed                                   ║
║   3. First Product Added                                 ║
║   4. Additional Product Added                            ║
║   5. Shop Opened                                         ║
║   6. Onboarding Completed                                ║
║   7. First Order Received                                ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Test sequence
    auth_data = test_1_registration()
    if not auth_data:
        print("\n❌ Tests failed at registration step")
        return

    token = auth_data["token"]
    shop_id = auth_data["shop_id"]

    test_2_name_change(token, shop_id)
    product_id = test_3_first_product(token)

    if not product_id:
        print("\n❌ Tests failed at first product step")
        return

    test_4_additional_product(token)
    test_5_shop_opened(shop_id)
    test_6_onboarding_complete(token)
    test_7_first_order(shop_id, product_id)

    # Summary
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print("\n📱 Check your Telegram channel for all 7 notifications")
    print(f"🏪 Test Shop ID: {shop_id}")
    print("\n💡 To cleanup test data, uncomment cleanup() call")

    # Uncomment to cleanup test data
    # cleanup(shop_id)


if __name__ == "__main__":
    main()
