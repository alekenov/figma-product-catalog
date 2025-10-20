#!/usr/bin/env python3
"""Delete product via production API"""

import os
import sys
import requests

# Production API base URL
API_BASE = "https://figma-product-catalog-production.up.railway.app/api/v1"

# Admin credentials (from Railway environment)
ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "77015211545")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

def login():
    """Login and get JWT token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"phone": ADMIN_PHONE, "password": ADMIN_PASSWORD}
    )

    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)

    data = response.json()
    return data.get("access_token")

def delete_product(product_id: int, token: str):
    """Delete product by ID"""
    headers = {"Authorization": f"Bearer {token}"}

    # First check if DELETE endpoint exists, if not we need to use database
    response = requests.delete(
        f"{API_BASE}/products/{product_id}",
        headers=headers
    )

    return response

if __name__ == "__main__":
    product_id = 11
    product_name = "Букет 'Белые розы премиум'"

    print(f"Logging in...")
    token = login()
    print(f"✓ Logged in successfully")

    print(f"\nDeleting product ID {product_id}: {product_name}")
    response = delete_product(product_id, token)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code in [200, 204]:
        print(f"✓ Product deleted successfully")
    elif response.status_code == 404:
        print(f"⚠ DELETE endpoint not found - need to use database directly")
    else:
        print(f"✗ Failed to delete product")
        sys.exit(1)
