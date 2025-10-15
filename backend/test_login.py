#!/usr/bin/env python3
"""Test login with different phone formats"""
import requests
import json

API_URL = "http://localhost:8014/api/v1/auth/login"

# Test cases
test_cases = [
    {"phone": "77088888888", "password": "test1234", "name": "Without +7"},
    {"phone": "+77088888888", "password": "test1234", "name": "With +7"},
]

print("Testing login API...\n")

for test in test_cases:
    print(f"Test: {test['name']}")
    print(f"  Phone: {test['phone']}")

    try:
        response = requests.post(
            API_URL,
            json={"phone": test['phone'], "password": test['password']},
            headers={"Content-Type": "application/json"}
        )

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success! User: {data.get('user', {}).get('name')}")
            print(f"  Shop ID: {data.get('user', {}).get('shop_id')}")
        else:
            print(f"  ❌ Failed: {response.text}")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()
