#!/usr/bin/env python3
"""
Тестирование MCP сервера через Claude API как реальный пользователь.
Имитирует поведение telegram бота - задает вопросы и смотрит как AI использует MCP tools.
"""

import anthropic
import os
import json
from datetime import datetime

# MCP сервер URL
MCP_BASE_URL = "http://localhost:8000"

# Определяем доступные MCP tools для Claude
MCP_TOOLS = [
    {
        "name": "list_products",
        "description": "Get list of products with filtering. Use shop_id=1 for testing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shop_id": {"type": "integer", "description": "Filter by shop ID (required, use 1)"},
                "search": {"type": "string", "description": "Search in product names"},
                "product_type": {
                    "type": "string",
                    "description": "Filter by type. Valid values: 'flowers', 'sweets', 'fruits', 'gifts'. Leave empty for all types."
                },
                "enabled_only": {"type": "boolean", "description": "Show only enabled products", "default": True},
                "min_price": {"type": "integer", "description": "Minimum price in tenge"},
                "max_price": {"type": "integer", "description": "Maximum price in tenge"},
                "skip": {"type": "integer", "description": "Number of products to skip", "default": 0},
                "limit": {"type": "integer", "description": "Number of products to return (max 100)", "default": 20}
            },
            "required": ["shop_id"]
        }
    },
    {
        "name": "get_shop_settings",
        "description": "Get shop settings and information. Use shop_id=1 for testing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shop_id": {"type": "integer", "description": "Shop ID (use 1 for testing)"}
            },
            "required": ["shop_id"]
        }
    },
    {
        "name": "get_telegram_client",
        "description": "Check if telegram user is registered. Returns client info or null.",
        "input_schema": {
            "type": "object",
            "properties": {
                "telegram_user_id": {"type": "string", "description": "Telegram user ID"},
                "shop_id": {"type": "integer", "description": "Shop ID"}
            },
            "required": ["telegram_user_id", "shop_id"]
        }
    }
]

def call_mcp_tool(tool_name: str, arguments: dict):
    """Вызов MCP tool через HTTP API"""
    import requests

    print(f"\n🔧 Вызываю MCP tool: {tool_name}")
    print(f"   Параметры: {json.dumps(arguments, ensure_ascii=False)}")

    response = requests.post(
        f"{MCP_BASE_URL}/call-tool",
        json={"name": tool_name, "arguments": arguments},
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Успешно: получено {len(str(result))} символов")
        return result.get("result")
    else:
        error = response.json()
        print(f"   ❌ Ошибка {response.status_code}: {error.get('detail', 'Unknown error')}")
        raise Exception(f"MCP tool failed: {error.get('detail')}")

def test_conversation(user_message: str):
    """Тестовая беседа с Claude с доступом к MCP tools"""

    print("\n" + "="*80)
    print(f"👤 Пользователь: {user_message}")
    print("="*80)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    messages = [{"role": "user", "content": user_message}]

    # Системный промпт как в телеграм боте
    system_prompt = """Ты AI-ассистент цветочного магазина.
Помогаешь клиентам подобрать букеты и подарки.
Отвечай кратко и дружелюбно на русском языке.
Цены в базе указаны в тиынах (1 тенге = 100 тиын), конвертируй в тенге при ответе."""

    iteration = 0
    max_iterations = 5

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Итерация {iteration}")

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            system=system_prompt,
            tools=MCP_TOOLS,
            messages=messages
        )

        print(f"🤖 Claude ответил: stop_reason={response.stop_reason}")

        # Обрабатываем ответ
        if response.stop_reason == "end_turn":
            # Финальный ответ
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\n💬 Ответ AI:\n{block.text}")
            break

        elif response.stop_reason == "tool_use":
            # Claude хочет использовать tool
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n🛠️  Claude использует tool: {block.name}")

                    try:
                        result = call_mcp_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "is_error": True,
                            "content": str(e)
                        })

            messages.append({"role": "user", "content": tool_results})
        else:
            print(f"⚠️  Неожиданный stop_reason: {response.stop_reason}")
            break

    print("\n" + "="*80)

if __name__ == "__main__":
    print("🧪 ТЕСТИРОВАНИЕ MCP СЕРВЕРА КАК РЕАЛЬНЫЙ ПОЛЬЗОВАТЕЛЬ")
    print(f"⏰ Начало тестов: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Проверяем API ключ
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n❌ Ошибка: установите ANTHROPIC_API_KEY")
        exit(1)

    # Проверяем что MCP сервер работает
    import requests
    try:
        health = requests.get(f"{MCP_BASE_URL}/health").json()
        print(f"✅ MCP сервер работает: {health}")
    except Exception as e:
        print(f"❌ MCP сервер недоступен: {e}")
        exit(1)

    # Тестовые вопросы как от реального пользователя
    test_questions = [
        "Покажи мне все букеты из цветов",
        "Найди букет за 1800 тенге",
        "Какие есть букеты на заказ?",  # Проверка что AI не использует type="custom"
    ]

    for question in test_questions:
        try:
            test_conversation(question)
        except Exception as e:
            print(f"\n❌ Ошибка при обработке вопроса: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n⏰ Конец тестов: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
