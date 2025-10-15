# 🗄️ Проверка Данных в БД Напрямую

## 📍 Локация БД

```
Local Development: /backend/figma_catalog.db (SQLite)
Production: Railway PostgreSQL (через DATABASE_URL)
```

---

## 📋 Структура таблицы `client` (где хранятся Telegram пользователи)

### Схема таблицы:
```sql
CREATE TABLE client (
    id INTEGER PRIMARY KEY,
    phone VARCHAR NOT NULL,                    -- Номер телефона
    customerName VARCHAR,                      -- Имя клиента
    notes VARCHAR,                             -- Заметки
    shop_id INTEGER NOT NULL,                  -- ID магазина (multi-tenancy)
    telegram_user_id VARCHAR,                  -- 🔑 Telegram ID пользователя
    telegram_username VARCHAR,                 -- @username в Telegram
    telegram_first_name VARCHAR,               -- Первое имя
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Индексы:
CREATE UNIQUE INDEX idx_client_phone_shop ON client (phone, shop_id);
CREATE INDEX idx_client_telegram_user_shop ON client (telegram_user_id, shop_id);
```

---

## 🔍 Команды для проверки данных

### 1️⃣ **Все клиенты (включая неавторизованных)**

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db \
  "SELECT id, phone, customerName, telegram_user_id, created_at FROM client ORDER BY created_at DESC;"
```

**Результат:**
```
+----------+----------------+---------------------+------------------+---------------------+
| id       | phone          | customerName        | telegram_user_id | created_at          |
+----------+----------------+---------------------+------------------+---------------------+
| 8        | +77015211545   | Test Kaspi Customer |                  | 2025-10-14 10:10:43 |
| 7        | +77771234572   | Premature Feedback  |                  | 2025-10-08 10:00:35 |
| 1        | +77771234567   | Test Customer       |                  | 2025-10-14 09:50:37 |
+----------+----------------+---------------------+------------------+---------------------+
```

### 2️⃣ **Только авторизованные Telegram пользователи**

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  id,
  phone,
  customerName,
  telegram_user_id,
  telegram_username,
  telegram_first_name,
  created_at
FROM client
WHERE telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0
ORDER BY created_at DESC;
EOF
```

**Результат (если есть авторизованные):**
```
+----+----------------+---------------------+------------------+-------------------+---------------------+---------------------+
| id | phone          | customerName        | telegram_user_id | telegram_username | telegram_first_name | created_at          |
+----+----------------+---------------------+------------------+-------------------+---------------------+---------------------+
| 10 | +77015211545   | Иван Петров         | 123456789        | ivan_petrov       | Иван                | 2025-10-15 10:30:00 |
| 11 | +77088888888   | Мария Сидорова      | 987654321        | maria_sidorova    | Мария               | 2025-10-15 11:00:00 |
+----+----------------+---------------------+------------------+-------------------+---------------------+---------------------+
```

### 3️⃣ **Поиск конкретного Telegram пользователя по ID**

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  id,
  phone,
  customerName,
  telegram_user_id,
  telegram_username,
  telegram_first_name,
  created_at
FROM client
WHERE telegram_user_id = '123456789'  -- Замени на реальный Telegram ID
LIMIT 1;
EOF
```

### 4️⃣ **Поиск по номеру телефона**

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  id,
  phone,
  customerName,
  telegram_user_id,
  telegram_username,
  telegram_first_name,
  created_at
FROM client
WHERE phone = '77015211545'  -- Замени на реальный номер
LIMIT 1;
EOF
```

### 5️⃣ **Статистика авторизации**

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  COUNT(*) as total_clients,
  COUNT(CASE WHEN telegram_user_id IS NOT NULL AND LENGTH(telegram_user_id) > 0 THEN 1 END) as authorized_telegram,
  COUNT(CASE WHEN telegram_user_id IS NULL OR LENGTH(telegram_user_id) = 0 THEN 1 END) as not_authorized
FROM client
WHERE shop_id = 8;  -- Фильтр по shop_id если нужно
EOF
```

**Результат:**
```
+---------------+--------------------+------------------+
| total_clients | authorized_telegram| not_authorized   |
+---------------+--------------------+------------------+
| 8             | 0                  | 8                |
+---------------+--------------------+------------------+
```

### 6️⃣ **Все Telegram поля (для отладки)**

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  id,
  phone,
  telegram_user_id,
  telegram_username,
  telegram_first_name,
  customerName,
  created_at,
  updated_at
FROM client
WHERE shop_id = 8
ORDER BY created_at DESC;
EOF
```

### 7️⃣ **SQL для добавления тестового Telegram клиента вручную**

```sql
INSERT INTO client (
  phone,
  customerName,
  shop_id,
  telegram_user_id,
  telegram_username,
  telegram_first_name
) VALUES (
  '77015211545',                    -- Номер телефона
  'Тестовый пользователь',         -- Имя
  8,                                -- Shop ID
  '123456789',                      -- Telegram User ID
  'test_user',                      -- Username
  'Test'                            -- First name
);
```

---

## 🚀 Быстрые команды для терминала

### Создать SQL скрипт и выполнить:

```bash
# 1. Все клиенты с Telegram данными
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db \
  "SELECT phone, customerName, telegram_user_id, telegram_username, created_at FROM client;"

# 2. Только авторизованные
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db \
  "SELECT * FROM client WHERE telegram_user_id NOT NULL;"

# 3. Форматированный вывод
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db \
  -header -column \
  "SELECT id, phone, customerName, telegram_user_id, created_at FROM client;"
```

---

## 📊 Полезные команды SQLite

### Интерактивный режим:

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db

# В интерактивном режиме:
> .mode column          -- Вывод в колонках
> .headers on           -- Показать заголовки
> .width 15 20 20       -- Ширина колонок
> SELECT * FROM client;
> .quit                 -- Выход
```

### Экспорт в CSV:

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db \
  -header -csv \
  "SELECT id, phone, customerName, telegram_user_id FROM client;" > clients.csv
```

### Экспорт в JSON (SQLite 3.38+):

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db \
  -json \
  "SELECT * FROM client WHERE telegram_user_id IS NOT NULL;"
```

---

## 🔑 Типичные сценарии

### Сценарий 1: Проверить, авторизовался ли пользователь (после нажатия "Поделиться контактом")

```bash
# Замени 123456789 на реальный Telegram ID пользователя
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT * FROM client WHERE telegram_user_id = '123456789' AND shop_id = 8;
EOF
```

**Если записи нет** → Пользователь НЕ авторизован ❌
**Если запись есть** → Пользователь авторизован ✅

### Сценарий 2: Проверить номер телефона авторизованного пользователя

```bash
# Замени 123456789 на реальный Telegram ID
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT phone FROM client WHERE telegram_user_id = '123456789';
EOF
```

Результат:
```
77015211545
```

Этот номер сохраняется в БД и используется для отслеживания заказов!

### Сценарий 3: Удалить авторизацию (отладка)

```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
UPDATE client
SET telegram_user_id = NULL, telegram_username = NULL, telegram_first_name = NULL
WHERE phone = '77015211545';
EOF
```

После этого пользователь должен будет авторизоваться заново! ✅

---

## 🛠️ Для Production (Railway PostgreSQL)

Если нужно подключиться к Production БД в Railway:

```bash
# Получить CONNECTION_STRING из Railway dashboard:
psql "postgresql://user:password@host:port/database"

# Или использовать Railway CLI:
railway connect --database

# Затем выполнить те же SQL запросы:
SELECT * FROM client WHERE telegram_user_id IS NOT NULL;
```

---

## 📝 Заметки

- **Таблица:** `client` (а не `telegram_clients`)
- **Главные столбцы:** `telegram_user_id`, `phone`, `shop_id`
- **Уникальность:** `(telegram_user_id, shop_id)` - один пользователь на магазин
- **Индекс:** Есть индекс на `(telegram_user_id, shop_id)` для быстрого поиска
- **Локация:** `/backend/figma_catalog.db` (SQLite) для локальной разработки
- **Все данные привязаны к `shop_id`** для multi-tenancy поддержки

---

## ✅ Проверка связи Bot → Backend → DB

```
┌─────────────┐
│ Telegram    │
│ User        │
└────────┬────┘
         │ Нажимает "Поделиться контактом"
         ▼
┌─────────────────────────┐
│ telegram-bot/bot.py     │
│ handle_contact()        │
└────────┬────────────────┘
         │ POST /api/v1/clients/telegram/register
         ▼
┌─────────────────────────┐
│ backend/main.py         │
│ API endpoint            │
└────────┬────────────────┘
         │ INSERT INTO client (...)
         ▼
┌─────────────────────────┐
│ figma_catalog.db        │
│ Таблица: client         │
│ ✅ Данные сохранены!    │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Следующий запрос        │
│ check_authorization()   │
│ SELECT * FROM client    │
│ WHERE telegram_user_id  │
└─────────────────────────┘
```

Все готово! 🎉
