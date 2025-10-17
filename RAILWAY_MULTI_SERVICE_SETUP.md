# Railway Multi-Service Setup для Telegram Bot

## Проблема

При деплое через `railway up` все сервисы (AI Agent V2, MCP Server, Telegram Bot, Backend) попадают в **один Railway service**, перезаписывая друг друга.

Текущая структура:
- Railway CLI привязан к service "figma-product-catalog" (backend)
- Все `railway up` команды деплоят в этот же сервис
- Каждый новый деплой заменяет предыдущий

## Решение: Создать отдельные Railway Services

### Архитектура (3 сервиса):

```
1. Backend API          → https://figma-product-catalog-production.up.railway.app
2. AI Agent Service V2  → https://ai-agent-service-production-XXX.up.railway.app
3. Telegram Bot         → https://telegram-bot-production-75a7.up.railway.app
```

**MCP Server НЕ нужен** - AI Agent V2 работает напрямую с Backend API.

---

## Шаг 1: Создать AI Agent Service V2

### Через Railway Dashboard:

1. Открыть [Railway Dashboard](https://railway.com/project/311bb135-7712-402e-aacf-14ce8b0b80df)
2. Click "New Service" → "GitHub Repo"
3. Выбрать `alekenov/figma-product-catalog`
4. **Root Directory**: `/ai-agent-service`
5. **Service Name**: `ai-agent-service`

### Environment Variables:

```bash
CLAUDE_API_KEY=sk-ant-api03-YOUR_API_KEY_HERE
CLAUDE_MODEL=claude-sonnet-4-5-20250929
BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
DEFAULT_SHOP_ID=8
DATABASE_URL=${{Postgres.DATABASE_URL}}
PORT=${{RAILWAY_PUBLIC_PORT}}
CACHE_REFRESH_INTERVAL_HOURS=1
LOG_LEVEL=INFO
```

### Generate Domain:
Click "Generate Domain" для публичного URL.

---

## Шаг 2: Создать Telegram Bot Service

### Через Railway Dashboard:

1. Click "New Service" → "GitHub Repo"
2. Выбрать `alekenov/figma-product-catalog`
3. **Root Directory**: `/telegram-bot`
4. **Service Name**: `telegram-bot`

### Environment Variables:

```bash
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
AI_AGENT_URL=https://ai-agent-service-production-XXX.up.railway.app  # ← URL из Шага 1
MCP_SERVER_URL=https://figma-product-catalog-production.up.railway.app/api/v1  # ← Используем backend напрямую
BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
DEFAULT_SHOP_ID=8
WEBHOOK_URL=https://telegram-bot-production-75a7.up.railway.app  # ← URL этого сервиса
WEBHOOK_PORT=${{RAILWAY_PUBLIC_PORT}}
```

### Generate Domain:
Click "Generate Domain" для webhook URL.

### Set Telegram Webhook:

После деплоя выполнить:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://telegram-bot-production-75a7.up.railway.app/webhook"
```

---

## Шаг 3: Проверка

### 1. Backend API (уже работает)
```bash
curl https://figma-product-catalog-production.up.railway.app/health
# Должен вернуть: {"status":"healthy"}
```

### 2. AI Agent Service V2
```bash
curl https://ai-agent-service-production-XXX.up.railway.app/health
# Должен вернуть: {"status":"healthy", "service":"ai-agent-service"}
```

### 3. Telegram Bot Webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
# Должен показать: "url": "https://telegram-bot-production-75a7.up.railway.app/webhook"
```

### 4. Telegram Bot (@cvetykzsupportbot)
Отправить `/start` в Telegram → должен ответить.

---

## Альтернатива: Монолитный деплой

Если не хочешь создавать отдельные сервисы, можно:

1. **Удалить AI Agent Service V2** из архитектуры
2. **Telegram Bot работает напрямую с Backend API**
3. Нужно переписать `telegram-bot/bot.py` для прямой интеграции

Это проще, но теряем преимущества Prompt Caching (80-90% экономия токенов).

---

## Troubleshooting

### Ошибка: "terminated by other getUpdates request"
- Убедись, что webhook установлен правильно
- Проверь, что локально не запущен бот с тем же токеном
- Очисти webhook: `python telegram-bot/clear_webhook.py`

### AI Agent V2 не отвечает (504)
- Проверь DATABASE_URL (должен быть PostgreSQL)
- Проверь BACKEND_API_URL доступен
- Проверь логи: Railway Dashboard → AI Agent Service → Deployments → Logs

### Telegram Bot не получает сообщения
- Проверь webhook: `getWebhookInfo`
- Проверь AI_AGENT_URL доступен
- Проверь логи бота на Railway

---

## Следующие шаги

После создания сервисов:
1. ✅ Backend API уже работает
2. ⏳ Создать AI Agent Service V2 (через dashboard)
3. ⏳ Создать Telegram Bot Service (через dashboard)
4. ⏳ Установить webhook
5. ⏳ Тестировать бота в Telegram

**Важно**: После создания сервисов не забудь обновить URLs в environment variables!
