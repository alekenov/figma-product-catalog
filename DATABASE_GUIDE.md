# 🗄️ Полный Гайд по БД - Хранение Telegram Клиентов

## 📊 Текущее состояние

```
✅ Всего клиентов в магазине (shop_id=8): 8
✅ Авторизованы через Telegram:          0
✅ НЕ авторизованы:                      8
```

**Это нормально!** Клиенты в БД созданы через seeds (тестовые данные), а не через Telegram бот.

---

## 🏗️ Архитектура хранения

```
┌─────────────────────────────────────┐
│ Telegram Bot                        │
│ /telegram-bot/bot.py                │
└────────────┬────────────────────────┘
             │
             │ handle_contact()
             │ Получает: phone, telegram_user_id
             │
             ▼
┌─────────────────────────────────────┐
│ MCP Client                          │
│ register_telegram_client()          │
└────────────┬────────────────────────┘
             │
             │ HTTP POST
             │ /api/v1/clients/telegram/register
             │
             ▼
┌─────────────────────────────────────┐
│ Backend FastAPI                     │
│ /backend/main.py                    │
│ api/clients.py                      │
└────────────┬────────────────────────┘
             │
             │ INSERT INTO client (...)
             │
             ▼
┌─────────────────────────────────────┐
│ SQLite Database                     │
│ /backend/figma_catalog.db           │
│ Таблица: client                     │
└─────────────────────────────────────┘
```

---

## 🔑 Таблица `client` - Структура

```sql
CREATE TABLE client (
    id INTEGER PRIMARY KEY,

    -- Основная информация
    phone VARCHAR NOT NULL,                    -- Номер телефона
    customerName VARCHAR,                      -- Имя клиента
    notes VARCHAR,                             -- Заметки
    shop_id INTEGER NOT NULL,                  -- ID магазина (для multi-tenancy)

    -- Telegram данные (заполняются при авторизации)
    telegram_user_id VARCHAR,                  -- 🔑 Уникальный ID Telegram пользователя
    telegram_username VARCHAR,                 -- @username в Telegram (опционально)
    telegram_first_name VARCHAR,               -- Первое имя (опционально)

    -- Метаданные
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(shop_id) REFERENCES shop (id)
);

-- Индексы для быстрого поиска:
CREATE UNIQUE INDEX idx_client_phone_shop ON client (phone, shop_id);
CREATE INDEX idx_client_telegram_user_shop ON client (telegram_user_id, shop_id);
```

---

## 📍 Где находится БД?

### Development (Local)
```
📁 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db

📝 SQLite формат
🔌 Не требует запущенного сервера
⚡ Идеально для локальной разработки
```

### Production (Railway)
```
📁 Railway PostgreSQL Service
🔑 Подключение через DATABASE_URL env variable
☁️ Автоматически бэкапируется
```

---

## 🚀 Быстрые команды

### 1. Проверить авторизованных пользователей

```bash
# Все авторизованные Telegram пользователи
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  id,
  phone,
  customerName,
  telegram_user_id,
  telegram_username,
  created_at
FROM client
WHERE telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0
ORDER BY created_at DESC;
EOF
```

### 2. Поиск по Telegram ID

```bash
# Замени 123456789 на реальный ID
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT * FROM client WHERE telegram_user_id = '123456789';
EOF
```

### 3. Поиск по номеру телефона

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT * FROM client WHERE phone = '77015211545';
EOF
```

### 4. Статистика

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  COUNT(*) as total,
  COUNT(CASE WHEN telegram_user_id IS NOT NULL THEN 1 END) as with_telegram,
  COUNT(CASE WHEN telegram_user_id IS NULL THEN 1 END) as without_telegram
FROM client
WHERE shop_id = 8;
EOF
```

### 5. Использовать скрипт

```bash
bash /Users/alekenov/figma-product-catalog/QUICK_DB_CHECK.sh
```

---

## 🔄 Полный цикл Авторизации

### ШАГ 1: Пользователь нажимает "Поделиться контактом"

```python
# telegram-bot/bot.py (bot.py:294-340)
async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact  # Telegram отправляет контакт

    # Данные:
    telegram_user_id = str(user.id)      # "123456789"
    phone = contact.phone_number          # "+77015211545"
    customer_name = user.first_name       # "Иван"
```

### ШАГ 2: Бот отправляет запрос в Backend

```python
# telegram-bot/mcp_client.py (мcp_client.py:202-241)
await self.mcp_client.register_telegram_client(
    telegram_user_id="123456789",
    phone="+77015211545",
    customer_name="Иван Петров",
    shop_id=8,
    telegram_username="ivan_petrov",
    telegram_first_name="Иван"
)

# Отправляет HTTP POST:
# POST http://localhost:8014/api/v1/clients/telegram/register
# {
#   "telegram_user_id": "123456789",
#   "phone": "+77015211545",
#   "customer_name": "Иван Петров",
#   "shop_id": 8,
#   "telegram_username": "ivan_petrov",
#   "telegram_first_name": "Иван"
# }
```

### ШАГ 3: Backend сохраняет в БД

```sql
-- backend/api/clients.py (api/clients.py)
INSERT INTO client (
    phone,
    customerName,
    shop_id,
    telegram_user_id,
    telegram_username,
    telegram_first_name,
    created_at,
    updated_at
) VALUES (
    '77015211545',
    'Иван Петров',
    8,
    '123456789',
    'ivan_petrov',
    'Иван',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
```

### ШАГ 4: Проверка авторизации работает

```python
# telegram-bot/bot.py (bot.py:87-97)
async def check_authorization(self, user_id: int) -> bool:
    client = await self.mcp_client.get_telegram_client(
        telegram_user_id=str(user_id),  # "123456789"
        shop_id=self.shop_id             # 8
    )
    # Backend ищет:
    # SELECT * FROM client WHERE telegram_user_id='123456789' AND shop_id=8

    return client is not None  # True - авторизован! ✅
```

---

## 🧪 Как Тестировать

### Тест 1: Неавторизованный пользователь

```bash
# 1. Запустить бот
cd telegram-bot && python bot.py

# 2. В Telegram:
/start
→ "Для использования бота необходимо поделиться контактом"

# 3. В БД:
sqlite3 /backend/figma_catalog.db "SELECT * FROM client WHERE telegram_user_id = <your_id>"
→ Пусто ❌
```

### Тест 2: После авторизации

```bash
# 1. Нажать "Поделиться контактом" в Telegram

# 2. В БД:
sqlite3 /backend/figma_catalog.db "SELECT * FROM client WHERE telegram_user_id = '<your_id>'"

# 3. Результат:
id   phone        customerName  telegram_user_id  telegram_username  created_at
--- ------------- ------------- --------- -------- -------- -------- -----------
10  +77015211545 Иван Петров   123456789 ivan_pet Иван     2025-10...

# 4. Теперь пользователь авторизован! ✅
```

---

## 📈 Статистика из Примера Выше

```
╔════════════════════════════════════════════════════════╗
║  📊 Текущее состояние БД (shop_id=8)                  ║
╠════════════════════════════════════════════════════════╣
║ Всего клиентов:           8                           ║
║ Авторизованы (Telegram):  0                           ║
║ НЕ авторизованы:          8                           ║
║ Процент авторизации:      0%                          ║
╚════════════════════════════════════════════════════════╝

Это тестовые данные из seeds!
После того как реальные пользователи авторизуются через бот,
статистика будет выглядеть так:

╔════════════════════════════════════════════════════════╗
║  📊 После авторизации 3 реальных пользователей       ║
╠════════════════════════════════════════════════════════╣
║ Всего клиентов:           11                          ║
║ Авторизованы (Telegram):  3                           ║
║ НЕ авторизованы:          8                           ║
║ Процент авторизации:      27.3%                       ║
╚════════════════════════════════════════════════════════╝
```

---

## 🔐 Что Защищает от Неавторизованного Доступа?

После наших улучшений, боту невозможно пользоваться БЕЗ авторизации:

```python
# ❌ ДО улучшений:
# Пользователь писал "привет" → бот обрабатывал (опасно!)

# ✅ ПОСЛЕ улучшений:
# Пользователь пишет "привет"
→ check_authorization() в handle_message()
→ SELECT * FROM client WHERE telegram_user_id='...' AND shop_id=8
→ Запись не найдена
→ Бот показывает: "📱 Для полного доступа к функциям бота..."
→ Просит авторизацию ✅
```

---

## 🎯 Ключевые Поля Для Отладки

При возникновении проблем, проверь эти поля:

| Поле | Значение | Что это значит |
|------|----------|----------------|
| `telegram_user_id` | `NULL` или пусто | Пользователь НЕ авторизован ❌ |
| `telegram_user_id` | `"123456789"` | Пользователь авторизован ✅ |
| `phone` | `"+77015211545"` | Номер для отслеживания заказов |
| `shop_id` | `8` | Магазин Almaty/Default |
| `created_at` | `2025-10-15 10:30:00` | Когда авторизовался |

---

## 🚨 Частые Проблемы и Решения

### Проблема 1: Пользователь авторизовался, но БД не обновляется

```bash
# Проверить логи бота:
cat /telegram-bot/logs/*.log | grep "register_telegram_client"

# Проверить API ответ:
curl -X POST http://localhost:8014/api/v1/clients/telegram/register \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Проблема 2: check_authorization() возвращает False

```bash
# 1. Проверить, есть ли запись в БД:
sqlite3 /backend/figma_catalog.db \
  "SELECT * FROM client WHERE telegram_user_id = '123456789'"

# 2. Проверить shop_id:
sqlite3 /backend/figma_catalog.db \
  "SELECT * FROM client WHERE telegram_user_id = '123456789' AND shop_id = 8"

# 3. Проверить индекс:
sqlite3 /backend/figma_catalog.db ".indexes client"
```

### Проблема 3: Номер телефона не сохраняется

```bash
# Проверить что приходит от Telegram:
grep "contact.phone_number" /telegram-bot/bot.py -A 5 -B 5

# Проверить что отправляется в Backend:
grep "register_telegram_client" /telegram-bot/mcp_client.py -A 10
```

---

## ✅ Финальная Проверка

Все работает правильно если:

```
✅ 1. Бот запущен: python /telegram-bot/bot.py
✅ 2. Backend запущен: python /backend/main.py (port 8014)
✅ 3. БД существует: ls -la /backend/figma_catalog.db
✅ 4. Таблица создана: sqlite3 /backend/figma_catalog.db ".tables" | grep client
✅ 5. Пользователь авторизуется: нажимает "Поделиться контактом"
✅ 6. Запись появляется в БД: sqlite3 /backend/figma_catalog.db "SELECT * FROM client"
✅ 7. Проверка работает: бот просит авторизацию если её нет
✅ 8. Данные используются: /myorders показывает заказы по сохраненному номеру
```

---

## 📚 Дополнительные ресурсы

- 📄 `/backend/figma_catalog.db` - Основная БД (SQLite)
- 📝 `DB_QUERIES.md` - Полный набор SQL запросов
- 🚀 `QUICK_DB_CHECK.sh` - Скрипт для быстрой проверки
- 🤖 `/telegram-bot/bot.py` - Telegram бот с авторизацией
- 🔌 `/backend/main.py` - Backend с API для клиентов
- 📋 `/backend/api/clients.py` - API endpoints для работы с клиентами

---

## 🎉 Готово!

Все компоненты работают вместе:
- Telegram бот собирает данные авторизации
- Backend сохраняет в БД
- Проверка авторизации работает для всех функций
- Номера телефонов сохраняются для отслеживания заказов

✅ Система готова к использованию!
