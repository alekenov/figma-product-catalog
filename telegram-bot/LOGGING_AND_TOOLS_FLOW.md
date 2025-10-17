# 🔍 Logging & Tool Calling Flow

## 📌 ПРОБЛЕМА: Логи видны только в терминале

Логи бота **НЕ сохраняются в базу данных** и **НЕ видны в нашем чате** потому что:

1. **Логи выводятся в STDOUT** (экран терминала)
2. Структурированное логирование (`structlog`) → JSON в консоль
3. Логи НЕ отправляются мне, только тебе в терминал
4. После перезагрузки бота - **логи удаляются**

---

## 🎯 РЕШЕНИЕ: Сохранять логи в файл

Нам нужно перенаправлять логи в файл, чтобы потом анализировать.

### Способ 1: Перенаправление при запуске

```bash
cd /Users/alekenov/figma-product-catalog/telegram-bot

# Запуск с сохранением логов в файл
python3 bot.py > bot_logs.txt 2>&1

# Или более детально
python3 bot.py > bot_$(date +%Y%m%d_%H%M%S).log 2>&1
```

**Потом можно читать логи:**
```bash
# Смотреть последние 50 строк в реальном времени
tail -f bot_logs.txt

# Поиск конкретного пользователя
grep "user_id=626599" bot_logs.txt

# Поиск ошибок
grep "ERROR" bot_logs.txt
```

### Способ 2: Логирование в БД (продвинутый)

Добавить в `bot.py`:

```python
import logging
from datetime import datetime

# Сохранять логи в файл
logging.basicConfig(
    filename=f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

---

## 🔗 TOOL CALLING FLOW (Как работают инструменты)

### Полная цепочка вызовов:

```
1. ПОЛЬЗОВАТЕЛЬ пишет сообщение
   ↓
2. TELEGRAM BOT получает обновление
   bot.py: handle_message()
   ├─ [LOG] message_received: user_id=626599, text="Мне нужны розы"
   ├─ [LOG] message_length=21
   └─ [LOG] request_id=req_a1b2c3d4 (для трейсинга)
   ↓
3. АВТОРИЗАЦИЯ (check_authorization)
   ├─ [LOG] authorization_check: user_id=626599, shop_id=8
   ├─ [CACHE HIT or MISS?]
   │  If MISS:
   │  │ [LOG] Calling MCP: get_telegram_client
   │  │ ├─ HTTP GET: /api/v1/telegram/client?telegram_user_id=626599&shop_id=8
   │  │ └─ [LOG] MCP response: 200 OK, client_record found
   │  └─ [LOG] Cache: auth_cache[626599] = (True, timestamp)
   │
   ├─ [LOG] authorization_result: is_authorized=True
   └─ If not authorized: [LOG] Requesting contact button, returning
   ↓
4. HTTP REQUEST К AI AGENT
   bot.py:
   ├─ [LOG] Calling AI Agent: POST /chat
   ├─ [LOG] Payload: {
   │     "message": "Мне нужны розы",
   │     "user_id": "626599",
   │     "channel": "telegram"
   │  }
   └─ [LOG] Timeout: 60s
   ↓
5. AI AGENT ОБРАБАТЫВАЕТ (ai-agent-service/main.py)
   ├─ [LOG] chat_endpoint_called
   ├─ [LOG] user_id=626599, message="Мне нужны розы"
   ├─ [LOG] Loading conversation history from DB
   ├─ [LOG] Building system prompt with MCP tools
   │
   ├─ CALL CLAUDE SONNET 4.5
   │ ├─ [LOG] Calling anthropic.messages.create()
   │ ├─ [LOG] Model: claude-sonnet-4-5-20250929
   │ ├─ [LOG] Tokens: input=250, output=180
   │ └─ [LOG] Stop reason: tool_use (Claude хочет вызвать инструмент!)
   │
   ├─ CLAUDE ВЫБРАЛ TOOLS:
   │ ├─ [LOG] Tool called: list_products
   │ ├─ [LOG] Tool params: {"search": "розы", "shop_id": 8}
   │ └─ Claude нужны продукты!
   │
   └─ ВЫЗОВ MCP TOOLS (mcp-server/server.py)
      ├─ [LOG] Tool execution: list_products
      ├─ [LOG] Params: search=розы, shop_id=8
      │
      ├─ MCP ВЫЗЫВАЕТ BACKEND API
      │ ├─ [LOG] HTTP GET: /api/v1/products?search=розы&shop_id=8
      │ ├─ Backend query database:
      │ │  SELECT * FROM product
      │ │  WHERE name LIKE '%розы%' AND shop_id=8 AND enabled=true
      │ │
      │ └─ [LOG] Result: 5 products found
      │
      ├─ [LOG] Tool result:
      │ ├─ Product 1: "Красные розы" - 2500000 копеек
      │ ├─ Product 2: "Розовые розы" - 2200000 копеек
      │ ├─ Product 3: "Белые розы" - 2300000 копеек
      │ ├─ Product 4: "Желтые розы" - 2100000 копеек
      │ └─ Product 5: "Микс роз" - 2800000 копеек
      │
      └─ Claude использует результаты для ответа
   ↓
6. CLAUDE ГЕНЕРИРУЕТ ОТВЕТ
   ├─ [LOG] Generating response with tool results
   ├─ [LOG] Response text: "Вот красные розы для вас..."
   ├─ [LOG] show_products: true (флаг для показа картинок)
   └─ [LOG] Saving to conversation history (SQLite)
   ↓
7. BOT ПОЛУЧАЕТ ОТВЕТ ОТ AI AGENT
   bot.py:
   ├─ [LOG] AI response received
   ├─ [LOG] Response text length: 285
   ├─ [LOG] show_products flag: True
   │
   ├─ ЕСЛИ show_products=true:
   │ ├─ [LOG] Fetching product images
   │ ├─ [LOG] Calling AI Agent: GET /products/626599
   │ ├─ [LOG] Images fetched: 5 items
   │ │
   │ ├─ ФОРМАТИРОВАНИЕ ДЛЯ TELEGRAM
   │ ├─ [LOG] Creating media group with 5 photos
   │ ├─ [LOG] Batch 1: photos 1-5 (max 10 per batch)
   │ └─ [LOG] Total batches: 1
   │
   └─ ОТПРАВКА В TELEGRAM
      ├─ [LOG] Sending media group to user
      ├─ [LOG] Caption: "Букет Красных Роз - 25000 ₸"
      └─ [LOG] Sent successfully
   ↓
8. ОТПРАВКА ТЕКСТА
   ├─ [LOG] Sending text response
   ├─ [LOG] Message split into 1 chunk (length < 4096)
   ├─ [LOG] Text: "Вот красные розы для вас..."
   └─ [LOG] Sent successfully
   ↓
9. ЗАВЕРШЕНИЕ
   ├─ [LOG] message_handling_success
   ├─ [LOG] Total time: 2.35s
   ├─ [LOG] request_id=req_a1b2c3d4 complete
   └─ [LOG] context cleared (no PII left in memory)
```

---

## 📊 ПРИМЕР РЕАЛЬНЫХ ЛОГОВ

### Что выведется в терминал:

```
[2025-10-16 15:30:45.123] [INFO] message_received
  timestamp=2025-10-16T15:30:45Z
  user_id=626599
  chat_id=626599
  message_length=21
  request_id=req_a1b2c3d4

[2025-10-16 15:30:45.234] [INFO] authorization_check
  user_id=626599
  shop_id=8
  request_id=req_a1b2c3d4

[2025-10-16 15:30:45.245] [INFO] authorization_cache_miss
  user_id=626599
  timestamp=1760596245.245
  request_id=req_a1b2c3d4

[2025-10-16 15:30:45.456] [INFO] authorization_check_success
  user_id=626599
  is_authorized=true
  request_id=req_a1b2c3d4

[2025-10-16 15:30:45.567] [INFO] ai_agent_call_start
  url=http://localhost:8002/chat
  timeout=60
  request_id=req_a1b2c3d4

[2025-10-16 15:30:47.890] [INFO] ai_agent_response_received
  status_code=200
  response_length=285
  show_products=true
  request_id=req_a1b2c3d4

[2025-10-16 15:30:47.891] [INFO] fetching_product_images
  product_count=5
  request_id=req_a1b2c3d4

[2025-10-16 15:30:48.123] [INFO] sending_media_group
  media_count=5
  batch_number=1
  request_id=req_a1b2c3d4

[2025-10-16 15:30:48.234] [INFO] sending_text_response
  message_length=285
  chunks=1
  request_id=req_a1b2c3d4

[2025-10-16 15:30:48.345] [INFO] message_handling_success
  total_time_ms=2220
  request_id=req_a1b2c3d4

[2025-10-16 15:30:48.346] [INFO] request_context_cleared
  request_id=req_a1b2c3d4
```

---

## 🔧 КАК НАСТРОИТЬ ЛОГИРОВАНИЕ

### Шаг 1: Создать директорию для логов

```bash
cd /Users/alekenov/figma-product-catalog/telegram-bot
mkdir -p logs
```

### Шаг 2: Запустить бот с сохранением логов

```bash
python3 bot.py | tee logs/bot_$(date +%Y%m%d_%H%M%S).log
```

**Что это делает:**
- `|` = передает вывод
- `tee` = одновременно выводит на экран И сохраняет в файл
- `logs/bot_*.log` = файл с датой и временем

### Шаг 3: Анализировать логи

```bash
# Последние 50 строк в реальном времени
tail -f logs/bot_20251016_153045.log

# Поиск конкретного пользователя
grep "user_id=626599" logs/bot_20251016_153045.log

# Подсчет сообщений
grep "message_received" logs/bot_20251016_153045.log | wc -l

# Поиск ошибок
grep -i "error\|failed\|exception" logs/bot_20251016_153045.log

# Timeline: вся история запроса
grep "request_id=req_a1b2c3d4" logs/bot_20251016_153045.log
```

---

## 📈 МЕТРИКИ ИЗ ЛОГОВ

**Из логов можно вывести:**

```bash
# Среднее время ответа
grep "message_handling_success" logs/bot_*.log | \
  sed 's/.*total_time_ms=\([0-9]*\).*/\1/' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count, "ms"}'

# Кол-во авторизованных пользователей
grep "is_authorized=true" logs/bot_*.log | cut -d'=' -f3 | sort -u | wc -l

# Кол-во уникальных пользователей
grep "message_received" logs/bot_*.log | \
  grep -o "user_id=[0-9]*" | cut -d'=' -f2 | sort -u | wc -l

# Процент кэш-попаданий
grep "authorization_cache_hit" logs/bot_*.log | wc -l
grep "authorization_cache_miss" logs/bot_*.log | wc -l
```

---

## 🎯 КАК ВИДЕТЬ TOOL CALLING

### Вариант 1: Смотреть в логах AI Agent

Запусти AI Agent в отдельном терминале:

```bash
cd /Users/alekenov/figma-product-catalog/ai-agent-service
python3 main.py | tee logs/ai_agent_$(date +%Y%m%d_%H%M%S).log
```

**Ты увидишь:**
```
[INFO] Chat endpoint called
[INFO] User message: "Мне нужны розы"
[INFO] Calling Claude Sonnet 4.5
[INFO] Claude returned tool_call: list_products
[INFO] Tool params: {"search": "розы", "shop_id": 8}
[INFO] Executing MCP tool: list_products
[INFO] MCP response: [5 products]
[INFO] Claude generated response: "Вот розы..."
```

### Вариант 2: Смотреть в логах MCP Server

```bash
cd /Users/alekenov/figma-product-catalog/mcp-server
./start.sh 2>&1 | tee logs/mcp_$(date +%Y%m%d_%H%M%S).log
```

**Ты увидишь:**
```
[INFO] Tool request: list_products
[INFO] Params: search=розы, shop_id=8
[INFO] Calling backend: GET /api/v1/products?search=розы&shop_id=8
[INFO] Backend response: 200 OK
[INFO] Found 5 products
[INFO] Tool result sent
```

### Вариант 3: Смотреть в логах Backend

Backend уже логирует, но давайте проверим:

```bash
cd /Users/alekenov/figma-product-catalog/backend

# Если запущен - можешь видеть логи в терминале
# Посмотри что выводится на экран
```

---

## 📝 ПОЛНЫЙ FLOW ЛОГИРОВАНИЯ

```
User Message
    ↓
┌───────────────────────────────────┐
│ TELEGRAM BOT LOGS (Terminal 4)    │
│ [INFO] message_received           │
│ [INFO] authorization_check        │
│ [INFO] ai_agent_call_start        │
└───────────────────────────────────┘
         ↓ HTTP POST
┌───────────────────────────────────┐
│ AI AGENT LOGS (Terminal 3)        │
│ [INFO] Chat endpoint called       │
│ [INFO] Claude processing          │
│ [INFO] Tool call: list_products   │
└───────────────────────────────────┘
         ↓ MCP Tool Request
┌───────────────────────────────────┐
│ MCP SERVER LOGS (Terminal 2)      │
│ [INFO] Tool: list_products        │
│ [INFO] Backend API call           │
└───────────────────────────────────┘
         ↓ HTTP Request
┌───────────────────────────────────┐
│ BACKEND LOGS (Terminal 1)         │
│ [INFO] GET /products              │
│ [INFO] Query: search=розы         │
│ [INFO] Result: 5 products         │
└───────────────────────────────────┘
         ↓ Response flows back
```

---

## 🎬 ПРАКТИЧЕСКИЙ ПРИМЕР

### Запусти всё с логированием:

**Terminal 1:**
```bash
cd backend
python3 main.py 2>&1 | tee logs/backend_$(date +%s).log
```

**Terminal 2:**
```bash
cd mcp-server
./start.sh 2>&1 | tee logs/mcp_$(date +%s).log
```

**Terminal 3:**
```bash
cd ai-agent-service
python3 main.py 2>&1 | tee logs/ai_agent_$(date +%s).log
```

**Terminal 4:**
```bash
cd telegram-bot
python3 bot.py 2>&1 | tee logs/bot_$(date +%s).log
```

**Terminal 5 (Анализ):**
```bash
# Смотри логи всех 4 сервисов одновременно
tail -f backend/logs/backend_*.log &
tail -f mcp-server/logs/mcp_*.log &
tail -f ai-agent-service/logs/ai_agent_*.log &
tail -f telegram-bot/logs/bot_*.log
```

---

## ✅ ИТОГ

**Теперь ты видишь:**
1. ✅ Где сохраняются логи (в файлы)
2. ✅ Как работает tool calling (Claude → MCP → Backend)
3. ✅ Какой поток логов генерирует каждый сервис
4. ✅ Как анализировать логи после запуска

**Главное:** Логи НЕ сохраняются автоматически - нужно использовать `tee` для сохранения в файл!
