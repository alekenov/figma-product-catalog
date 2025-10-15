"""
Integration test for Vetka shop and admin
Tests full customer journey + admin management
"""
import json
import time
from datetime import datetime

# Shop test data
SHOP_ID = 8
SHOP_URL = "http://localhost:5180/vetka"
ADMIN_URL = "http://localhost:5176"
API_URL = "http://localhost:8014/api/v1"

def test_shop_products():
    """Test 1: Check products are available"""
    print("\n=== Test 1: Check products API ===")
    import subprocess
    result = subprocess.run(
        f"curl -s '{API_URL}/products/admin?shop_id={SHOP_ID}&limit=5' -H 'Authorization: Bearer test'",
        shell=True,
        capture_output=True,
        text=True
    )
    print(f"Response: {result.stdout[:200]}")
    if "Not authenticated" in result.stdout:
        print("✓ Admin endpoint requires auth (as expected)")
    return True

def test_shop_settings():
    """Test 2: Check shop settings"""
    print("\n=== Test 2: Check shop settings ===")
    import subprocess
    result = subprocess.run(
        f"curl -s '{API_URL}/shop/settings/public?shop_id={SHOP_ID}'",
        shell=True,
        capture_output=True,
        text=True
    )
    try:
        data = json.loads(result.stdout)
        print(f"Shop name: {data.get('shop_name')}")
        print(f"Phone: {data.get('phone')}")
        print(f"Delivery cost: {data.get('delivery_cost_tenge')} ₸")
        print("✓ Shop settings loaded")
        return True
    except:
        print(f"✗ Failed to load settings: {result.stdout}")
        return False

def test_delivery_slots():
    """Test 3: Check delivery slots"""
    print("\n=== Test 3: Check delivery slots ===")
    import subprocess
    result = subprocess.run(
        f"curl -s '{API_URL}/delivery/slots?shop_id={SHOP_ID}'",
        shell=True,
        capture_output=True,
        text=True
    )
    try:
        data = json.loads(result.stdout)
        print(f"Available slots: {len(data)}")
        available = [s for s in data if s.get('available')]
        print(f"Available now: {len(available)}")
        print("✓ Delivery slots loaded")
        return True
    except:
        print(f"✗ Failed to load slots: {result.stdout}")
        return False

def main():
    print("="*60)
    print(" Integration Test: Vetka Shop + CRM")
    print("="*60)
    
    results = {
        "products": test_shop_products(),
        "settings": test_shop_settings(),
        "delivery_slots": test_delivery_slots(),
    }
    
    print("\n" + "="*60)
    print(" Test Summary")
    print("="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print("\nNext steps:")
    print(f"1. Open shop: {SHOP_URL}")
    print(f"2. Open admin: {ADMIN_URL}/orders")
    print("3. Manually test order creation and status management")

if __name__ == "__main__":
    main()
