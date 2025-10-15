#!/usr/bin/env python3
"""Test Kaspi refunds on production"""
import requests

BASE_URL = "https://figma-product-catalog-production.up.railway.app/api/v1"
PAYMENT_ID = "12707474637"
TOTAL = 12000  # tenge

def test_refund(amount, description):
    """Test refund"""
    print(f"\n{description}")
    print(f"💸 Возврат: {amount} тенге...")

    response = requests.post(
        f"{BASE_URL}/kaspi/refund",
        json={"external_id": PAYMENT_ID, "amount": amount}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Успешно!")
        print(f"   Ответ: {data}")
        return True
    else:
        try:
            error = response.json().get('detail', response.text)
        except:
            error = response.text
        print(f"❌ Ошибка: {error}")
        return False

def main():
    print("="*60)
    print("ТЕСТИРОВАНИЕ ВОЗВРАТОВ KASPI PAY НА ПРОДАКШЕНЕ")
    print("="*60)
    print(f"Payment ID: {PAYMENT_ID}")
    print(f"Общая сумма: {TOTAL} тенге")

    # Refund 1: 50%
    test_refund(TOTAL / 2, "1️⃣ Первый возврат (50%)")

    # Refund 2: Remaining 50%
    test_refund(TOTAL / 2, "2️⃣ Второй возврат (остальные 50%)")

    # Refund 3: Excess (should fail)
    test_refund(1000, "3️⃣ Избыточный возврат (должен быть отклонен)")

    print("\n" + "="*60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("="*60)

if __name__ == "__main__":
    main()
