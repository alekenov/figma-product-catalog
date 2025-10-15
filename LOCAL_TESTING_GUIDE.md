# 🚀 Локальный Тест Авторизации Telegram Бота

## 📍 Основной Бот для Тестирования

```
📁 /telegram-bot/bot.py
```

**Это основной бот** который был улучшен с обязательной авторизацией.

---

## 🛠️ Полный Стек для Локального Запуска

```
┌─────────────────────────────────────────┐
│ 1. Backend (port 8014)                  │
│    FastAPI + SQLite БД                  │
│    Handles API requests                 │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 2. MCP Server (port 8000)               │
│    API Tools Provider                   │
│    list_products, create_order, etc     │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 3. Telegram Bot (polling mode)          │
│    /telegram-bot/bot.py                 │
│    With authorization ✅                │
└─────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 4. Your Telegram Client                 │
│    Test with real Telegram app          │
└─────────────────────────────────────────┘
```

**Опционально:**
```
┌─────────────────────────────────────────┐
│ AI Agent Service V2 (port 8001)         │
│ (не обязателен для базового теста)      │
└─────────────────────────────────────────┘
```

---

## 🚀 Быстрый Старт (4 терминала)

### Terminal 1: Backend
```bash
cd /Users/alekenov/figma-product-catalog/backend

# Активировать виртуальное окружение (если нужно)
python3 -m venv .venv
source .venv/bin/activate

# Установить зависимости (один раз)
pip install -r requirements.txt

# Запустить backend
python main.py
```

✅ **Ожидаемый вывод:**
```
backend_starting project_name=Figma Product Catalog API
database_tables_created
seeds_applied
backend_started_successfully
```

---

### Terminal 2: MCP Server
```bash
cd /Users/alekenov/figma-product-catalog/mcp-server

# Активировать виртуальное окружение (если нужно)
python3 -m venv .venv
source .venv/bin/activate

# Установить зависимости (один раз)
pip install -r requirements.txt

# Запустить MCP сервер
python server.py
# или
./start.sh
```

✅ **Ожидаемый вывод:**
```
Starting MCP server on http://localhost:8000
Server listening on port 8000
```

---

### Terminal 3: Telegram Bot

```bash
cd /Users/alekenov/figma-product-catalog/telegram-bot

# Активировать виртуальное окружение (если нужно)
python3 -m venv .venv
source .venv/bin/activate

# Установить зависимости (один раз)
pip install -r requirements.txt

# Проверить .env (должны быть установлены переменные)
cat .env

# Запустить бот в polling режиме
python bot.py
```

✅ **Ожидаемый вывод:**
```
telegram_bot_starting shop_id=8
Bot initialized successfully
Starting bot in polling mode...
```

---

### Terminal 4: Тестирование

Откройте Telegram и напишите вашему боту.

**Бот для тестирования:**
```
Имя: Flower Shop Bot (или как вы его назвали)
Username: your_shop_bot (или как вы его создали)
```

---

## ✅ Тестовые Сценарии

### Сценарий 1: Новый Пользователь (НЕ авторизован)

```
🤖 Вы: /start

🤖 Бот ответит:
📱 Для полного доступа к функциям бота необходимо поделиться контактом.

Это нужно для:
• Оформления заказов
• Отслеживания доставки
• Сохранения ваших данных

Нажмите кнопку ниже, чтобы авторизоваться:
[Кнопка] 📱 Поделиться контактом
```

✅ **Ожидается:** Бот просит авторизацию

---

### Сценарий 2: Попытка Писать Без Авторизации

```
🤖 Вы: Привет!

🤖 Бот ответит:
📱 Для полного доступа к функциям бота необходимо поделиться контактом.

Это нужно для:
• Оформления заказов
• Отслеживания доставки
• Сохранения ваших данных

Нажмите кнопку ниже, чтобы авторизоваться:
[Кнопка] 📱 Поделиться контактом
```

✅ **Ожидается:** Бот просит авторизацию даже на простое сообщение ⭐

---

### Сценарий 3: Просмотр Каталога Без Авторизации

```
🤖 Вы: /catalog

🤖 Бот ответит:
📱 Для полного доступа к функциям бота необходимо поделиться контактом.

Это нужно для:
• Оформления заказов
• Отслеживания доставки
• Сохранения ваших данных

Нажмите кнопку ниже, чтобы авторизоваться:
[Кнопка] 📱 Поделиться контактом
```

✅ **Ожидается:** Бот просит авторизацию

---

### Сценарий 4: Авторизация Через Контакт

```
1️⃣ Нажать кнопку "📱 Поделиться контактом"

2️⃣ Telegram запросит разрешение:
   "Flower Shop Bot хочет доступ к вашему контакту"
   [Разрешить] [Отклонить]

3️⃣ Нажать "Разрешить"

4️⃣ Бот ответит:
✅ Спасибо! Вы успешно авторизованы.

Теперь вы можете:
🌹 Выбрать букет из каталога
🛒 Оформить заказ на доставку
📦 Отследить ваш заказ

Просто напишите мне, что вам нужно, или используйте:
/catalog - Каталог
/myorders - Мои заказы
/help - Помощь
```

✅ **Ожидается:** Успешная авторизация!

---

### Сценарий 5: После Авторизации (ВСЕ функции работают)

```
🤖 Вы: /catalog

🤖 Бот ответит:
Выберите категорию:
[🌹 Готовые букеты] [✨ На заказ]
[🔄 Подписки]       [🔍 Поиск]
```

✅ **Ожидается:** Каталог доступен!

```
🤖 Вы: Покажи букеты до 10000 тенге

🤖 Бот ответит:
Вот букеты до 10 000 ₸:
1. Букет 'Нежность' — 9 000 ₸
2. Букет 'Романтика' — 8 500 ₸
...
```

✅ **Ожидается:** AI обрабатывает запрос!

```
🤖 Вы: /myorders

🤖 Бот ответит:
Отследи мои заказы по номеру...
[обработка через AI]
Ваши заказы: ...
```

✅ **Ожидается:** Заказы отслеживаются!

---

## 🗄️ Проверка БД Во Время Тестирования

**В отдельном терминале 5:**

```bash
# Посмотреть, когда пользователь авторизовался
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT id, phone, customerName, telegram_user_id, telegram_username, created_at
FROM client
WHERE telegram_user_id IS NOT NULL
ORDER BY created_at DESC;
EOF
```

**После авторизации увидите:**
```
id | phone      | customerName | telegram_user_id | telegram_username | created_at
-- | ---------- | ------------ | --------------- | --------- ---- | ------
10 | +77015... | Иван П.    | 123456789        | ivan_petrov    | 2025-10-15 15:30:00
```

✅ **Данные сохранены в БД!**

---

## 🔧 Конфигурация (`.env`)

**Уже готово в `/telegram-bot/.env`:**

```env
# Telegram бот (тестовый)
TELEGRAM_TOKEN=5261424288:AAEDEY3pfLVIHIkFJnRtLGM_qLNjJcbbjrs

# Локальный Backend
BACKEND_API_URL=http://localhost:8014/api/v1

# Локальный MCP Server
MCP_SERVER_URL=http://localhost:8000

# Магазин
DEFAULT_SHOP_ID=8

# Для локального теста - оставить пустым (polling режим)
# WEBHOOK_URL=
# WEBHOOK_PORT=8080
```

✅ **Все готово для локального тестирования!**

---

## 📊 Проверка Компонентов

### Проверить Backend:
```bash
curl http://localhost:8014/health
```

✅ **Ожидаемый результат:**
```json
{
  "status": "healthy",
  "service": "backend",
  "checks": {"database": {"status": "healthy"}}
}
```

### Проверить MCP Server:
```bash
curl http://localhost:8000/health
```

✅ **Ожидаемый результат:**
```json
{"status": "healthy"}
```

### Проверить БД:
```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db "SELECT COUNT(*) FROM client;"
```

✅ **Ожидаемый результат:**
```
8
```

---

## 🐛 Общие Проблемы и Решения

### Проблема 1: "Bot doesn't respond"

```bash
# Проверить логи бота (Terminal 3)
# Должны быть:
# - "telegram_bot_starting"
# - "Bot initialized successfully"
# - "Starting bot in polling mode..."

# Проверить TELEGRAM_TOKEN:
grep TELEGRAM_TOKEN /telegram-bot/.env

# Проверить MCP сервер:
curl http://localhost:8000/health
```

### Проблема 2: "Connection refused: Backend"

```bash
# Проверить Backend запущен:
curl http://localhost:8014/health

# Если не работает - запустить Backend (Terminal 1):
cd /backend && python main.py
```

### Проблема 3: "Connection refused: MCP Server"

```bash
# Проверить MCP запущен:
curl http://localhost:8000/health

# Если не работает - запустить MCP (Terminal 2):
cd /mcp-server && python server.py
```

### Проблема 4: Авторизация не сохраняется в БД

```bash
# Проверить логи Backend (Terminal 1) на ошибки
# Проверить БД:
sqlite3 /backend/figma_catalog.db "SELECT * FROM client LIMIT 10;"

# Проверить API endpoint:
curl -X POST http://localhost:8014/api/v1/clients/telegram/register \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_user_id": "123",
    "phone": "77015211545",
    "customer_name": "Test",
    "shop_id": 8
  }'
```

---

## 📝 Логи и Отладка

### Посмотреть логи бота (Terminal 3):
```
Нажать Ctrl+C и запустить заново или просто смотреть консоль
```

### Посмотреть логи Backend (Terminal 1):
```
Там будут все запросы к API
```

### Посмотреть логи MCP (Terminal 2):
```
Там будут все вызовы tools
```

### Проверить БД в реальном времени:
```bash
# Terminal 5 (отдельный):
watch 'sqlite3 /backend/figma_catalog.db "SELECT COUNT(*), COUNT(CASE WHEN telegram_user_id IS NOT NULL THEN 1 END) FROM client;"'
```

Обновляется каждые 2 секунды показывая:
- Всего клиентов
- Авторизованных Telegram пользователей

---

## 🎯 Финальная Проверка

Все готово если:

```
✅ Terminal 1 (Backend):
   - Shows "backend_started_successfully"

✅ Terminal 2 (MCP Server):
   - Shows "Server listening on port 8000"

✅ Terminal 3 (Bot):
   - Shows "Starting bot in polling mode..."

✅ Terminal 4 (Telegram):
   - Бот отвечает на /start

✅ Terminal 5 (БД):
   - curl http://localhost:8014/health ← healthy
   - curl http://localhost:8000/health ← healthy
```

---

## 🚀 Готово!

Все компоненты запущены локально:
- ✅ Backend на port 8014
- ✅ MCP Server на port 8000
- ✅ Telegram Bot в polling режиме
- ✅ SQLite БД готова к сохранению данных
- ✅ Авторизация требуется везде

**Теперь тестируйте авторизацию в Telegram!** 🎉
