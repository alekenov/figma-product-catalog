#!/usr/bin/env python3
"""Test complete Kaspi Pay flow on production"""
import requests
import json
import time

BASE_URL = "https://figma-product-catalog-production.up.railway.app/api/v1"
TRACKING_ID = "788007734"
KASPI_PAYMENT_ID = "12707474637"

def get_token():
    """Get admin token"""
    print("🔑 Получаю токен администратора...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": "+77015211545", "password": "testpass123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Токен получен")
        return token
    else:
        print(f"❌ Ошибка получения токена: {response.status_code}")
        print(response.text)
        return None

def check_payment_status():
    """Check Kaspi payment status"""
    print(f"\n💰 Проверяю статус платежа Kaspi ID: {KASPI_PAYMENT_ID}...")
    response = requests.get(f"{BASE_URL}/kaspi/status/{KASPI_PAYMENT_ID}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Статус платежа: {data.get('status')}")
        print(f"   Сумма: {data.get('amount')} тенге")
        return data
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)
        return None

def get_order_details(token, order_id):
    """Get order details"""
    print(f"\n📋 Получаю детали заказа...")
    response = requests.get(
        f"{BASE_URL}/orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Заказ #{data.get('orderNumber')}")
        print(f"   Статус: {data.get('status')}")
        print(f"   Kaspi Payment Status: {data.get('kaspi_payment_status')}")
        print(f"   Сумма: {data.get('total', 0)/100} тенге")
        return data
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)
        return None

def find_order_by_tracking(token):
    """Find order by tracking ID"""
    print(f"\n🔍 Ищу заказ по tracking ID: {TRACKING_ID}...")
    response = requests.get(
        f"{BASE_URL}/orders/",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 100}
    )

    if response.status_code == 200:
        orders = response.json()
        for order in orders:
            if order.get('tracking_id') == TRACKING_ID:
                print(f"✅ Заказ найден: ID {order['id']}, #{order.get('orderNumber')}")
                return order['id']
        print(f"❌ Заказ с tracking_id {TRACKING_ID} не найден")
        return None
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return None

def change_status(token, order_id, status, notes=""):
    """Change order status"""
    print(f"\n📝 Меняю статус на: {status}...")
    response = requests.patch(
        f"{BASE_URL}/orders/{order_id}/status",
        params={"status": status, "notes": notes},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Статус изменен: {data.get('status')}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)
        return False

def test_refund(amount):
    """Test Kaspi refund"""
    print(f"\n💸 Делаю возврат: {amount} тенге...")
    response = requests.post(
        f"{BASE_URL}/kaspi/refund",
        json={"external_id": KASPI_PAYMENT_ID, "amount": amount}
    )

    if response.status_code == 200:
        print(f"✅ Возврат выполнен: {amount} тенге")
        return True
    else:
        data = response.json() if response.headers.get('content-type') == 'application/json' else {}
        error = data.get('detail', response.text)
        print(f"❌ Ошибка возврата: {error}")
        return False

def main():
    print("="*60)
    print("ТЕСТИРОВАНИЕ ПОЛНОГО ЦИКЛА KASPI PAY НА ПРОДАКШЕНЕ")
    print("="*60)

    # 1. Get admin token
    token = get_token()
    if not token:
        return

    # 2. Check Kaspi payment status
    payment_status = check_payment_status()

    # 3. Find order by tracking ID
    order_id = find_order_by_tracking(token)
    if not order_id:
        print("\n⚠️  Заказ не найден, завершаю тест")
        return

    # 4. Get order details
    order = get_order_details(token, order_id)
    if not order:
        return

    total_amount = order.get('total', 0) / 100
    current_status = order.get('status')

    print(f"\n📊 Текущее состояние:")
    print(f"   Заказ ID: {order_id}")
    print(f"   Статус заказа: {current_status}")
    print(f"   Kaspi Payment: {order.get('kaspi_payment_status')}")
    print(f"   Сумма: {total_amount} тенге")

    # 5. Change order statuses
    if current_status == "NEW":
        print("\n🔄 Заказ в статусе NEW, меняю статусы...")

        statuses = [
            ("paid", "Оплачен через Kaspi"),
            ("accepted", "Заказ принят"),
            ("assembled", "Заказ собран"),
            ("in_delivery", "В пути к клиенту"),
            ("delivered", "Доставлен")
        ]

        for status, notes in statuses:
            if not change_status(token, order_id, status, notes):
                print(f"❌ Не удалось изменить статус на {status}")
                return
            time.sleep(1)
    else:
        print(f"\n⚠️  Заказ уже в статусе {current_status}, пропускаю изменение статусов")

    # 6. Show final order state
    print("\n" + "="*60)
    print("ФИНАЛЬНОЕ СОСТОЯНИЕ ЗАКАЗА")
    print("="*60)
    get_order_details(token, order_id)

    # 7. Test refunds
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ВОЗВРАТОВ")
    print("="*60)

    # Refund 1: 50%
    refund1 = total_amount / 2
    test_refund(refund1)
    time.sleep(1)

    # Refund 2: Remaining 50%
    refund2 = total_amount / 2
    test_refund(refund2)
    time.sleep(1)

    # Refund 3: Excess (should fail)
    print("\n🔍 Пробую избыточный возврат (должен быть отклонен)...")
    test_refund(1000)

    print("\n" + "="*60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("="*60)

if __name__ == "__main__":
    main()
