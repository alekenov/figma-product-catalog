#!/usr/bin/env python3
"""Check order via tracking API"""
import requests
import json

TRACKING_ID = "099128807"
API_URL = f"http://localhost:8014/api/v1/orders/by-tracking/{TRACKING_ID}/status"

print(f"Проверка заказа tracking_id: {TRACKING_ID}\n")

# Public API (no auth required)
response = requests.get(API_URL)

if response.status_code == 200:
    data = response.json()
    print("✅ Заказ найден через публичный API")
    print(f"\nOrder Number: {data.get('orderNumber')}")
    print(f"Status: {data.get('status')}")
    print(f"Customer: {data.get('customerName')}")
    print(f"Phone: {data.get('phone')}")
    print(f"Address: {data.get('delivery_address')}")
    print(f"Total: {data.get('total') / 100:.2f} ₸")
    print(f"Items: {len(data.get('items', []))}")
    for item in data.get('items', []):
        print(f"  - {item['product_name']} x{item['quantity']} @ {item['product_price']/100:.0f}₸")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
