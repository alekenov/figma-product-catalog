# AI Testing Framework для Цветочного Магазина

Система автоматического тестирования с использованием Claude 4.5, где два AI (менеджер и клиент) ведут реалистичный диалог, а третий компонент логирует все взаимодействия и создает детальные отчеты.

## 🎯 Возможности

- **AI Менеджер**: Claude 4.5 имитирует менеджера магазина с доступом к MCP tools (backend API)
- **AI Клиент**: Claude 4.5 играет роль клиента с различными персонами
- **Детальное логирование**: Записывает ВСЁ - сообщения, thinking blocks, tool calls, API requests, SQL queries
- **Автоматическая генерация отчетов**: Markdown + JSON с полным анализом
- **Memory Tool**: AI помнит контекст между сценариями
- **Interleaved Thinking**: Видимые рассуждения AI для отладки

## 📁 Структура

```
testing-framework/
├── ai_manager_service.py      # AI менеджер с MCP интеграцией
├── ai_client_service.py       # AI клиент с персонами
├── logger_analyzer.py         # Логирование и отчеты
├── test_orchestrator.py       # Оркестрация тестов
├── config.py                  # Конфигурация
├── requirements.txt           # Зависимости
├── scenarios/                 # Сценарии тестирования (YAML)
│   ├── 01_budget_customer.yaml
│   ├── 02_regular_customer.yaml
│   ├── 03_new_customer_questions.yaml
│   ├── 04_vip_demanding_customer.yaml
│   └── 05_order_tracking.yaml
├── personas/                  # Персоны клиентов (JSON)
│   ├── new_customer.json
│   ├── regular_customer.json
│   ├── budget_customer.json
│   └── demanding_customer.json
├── memories/                  # Memory Tool хранилище
│   ├── manager/
│   └── clients/
└── reports/                   # Сгенерированные отчеты
    └── latest/                # Симлинк на последний отчет
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd testing-framework
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Создайте .env файл или экспортируйте переменные
export CLAUDE_API_KEY="your-api-key"
export MCP_SERVER_URL="http://localhost:8000"
export BACKEND_API_URL="http://localhost:8014/api/v1"
export SHOP_ID="8"
```

### 3. Запуск MCP сервера и backend

```bash
# Terminal 1: Backend
cd ../backend
python main.py

# Terminal 2: MCP Server
cd ../mcp-server
./start.sh
```

### 4. Запуск теста

```bash
# Запустить один сценарий
python test_orchestrator.py 01_budget_customer.yaml

# Или использовать как модуль
python -c "import asyncio; from test_orchestrator import run_test; asyncio.run(run_test('01_budget_customer.yaml'))"
```

## 📝 Создание сценария

Создайте YAML файл в `scenarios/`:

```yaml
name: "Название теста"
description: "Описание что проверяется"

persona: "имя_персоны"  # Имя JSON файла из personas/

initial_message: "Первое сообщение клиента"

# Ожидаемый flow (для документации)
expected_flow:
  - manager_should_do_something: true

# Критерии успеха
success_criteria:
  products_shown: true         # Менеджер показал продукты
  price_filter_used: true      # Менеджер фильтровал по цене
  order_created: true          # Заказ был создан
  goal_achieved: true          # Клиент достиг цели

max_turns: 15                  # Макс кол-во сообщений
timeout_seconds: 120           # Таймаут в секундах
```

## 🎭 Создание персоны

Создайте JSON файл в `personas/`:

```json
{
  "name": "Имя клиента",
  "type": "тип_клиента",
  "characteristics": {
    "politeness": "high|medium|low",
    "decisiveness": "high|medium|low",
    "budget_sensitivity": "very_high|high|medium|low",
    "question_frequency": "high|medium|low"
  },
  "preferences": {
    "colors": ["red", "pink"],
    "price_range": [10000, 20000],
    "delivery_time": "morning|afternoon|evening|flexible"
  },
  "order_history": [
    {
      "date": "2025-09-15",
      "product": "Букет 'Нежность'",
      "price": 18000,
      "rating": 5
    }
  ],
  "communication_style": {
    "greeting": "formal|friendly|casual|business_like",
    "requests": "polite|direct|demanding",
    "complaints": "none|rare|occasional|frequent"
  }
}
```

## 📊 Отчеты

После каждого теста генерируются отчеты в `reports/YYYY_MM_DD_HH_MM_SS/`:

### full_report.md
Полный markdown отчет с:
- Метриками (длительность, кол-во сообщений, tool calls)
- Полным диалогом с thinking blocks
- Таблицей использования MCP tools
- Анализом успеха/провала
- Рекомендациями

### dialog.txt
Чистый текстовый диалог для легкого чтения

### api_calls.json
Структурированные данные всех MCP tool calls и API requests

### analysis.json
Метрики и анализ теста в JSON формате

## 🔧 Архитектура

### Компоненты

1. **AI Manager** (`ai_manager_service.py`)
   - Claude 4.5 Sonnet с MCP integration
   - Вызывает backend через MCP tools
   - Логирует все thinking blocks и tool calls

2. **AI Client** (`ai_client_service.py`)
   - Claude 4.5 Sonnet с persona system
   - Генерирует реалистичные сообщения
   - Использует Memory Tool для запоминания

3. **Test Logger** (`logger_analyzer.py`)
   - Записывает все взаимодействия
   - Генерирует отчеты в Markdown и JSON
   - Вычисляет метрики (latency, success rate)

4. **Test Orchestrator** (`test_orchestrator.py`)
   - Управляет flow теста
   - Координирует Manager и Client
   - Анализирует результаты

### Workflow

```
Orchestrator загружает сценарий
    ↓
Создает AI Manager + AI Client
    ↓
Client отправляет initial_message
    ↓
Logger записывает → Manager обрабатывает (может вызвать MCP tools)
    ↓
Logger записывает tool calls → Manager отвечает
    ↓
Client анализирует ответ (thinking) → генерирует следующее сообщение
    ↓
Повторяется до max_turns или goal_achieved
    ↓
Logger генерирует отчет
```

## 🎓 Использование Claude 4.5 возможностей

### Memory Tool
```python
# Автоматически активируется через beta headers
# Claude сохраняет контекст в memories/manager/ и memories/clients/
```

### Context Editing
```python
# Автоматически очищает старые tool calls
# Позволяет вести длинные диалоги без переполнения контекста
```

### Interleaved Thinking
```python
# Видимые thinking blocks между tool calls
# Показывают рассуждения AI для отладки
```

## 🐛 Troubleshooting

### MCP Server не отвечает
```bash
# Проверьте что MCP сервер запущен
curl http://localhost:8000/health

# Перезапустите MCP сервер
cd ../mcp-server
./start.sh
```

### Backend не доступен
```bash
# Проверьте backend
curl http://localhost:8014/health

# Запустите backend
cd ../backend
python main.py
```

### Ошибка "CLAUDE_API_KEY not found"
```bash
export CLAUDE_API_KEY="your-anthropic-api-key"
```

### Тест зависает
- Проверьте timeout в сценарии (возможно слишком маленький)
- Проверьте логи MCP сервера на ошибки
- Увеличьте max_turns если диалог сложный

## 📈 Метрики и анализ

Система автоматически вычисляет:

- **Длительность теста** (секунды)
- **Кол-во сообщений** (client + manager)
- **Кол-во MCP tool calls**
- **Средний latency** tool calls и API requests
- **Success rate** критериев успеха
- **Достижение цели** клиента

## 🔮 Примеры использования

### Запуск одного теста
```bash
python test_orchestrator.py 01_budget_customer.yaml
```

### Запуск всех тестов
```bash
for scenario in scenarios/*.yaml; do
    python test_orchestrator.py $(basename $scenario)
done
```

### Программный запуск
```python
import asyncio
from test_orchestrator import run_test, run_multiple_tests

# Один тест
result = asyncio.run(run_test('01_budget_customer.yaml'))
print(f"Result: {result['result']}")
print(f"Report: {result['report_dir']}")

# Множественные тесты
results = asyncio.run(run_multiple_tests([
    '01_budget_customer.yaml',
    '02_regular_customer.yaml',
    '03_new_customer_questions.yaml'
]))
```

## 🎯 Best Practices

1. **Создавайте реалистичные персоны** - чем детальнее, тем лучше
2. **Задавайте четкие success_criteria** - упрощает автоматический анализ
3. **Используйте thinking blocks** - они показывают почему AI принял решение
4. **Ограничивайте max_turns** - предотвращает бесконечные диалоги
5. **Проверяйте отчеты** - там может быть много инсайтов для улучшения промптов

## 📚 Дополнительная документация

- [Claude 4.5 Features](https://docs.anthropic.com/en/docs/about-claude/models/whats-new-sonnet-4-5)
- [MCP Server Documentation](../mcp-server/README.md)
- [Backend API Documentation](../backend/README.md)

## 🤝 Contributing

Для добавления новых сценариев или персон:

1. Создайте файлы в `scenarios/` или `personas/`
2. Следуйте существующему формату
3. Протестируйте локально
4. Создайте Pull Request

## 📄 Лицензия

Часть проекта figma-product-catalog
