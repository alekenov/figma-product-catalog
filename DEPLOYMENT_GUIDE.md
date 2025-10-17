# 🚀 Deployment Guide - Локальная разработка и Railway Production

## 📊 Архитектура системы

### **Локальная разработка (SQLite)**
```
┌─────────────────────────────────────────────────────┐
│  LOCAL DEVELOPMENT STACK                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Backend API                                        │
│  └─ http://localhost:8014                          │
│  └─ SQLite: figma_catalog.db                       │
│  └─ No DATABASE_URL in .env                        │
│                                                     │
│  MCP Server                                         │
│  └─ http://localhost:8000                          │
│                                                     │
│  AI Agent Service                                   │
│  └─ http://localhost:8002                          │
│                                                     │
│  Telegram Bot (Polling mode)                       │
│  └─ Test bot: 8080729458:AAEwmnBrSDN-n1IEOYS4w0balnBjD0d6yqo│
│  └─ WEBHOOK_URL="" (empty)                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### **Railway Production (PostgreSQL)**
```
┌─────────────────────────────────────────────────────┐
│  RAILWAY PRODUCTION STACK                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Backend API                                        │
│  └─ figma-product-catalog-production.up.railway.app│
│  └─ PostgreSQL (Railway managed)                   │
│  └─ DATABASE_URL set by Railway                    │
│                                                     │
│  MCP Server                                         │
│  └─ mcp-server-production-00cd.up.railway.app     │
│                                                     │
│  AI Agent Service                                   │
│  └─ ai-agent-service-production-c331.up.railway.app│
│                                                     │
│  Telegram Bot (Webhook mode)                       │
│  └─ Prod bot: 8080729458:AAGTAKgoqC87chAKkV5AlpAuG33kWjvdIhA│
│  └─ WEBHOOK_URL=telegram-bot-production-75a7.up... │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔑 Переменные окружения

### Локальная разработка

#### `backend/.env`
```bash
# DATABASE_URL закомментирована - используется SQLite автоматически
# DATABASE_URL=

DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production-12345
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5176,http://localhost:5179,http://localhost:5180
```

#### `telegram-bot/.env`
```bash
# Тест бот (отдельный от продакшна)
TEST_TELEGRAM_TOKEN=8080729458:AAEwmnBrSDN-n1IEOYS4w0balnBjD0d6yqo
TELEGRAM_TOKEN=  # Пусто - будет использован TEST_TELEGRAM_TOKEN

# Локальные сервисы
BACKEND_API_URL=http://localhost:8014/api/v1
MCP_SERVER_URL=http://localhost:8000
AI_AGENT_URL=http://localhost:8002

# Webhook пустой для polling mode
WEBHOOK_URL=
```

### Railway Production

```bash
# Переменные устанавливаются через Railway CLI:
railway variables --set TELEGRAM_TOKEN=8080729458:AAGTAKgoqC87chAKkV5AlpAuG33kWjvdIhA
railway variables --set BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
railway variables --set WEBHOOK_URL=https://telegram-bot-production-75a7.up.railway.app
railway variables --set DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-set by Railway
```

---

## 🛠 Локальная установка

### 1. Инициализация SQLite базы данных

```bash
cd backend

# Создать чистую БД с seed данными
./init_local_db.sh

# Или сохранить существующую БД и только обновить схему
./init_local_db.sh --keep
```

**Тестовые учетные данные:**
- Логин: `+77015211545`
- Пароль: `1234`
- Shop ID: `8`
- Тест Telegram ID: `123456789`

### 2. Запуск Backend

```bash
cd backend
python3 main.py
```

Проверка: http://localhost:8014/docs

### 3. Запуск MCP Server

```bash
cd mcp-server
./start.sh
```

### 4. Запуск AI Agent

```bash
cd ai-agent-service
python main.py
```

### 5. Запуск Telegram Bot

```bash
cd telegram-bot
python bot.py  # Автоматически использует polling mode
```

---

## 🚢 Деплой на Railway

### Требования
- Railway CLI установлен: `npm install -g railway`
- Авторизован: `railway login`

### Деплой Backend

```bash
cd backend
railway link  # Выбрать backend service
railway variables --set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables --set SECRET_KEY=random-secure-key-here
railway up --ci
```

### Деплой Telegram Bot

```bash
cd telegram-bot
railway link  # Выбрать telegram-bot service

# Установить продакшн токен
railway variables --set TELEGRAM_TOKEN=8080729458:AAGTAKgoqC87chAKkV5AlpAuG33kWjvdIhA

# URL сервисов
railway variables --set BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
railway variables --set MCP_SERVER_URL=https://mcp-server-production-00cd.up.railway.app
railway variables --set AI_AGENT_URL=https://ai-agent-service-production-c331.up.railway.app

# Webhook mode
railway variables --set WEBHOOK_URL=https://telegram-bot-production-75a7.up.railway.app
railway variables --set WEBHOOK_PORT=8080

railway up --ci
```

### Проверка деплоя

```bash
# Логи
railway logs --deploy

# Health check
curl https://figma-product-catalog-production.up.railway.app/health
```

---

## 🔄 Workflow: Локал → Продакшн

### 1. Разработка локально

```bash
# Terminal 1: Backend
cd backend && python3 main.py

# Terminal 2: Bot
cd telegram-bot && python bot.py

# Тестирование в тест боте
```

### 2. Коммит изменений

```bash
git add .
git commit -m "feat: Add feature X"
git push origin main
```

### 3. Деплой на Railway

Railway автоматически деплоит при push в main (если настроен webhook).

Или вручную:
```bash
railway up --ci
```

---

## 🐛 Troubleshooting

### Проблема: Бот не знает мой номер телефона

**Причина**: Авторизация проверяется через backend API

**Решение:**
```bash
# Проверить что backend доступен
curl http://localhost:8014/api/v1/telegram/client?telegram_user_id=123&shop_id=8

# Проверить что BACKEND_API_URL правильный в telegram-bot/.env
cat telegram-bot/.env | grep BACKEND_API_URL

# Проверить логи бота
tail -f telegram-bot/logs/bot.log
```

### Проблема: SQLite база пустая

**Решение:**
```bash
cd backend
./init_local_db.sh  # Пересоздать с seed данными
```

### Проблема: Railway бот не отвечает

**Проверка:**
```bash
# Логи
railway logs -d 50

# Переменные
railway variables --kv | grep BACKEND_API_URL
```

### Проблема: Конфликт двух ботов (409 Conflict)

**Причина**: Два бота с одним токеном работают одновременно

**Решение:**
```bash
# Остановить локальный бот
pkill -f "python bot.py"

# Или использовать TEST_TELEGRAM_TOKEN локально
```

---

## 📝 Checklist перед деплоем

- [ ] Backend тесты пройдены: `cd backend && pytest`
- [ ] Seed данные загружены локально
- [ ] Telegram бот работает локально
- [ ] .env файлы НЕ закоммичены
- [ ] Railway переменные установлены правильно
- [ ] TELEGRAM_TOKEN на Railway - продакшн бот
- [ ] BACKEND_API_URL указывает на Railway backend

---

## 🔐 Безопасность

### Что НЕ коммитить:
- `*.env` файлы
- `*.db` файлы (SQLite)
- API токены и секреты

### .gitignore обязательно должен содержать:
```
.env
*.db
*.log
```

---

## 📚 Дополнительно

- [LOCAL_SETUP.md](./LOCAL_SETUP.md) - Детальная инструкция по локальной установке
- [telegram-bot/README.md](./telegram-bot/README.md) - Документация по боту
- [backend/README.md](./backend/README.md) - Документация по API
