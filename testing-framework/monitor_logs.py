#!/usr/bin/env python3
"""
Мониторинг логов AI Agent в реальном времени с фильтрацией и подсветкой.
"""
import subprocess
import threading
import time
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import re

console = Console()

class LogMonitor:
    def __init__(self):
        self.logs = {
            "ai_agent": [],
            "mcp_server": [],
            "telegram": [],
            "backend": []
        }
        self.stats = {
            "requests": 0,
            "errors": 0,
            "timeouts": 0,
            "avg_time": 0
        }
        self.running = True

    def tail_log(self, log_file, log_key):
        """Следит за логом в отдельном потоке."""
        try:
            process = subprocess.Popen(
                ['tail', '-f', log_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in process.stdout:
                if not self.running:
                    break

                # Добавляем строку в буфер (максимум 50 строк)
                self.logs[log_key].append(line.strip())
                if len(self.logs[log_key]) > 50:
                    self.logs[log_key].pop(0)

                # Анализируем строку
                self.analyze_line(line, log_key)

        except Exception as e:
            self.logs[log_key].append(f"[red]Ошибка чтения лога: {e}[/red]")

    def analyze_line(self, line, source):
        """Анализирует строку лога для статистики."""
        # Подсчет запросов
        if "POST /chat" in line or "Incoming chat request" in line:
            self.stats["requests"] += 1

        # Подсчет ошибок
        if "ERROR" in line or "error" in line.lower():
            self.stats["errors"] += 1

        # Поиск времени ответа
        time_match = re.search(r'(\d+\.\d+)s', line)
        if time_match:
            response_time = float(time_match.group(1))
            if self.stats["avg_time"] == 0:
                self.stats["avg_time"] = response_time
            else:
                self.stats["avg_time"] = (self.stats["avg_time"] + response_time) / 2

    def format_log_lines(self, lines, title):
        """Форматирует строки лога для отображения."""
        formatted = []
        for line in lines[-20:]:  # Последние 20 строк
            # Подсветка важных элементов
            if "ERROR" in line:
                formatted.append(f"[red]{line}[/red]")
            elif "WARNING" in line:
                formatted.append(f"[yellow]{line}[/yellow]")
            elif "SUCCESS" in line or "200 OK" in line:
                formatted.append(f"[green]{line}[/green]")
            elif "INTENT" in line or "Tool" in line:
                formatted.append(f"[cyan]{line}[/cyan]")
            else:
                formatted.append(line)

        return Panel(
            "\n".join(formatted) if formatted else "Ожидание логов...",
            title=title,
            border_style="cyan"
        )

    def create_stats_table(self):
        """Создает таблицу со статистикой."""
        table = Table(title="📊 Статистика", show_header=True)
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", justify="right")

        table.add_row("Запросов", str(self.stats["requests"]))
        table.add_row("Ошибок", f"[red]{self.stats['errors']}[/red]" if self.stats["errors"] > 0 else "0")
        table.add_row("Среднее время", f"{self.stats['avg_time']:.2f}с")

        # Индикаторы проблем
        if self.stats["avg_time"] > 5:
            table.add_row("⚠️  Статус", "[red]Медленно[/red]")
        elif self.stats["errors"] > 0:
            table.add_row("⚠️  Статус", "[yellow]Есть ошибки[/yellow]")
        else:
            table.add_row("✅ Статус", "[green]Работает[/green]")

        return table

    def create_layout(self):
        """Создает layout для отображения."""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=8)
        )

        layout["header"].update(
            Panel(
                f"🔍 [bold cyan]Мониторинг логов AI Agent[/bold cyan] | {datetime.now().strftime('%H:%M:%S')}",
                border_style="cyan"
            )
        )

        # Главная область с логами
        main = Layout()
        main.split_row(
            Layout(self.format_log_lines(self.logs["ai_agent"], "AI Agent"), name="ai_agent"),
            Layout(self.format_log_lines(self.logs["mcp_server"], "MCP Server"), name="mcp")
        )
        layout["main"].update(main)

        # Нижняя панель со статистикой
        layout["footer"].update(self.create_stats_table())

        return layout

def main():
    monitor = LogMonitor()

    # Запускаем мониторинг логов в отдельных потоках
    threads = [
        threading.Thread(target=monitor.tail_log, args=("/tmp/ai-agent-new.log", "ai_agent")),
        threading.Thread(target=monitor.tail_log, args=("/tmp/mcp-server-final.log", "mcp_server")),
        threading.Thread(target=monitor.tail_log, args=("telegram-bot/logs/bot_8.log", "telegram"))
    ]

    for t in threads:
        t.daemon = True
        t.start()

    # Отображаем в реальном времени
    try:
        with Live(monitor.create_layout(), refresh_per_second=1, screen=True) as live:
            while True:
                time.sleep(0.5)
                live.update(monitor.create_layout())
    except KeyboardInterrupt:
        monitor.running = False
        console.print("\n[yellow]Мониторинг остановлен[/yellow]")

if __name__ == "__main__":
    console.print("[cyan]Запускаю мониторинг логов...[/cyan]")
    console.print("Нажмите Ctrl+C для остановки\n")
    main()