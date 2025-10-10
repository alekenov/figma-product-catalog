#!/usr/bin/env python3
"""
Быстрый тест V2 AI Agent Service
Используйте для проверки работоспособности перед тестированием в Telegram
"""

import requests
import json
import time
from datetime import datetime

# Настройки
V2_URL = "http://localhost:8002"
TEST_USER_ID = "quick_test"

def print_separator():
    print("=" * 80)

def test_health():
    """Проверка health endpoint"""
    print_separator()
    print("🏥 Проверка здоровья сервиса...")

    try:
        response = requests.get(f"{V2_URL}/health", timeout=5)
        health = response.json()

        print(f"✅ Статус: {health['status']}")
        print(f"📊 Cache Hit Rate: {health['cache_hit_rate']}")
        print(f"📈 Total Requests: {health['total_requests']}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_chat(message: str):
    """Отправить сообщение в v2 и показать ответ"""
    print_separator()
    print(f"💬 Отправка: '{message}'")
    print(f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}")

    payload = {
        "message": message,
        "user_id": TEST_USER_ID,
        "channel": "telegram"
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{V2_URL}/chat",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            print(f"\n✅ Ответ получен за {elapsed:.2f}с")
            print(f"\n📝 Текст ответа:")
            print("-" * 80)
            # Убираем thinking и conversation_status из вывода
            text = data['text']
            if '<thinking>' in text:
                text = text.split('</thinking>')[-1].strip()
            if '<conversation_status>' in text:
                text = text.split('<conversation_status>')[0].strip()
            print(text)
            print("-" * 80)

            # Показываем usage
            usage = data.get('usage', {})
            print(f"\n💰 Стоимость: ${usage.get('total_cost_usd', 0):.6f}")
            print(f"🔄 Cache hit: {usage.get('cache_hit', False)}")
            print(f"📊 Токены: input={usage.get('input_tokens', 0)}, output={usage.get('output_tokens', 0)}")

            if usage.get('cache_creation_tokens', 0) > 0:
                print(f"🆕 Cache created: {usage.get('cache_creation_tokens', 0)} tokens")
            if usage.get('cache_read_tokens', 0) > 0:
                print(f"📖 Cache read: {usage.get('cache_read_tokens', 0)} tokens")

            return True
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Запуск тестов"""
    print("\n🧪 Быстрый тест V2 AI Agent Service")
    print(f"🎯 URL: {V2_URL}")
    print(f"👤 User ID: {TEST_USER_ID}\n")

    # 1. Проверка health
    if not test_health():
        print("\n❌ Сервис недоступен. Убедитесь что v2 запущен.")
        return

    # 2. Тест простого запроса
    test_chat("привет")

    # 3. Тест с кэшем (второй запрос должен использовать cache)
    input("\n⏸️  Нажмите Enter для следующего теста...")
    test_chat("покажи готовые букеты")

    # 4. Тест создания заказа
    input("\n⏸️  Нажмите Enter для теста создания заказа...")
    test_chat("Хочу заказать 15 роз на завтра утром. Иван 77011111111, адрес Абая 50")

    print_separator()
    print("\n✅ Все тесты завершены!")
    print("\n💡 Подсказка: Если v2 работает, можете тестировать в Telegram @cvetysdkbot")
    print(f"💡 Логи v2: tail -f /tmp/v2_restart.log")
    print(f"💡 Логи бота: tail -f /tmp/bot_restart.log\n")

if __name__ == "__main__":
    main()
