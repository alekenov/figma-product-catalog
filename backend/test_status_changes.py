#!/usr/bin/env python3
"""Test order status changes and refund"""
import requests
import json

BASE_URL = "http://localhost:8014/api/v1"
ORDER_ID = 74

def get_token():
    """Get admin token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": "+77015211545", "password": "testpass123"}
    )
    return response.json()["access_token"]

def change_status(token, status, notes=""):
    """Change order status"""
    print(f"\n📝 Меняю статус на: {status}")
    response = requests.patch(
        f"{BASE_URL}/orders/{ORDER_ID}/status",
        params={"status": status, "notes": notes},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Статус изменен: {data['status']}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")
        return False

def get_order_details(token):
    """Get order details"""
    response = requests.get(
        f"{BASE_URL}/orders/{ORDER_ID}",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 Заказ #{data['orderNumber']}")
        print(f"   Статус: {data['status']}")
        print(f"   Сумма: {data['total']/100} тенге")
        print(f"   Kaspi Payment ID: {data.get('kaspi_payment_id')}")
        return data
    return None

def test_refund(payment_id, amount):
    """Test Kaspi refund"""
    print(f"\n💰 Тестирую возврат: {amount} тенге")
    response = requests.post(
        f"{BASE_URL}/kaspi/refund",
        json={"external_id": payment_id, "amount": amount}
    )

    if response.status_code == 200:
        print(f"✅ Возврат успешно выполнен: {amount} тенге")
        return True
    else:
        data = response.json() if response.headers.get('content-type') == 'application/json' else {}
        error = data.get('detail', response.text)
        print(f"❌ Ошибка возврата: {error}")
        return False

def main():
    print("🚀 Тестирование изменения статусов заказа")

    # Get token
    print("\n🔑 Получаю токен...")
    token = get_token()
    print("✅ Токен получен")

    # Show current status
    order = get_order_details(token)
    if not order:
        print("❌ Не удалось получить заказ")
        return

    kaspi_payment_id = order.get('kaspi_payment_id')
    total_amount = order['total'] / 100  # Convert kopecks to tenge

    # Change statuses: PAID → ACCEPTED → ASSEMBLED → IN_DELIVERY → DELIVERED
    # Note: API accepts lowercase status values
    statuses = [
        ("accepted", "Заказ принят"),
        ("assembled", "Заказ собран"),
        ("in_delivery", "В пути"),
        ("delivered", "Доставлен")
    ]

    for status, notes in statuses:
        if not change_status(token, status, notes):
            print(f"❌ Не удалось изменить статус на {status}")
            return

    # Show final status
    print("\n" + "="*60)
    get_order_details(token)

    # Test refunds
    print("\n" + "="*60)
    print("💰 ТЕСТИРОВАНИЕ ВОЗВРАТОВ")
    print("="*60)

    if not kaspi_payment_id:
        print("❌ Нет Kaspi Payment ID для возврата")
        return

    # Refund 1: 50%
    refund1 = total_amount / 2
    test_refund(kaspi_payment_id, refund1)

    # Refund 2: Remaining 50%
    refund2 = total_amount / 2
    test_refund(kaspi_payment_id, refund2)

    # Refund 3: Excess (should fail)
    print("\n🔍 Пробую избыточный возврат (должен быть отклонен)...")
    test_refund(kaspi_payment_id, 1000)

    print("\n" + "="*60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("="*60)

if __name__ == "__main__":
    main()
