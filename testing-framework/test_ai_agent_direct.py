#!/usr/bin/env python3
"""
Прямое тестирование AI Agent Service с логированием и таймингом.
Позволяет быстро тестировать запросы без Telegram.
"""
import asyncio
import httpx
import time
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()

# Конфигурация
AI_AGENT_URL = "http://localhost:8000"
MCP_SERVER_URL = "http://localhost:8001"
USER_ID = "test_user_123"

# Тестовые запросы
TEST_MESSAGES = [
    {"message": "привет", "expected": "приветствие"},
    {"message": "покажи букеты", "expected": "список товаров"},
    {"message": "букет роз до 10000", "expected": "фильтр по цене"},
    {"message": "хочу заказать", "expected": "процесс заказа"},
    {"message": "статус заказа", "expected": "отслеживание"},
]

async def test_single_message(message: str, session: httpx.AsyncClient) -> dict:
    """Тестирует одно сообщение и измеряет время ответа."""

    console.print(f"\n[blue]➤ Отправляю:[/blue] {message}")

    start_time = time.time()

    try:
        response = await session.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": message,
                "user_id": USER_ID,
                "channel": "telegram"
            },
            timeout=60.0
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            # Показываем результат
            console.print(f"[green]✓ Ответ за {elapsed:.2f}с:[/green]")

            # Выводим первые 200 символов ответа
            text = result.get("text", "")[:200]
            if len(result.get("text", "")) > 200:
                text += "..."

            console.print(Panel(text, title="Ответ AI", border_style="green"))

            return {
                "status": "success",
                "time": elapsed,
                "response": result
            }
        else:
            console.print(f"[red]✗ Ошибка {response.status_code}:[/red] {response.text}")
            return {
                "status": "error",
                "time": elapsed,
                "error": f"HTTP {response.status_code}"
            }

    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        console.print(f"[red]✗ Таймаут после {elapsed:.2f}с[/red]")
        return {
            "status": "timeout",
            "time": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        console.print(f"[red]✗ Ошибка: {e}[/red]")
        return {
            "status": "error",
            "time": elapsed,
            "error": str(e)
        }

async def check_services():
    """Проверяет доступность сервисов."""

    console.print("\n[cyan]🔍 Проверяю сервисы...[/cyan]\n")

    services = [
        ("AI Agent", AI_AGENT_URL, "/health"),
        ("MCP Server", MCP_SERVER_URL, "/health"),
        ("Backend", "http://localhost:8014", "/health"),
    ]

    table = Table(title="Статус сервисов", show_header=True, header_style="bold magenta")
    table.add_column("Сервис", style="cyan", width=15)
    table.add_column("URL", style="blue")
    table.add_column("Статус", justify="center")
    table.add_column("Время ответа", justify="right")

    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url, endpoint in services:
            try:
                start = time.time()
                response = await client.get(f"{url}{endpoint}")
                elapsed = time.time() - start

                if response.status_code == 200:
                    table.add_row(
                        name,
                        f"{url}",
                        "[green]✓ Работает[/green]",
                        f"{elapsed:.3f}с"
                    )
                else:
                    table.add_row(
                        name,
                        f"{url}",
                        f"[yellow]⚠ HTTP {response.status_code}[/yellow]",
                        f"{elapsed:.3f}с"
                    )
            except Exception as e:
                table.add_row(
                    name,
                    f"{url}",
                    "[red]✗ Недоступен[/red]",
                    "-"
                )

    console.print(table)

async def run_tests():
    """Запускает серию тестов."""

    # Проверяем сервисы
    await check_services()

    console.print("\n[cyan]🚀 Начинаю тестирование AI Agent...[/cyan]\n")

    results = []

    async with httpx.AsyncClient() as session:
        for test in TEST_MESSAGES:
            result = await test_single_message(test["message"], session)
            result["message"] = test["message"]
            result["expected"] = test["expected"]
            results.append(result)

            # Небольшая пауза между запросами
            await asyncio.sleep(1)

    # Показываем сводку
    console.print("\n[cyan]📊 Результаты тестирования:[/cyan]\n")

    table = Table(title="Сводка тестов", show_header=True, header_style="bold magenta")
    table.add_column("Сообщение", style="cyan", width=25)
    table.add_column("Ожидалось", style="blue", width=20)
    table.add_column("Статус", justify="center", width=15)
    table.add_column("Время", justify="right", width=10)

    total_time = 0
    success_count = 0

    for r in results:
        status_style = {
            "success": "[green]✓ Успех[/green]",
            "error": "[red]✗ Ошибка[/red]",
            "timeout": "[red]⏱ Таймаут[/red]"
        }

        table.add_row(
            r["message"][:25],
            r["expected"],
            status_style.get(r["status"], r["status"]),
            f"{r['time']:.2f}с"
        )

        total_time += r["time"]
        if r["status"] == "success":
            success_count += 1

    console.print(table)

    # Статистика
    console.print(f"\n[bold]Статистика:[/bold]")
    console.print(f"• Успешных: {success_count}/{len(results)}")
    console.print(f"• Среднее время: {total_time/len(results):.2f}с")
    console.print(f"• Общее время: {total_time:.2f}с")

    # Предупреждения
    if total_time/len(results) > 5:
        console.print("\n[red]⚠️  ПРОБЛЕМА: Среднее время ответа > 5 секунд![/red]")
        console.print("[yellow]Возможные причины:[/yellow]")
        console.print("• Неправильная модель OpenAI (gpt-5-mini не существует)")
        console.print("• Избыточная 3-шаговая архитектура")
        console.print("• Проблемы с MCP Server")

async def interactive_test():
    """Интерактивный режим тестирования."""

    console.print("[cyan]💬 Интерактивный режим[/cyan]")
    console.print("Введите сообщения для тестирования (или 'exit' для выхода)\n")

    async with httpx.AsyncClient() as session:
        while True:
            message = console.input("[blue]Вы: [/blue]")

            if message.lower() in ['exit', 'quit', 'выход']:
                break

            await test_single_message(message, session)

def main():
    """Главная функция."""

    console.print(Panel.fit(
        "🧪 [bold cyan]Тестирование AI Agent Service[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\nВыберите режим:")
    console.print("1. Автоматические тесты")
    console.print("2. Интерактивный режим")
    console.print("3. Только проверка сервисов")

    choice = console.input("\n[cyan]Выбор (1/2/3): [/cyan]")

    if choice == "1":
        asyncio.run(run_tests())
    elif choice == "2":
        asyncio.run(interactive_test())
    elif choice == "3":
        asyncio.run(check_services())
    else:
        console.print("[red]Неверный выбор[/red]")

if __name__ == "__main__":
    main()