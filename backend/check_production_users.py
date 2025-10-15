#!/usr/bin/env python3
"""
Check production users via API endpoint.
"""
import requests
import json

PRODUCTION_URL = "https://figma-product-catalog-production.up.railway.app"

def check_production():
    """Get all users from production database"""

    print("🔍 Checking production database...")
    print(f"URL: {PRODUCTION_URL}\n")

    # First check health
    try:
        health = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
        if health.status_code == 200:
            print("✅ Production is UP\n")
        else:
            print(f"⚠️  Production health check returned {health.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot reach production: {e}\n")
        return

    # Get shops list (public endpoint)
    try:
        print("📊 Fetching shops from production...\n")
        response = requests.get(f"{PRODUCTION_URL}/api/v1/shops/", timeout=10)

        if response.status_code == 200:
            shops = response.json()  # API returns list directly

            print(f"=== PRODUCTION SHOPS: {len(shops)} ===\n")

            for shop in shops:
                print(f"🏪 {shop.get('name')} (ID: {shop.get('id')})")
                print(f"   📍 {shop.get('city', 'Город не указан')}")
                print(f"   📞 {shop.get('phone', 'Не указан')}")
                print(f"   {'🟢' if shop.get('is_active') else '🔴'} {'Открыт' if shop.get('is_active') else 'Закрыт'}")
                print()

            return shops
        else:
            print(f"❌ Failed to fetch shops: {response.status_code}")
            print(response.text[:200])

    except Exception as e:
        print(f"❌ Error fetching production data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_production()
