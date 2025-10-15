#!/usr/bin/env python3
"""Get auth token for shop_id=8 user"""
import requests
import json

API_URL = "http://localhost:8014/api/v1/auth/login"

response = requests.post(
    API_URL,
    json={"phone": "77088888888", "password": "test1234"},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    token = data.get('access_token')
    user = data.get('user', {})

    print("✅ Login successful!")
    print(f"\nUser: {user.get('name')}")
    print(f"Phone: {user.get('phone')}")
    print(f"Role: {user.get('role')}")
    print(f"Shop ID: {user.get('shop_id')}")
    print(f"\nToken: {token}")
    print("\nTo set in browser console:")
    print(f'localStorage.setItem("token", "{token}");')
    print(f'localStorage.setItem("user", \'{json.dumps(user)}\');')
    print('window.location.reload();')
else:
    print(f"❌ Login failed: {response.text}")
