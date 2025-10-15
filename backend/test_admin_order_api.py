#!/usr/bin/env python3
"""Test admin order management API"""
import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicGhvbmUiOiI3NzA4ODg4ODg4OCIsInJvbGUiOiJESVJFQ1RPUiIsInNob3BfaWQiOjgsImV4cCI6MTc2MTA0NTY2OX0.TvtD0KX4sD8_4TdsGu8gUP68gbWbjITwskWURaSGVPM"
API_BASE = "http://localhost:8014/api/v1"
TRACKING_ID = "099128807"

headers = {"Authorization": f"Bearer {TOKEN}"}

print("=" * 60)
print("ТЕСТ АДМИНСКОГО API ДЛЯ CRM")
print("=" * 60)

# 1. Get list of orders
print("\n1️⃣  Получение списка заказов для shop_id=8...")
response = requests.get(f"{API_BASE}/orders/", headers=headers)
if response.status_code == 200:
    orders = response.json()
    print(f"✅ Найдено заказов: {len(orders)}")
    target_order = next((o for o in orders if o.get('tracking_id') == TRACKING_ID), None)
    if target_order:
        print(f"✅ Найден наш заказ: {target_order.get('orderNumber')} (ID: {target_order.get('id')})")
        order_id = target_order.get('id')
    else:
        print(f"❌ Заказ {TRACKING_ID} не найден в списке")
        order_id = None
else:
    print(f"❌ Ошибка: {response.status_code} - {response.text}")
    order_id = None

if not order_id:
    # Try to get order_id from database
    import sqlite3
    conn = sqlite3.connect('figma_catalog.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM "order" WHERE tracking_id = ?', (TRACKING_ID,))
    result = cursor.fetchone()
    if result:
        order_id = result[0]
        print(f"ℹ️  Order ID получен из базы: {order_id}")
    conn.close()

if order_id:
    # 2. Get order details
    print(f"\n2️⃣  Получение деталей заказа ID={order_id}...")
    response = requests.get(f"{API_BASE}/orders/{order_id}", headers=headers)
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Заказ получен:")
        print(f"   Order Number: {order.get('orderNumber')}")
        print(f"   Status: {order.get('status')}")
        print(f"   Customer: {order.get('customerName')}")
        print(f"   Total: {order.get('total', 0) / 100:.2f} ₸")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")

    # 3. Change order status
    print(f"\n3️⃣  Изменение статуса заказа на 'paid'...")
    response = requests.patch(
        f"{API_BASE}/orders/{order_id}/status?status=paid&notes=Оплачено через тест",
        headers=headers
    )
    if response.status_code == 200:
        print("✅ Статус изменен на PAID")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")

    # 4. Verify status change
    print(f"\n4️⃣  Проверка изменения статуса...")
    response = requests.get(f"{API_BASE}/orders/{order_id}", headers=headers)
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Текущий статус: {order.get('status')}")
    else:
        print(f"❌ Ошибка: {response.status_code}")

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 60)
