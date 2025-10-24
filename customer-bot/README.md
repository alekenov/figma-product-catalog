# Customer Bot - Telegram Bot for Flower Shop Customers

AI-powered Telegram bot for customers to browse products, place orders, and track deliveries.

## 🎯 Purpose

This bot serves **customers** (not staff). Customers can:
- 📸 Search for bouquets by sending a photo (visual search)
- 🌹 Browse product catalog
- 🛒 Place orders using natural language
- 📦 Track order status
- 💳 Pay via Kaspi Pay (production)

For **staff/admin functions** (managing orders, inventory), see `/admin-bot`.

---

## 🏗️ Architecture

Supports two environments with separate databases:

### Production Environment
- **Shop ID**: 17008
- **Database**: Bitrix (185.125.90.141)
- **Mode**: Webhook (Railway deployment)
- **Users**: Real cvety.kz customers

### Development Environment
- **Shop ID**: 8
- **Database**: Railway PostgreSQL
- **Mode**: Polling (local testing)
- **Users**: Development/testing

---

## 🚀 Quick Start

### Production Deployment (Railway)

1. **Configure Environment Variables in Railway UI:**
   ```bash
   # Copy values from .env.production
   ENVIRONMENT=production
   TELEGRAM_TOKEN=<existing_cvety_bot_token>
   DEFAULT_SHOP_ID=17008
   MCP_SERVER_URL=https://mcp-server-production-00cd.up.railway.app
   AI_AGENT_URL=https://ai-agent-service-production-c331.up.railway.app
   BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
   WEBHOOK_URL=${{RAILWAY_PUBLIC_DOMAIN}}
   LOG_LEVEL=INFO
   ```

2. **Deploy:**
   ```bash
   git push origin main  # Auto-deploys to Railway
   ```

3. **Verify:**
   ```bash
   railway logs --service customer-bot-production
   ```

### Local Development

1. **Copy environment file:**
   ```bash
   cd customer-bot
   cp .env.example .env.development
   ```

2. **Edit `.env.development` with your tokens:**
   - Create new bot in @BotFather: "Cvety.kz Customer Bot (Dev)"
   - Username: `cvety_customer_dev_bot`
   - Get token and paste into `TELEGRAM_TOKEN`

3. **Start local backend services:**
   ```bash
   # Terminal 1: Backend API
   cd ../backend
   python main.py  # Runs on port 8014

   # Terminal 2: MCP Server
   cd ../mcp-server
   python server.py --transport streamable-http --port 8000

   # Terminal 3: AI Agent Service
   cd ../ai-agent-service
   python main.py  # Runs on port 8002
   ```

4. **Run bot:**
   ```bash
   cd customer-bot
   ENVIRONMENT=development python bot.py
   ```

   Bot will start in **polling mode** (no webhook needed for local dev).

---

## 📝 Environment Variables

| Variable | Production | Development | Description |
|----------|-----------|-------------|-------------|
| `ENVIRONMENT` | `production` | `development` | Determines which .env file to load |
| `TELEGRAM_TOKEN` | Existing cvety-bot token | New dev token | Bot token from @BotFather |
| `DEFAULT_SHOP_ID` | `17008` | `8` | Multi-tenancy shop ID |
| `MCP_SERVER_URL` | Railway URL | `http://localhost:8000` | MCP server endpoint |
| `AI_AGENT_URL` | Railway URL | `http://localhost:8002` | AI agent service |
| `BACKEND_API_URL` | Railway URL | `http://localhost:8014/api/v1` | Backend API |
| `WEBHOOK_URL` | `${{RAILWAY_PUBLIC_DOMAIN}}` | (empty) | Webhook URL (empty = polling mode) |
| `LOG_LEVEL` | `INFO` | `DEBUG` | Logging verbosity |

---

## 🤖 Bot Commands

### For Customers

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and authorization |
| `/help` | Show available features and examples |

### Features

**Visual Search:**
```
Customer: [sends photo of a bouquet]
Bot: 🔍 Найдены похожие букеты:
     1. Букет "Романтика" - 15,000₸
     2. Букет "Нежность" - 18,000₸
     [Shows product photos]
```

**Natural Language Ordering:**
```
Customer: Хочу заказать букет роз на завтра к 15:00
Bot: [AI Agent collects details conversationally]
     ✅ Заказ #156 создан!
     Сумма: 12,000₸
     Доставка: завтра, 24.10.2025, 15:00
```

**Order Tracking:**
```
Customer: Где мой заказ?
Bot: Введите номер телефона
Customer: +77011234567
Bot: 📦 Ваши заказы:
     #156 - В обработке (создан 23.10.2025)
     #142 - Доставлен (20.10.2025)
```

---

## 🔧 Technical Stack

- **Framework**: python-telegram-bot 22.5
- **AI**: Claude Sonnet 4.5 (via AI Agent Service)
- **Tools**: 40+ MCP tools (products, orders, payments, etc.)
- **Database**: Bitrix (prod) / PostgreSQL (dev)
- **Deployment**: Railway (Nixpacks)

---

## 📁 Project Structure

```
customer-bot/
├── bot.py                  # Main bot application
├── mcp_client.py          # MCP server HTTP client
├── formatters.py          # Product image formatters
├── logging_config.py      # Structured logging
├── requirements.txt       # Python dependencies
├── railway.json           # Railway deployment config
├── .env.production        # Production environment vars
├── .env.development       # Development environment vars
├── .env.example           # Template for new setup
└── README.md              # This file
```

---

## 🔐 Security

- **Tokens**: NEVER commit `.env.production` or `.env.development` to Git
- **Multi-tenancy**: shop_id isolation enforced by backend
- **Webhook**: HTTPS-only (Telegram requirement)
- **Secrets**: Use Railway secret management for production

---

## 🐛 Troubleshooting

### Bot doesn't respond

1. **Check Telegram token:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```

2. **Check webhook status (production):**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```

3. **Check services are running:**
   - Backend API: `curl http://localhost:8014/health`
   - MCP Server: `curl http://localhost:8000/health`
   - AI Agent: `curl http://localhost:8002/health`

### Environment not loading

**Symptom**: Bot says "⚠️ .env.development not found"

**Solution**: Ensure you set `ENVIRONMENT` variable BEFORE running:
```bash
ENVIRONMENT=development python bot.py
```

### Polling vs Webhook confusion

| Mode | When? | WEBHOOK_URL | How to run |
|------|-------|-------------|------------|
| Polling | Local dev | Empty/not set | `ENVIRONMENT=development python bot.py` |
| Webhook | Production | Set by Railway | Automatic on Railway |

---

## 📊 Monitoring

### Railway Logs
```bash
railway logs --service customer-bot-production --follow
```

### Key Metrics
- User registrations (contact sharing)
- Photo searches (visual search)
- Order creations
- AI Agent response times

---

## 🔗 Related Services

- **Backend API**: `/backend`
- **MCP Server**: `/mcp-server`
- **AI Agent**: `/ai-agent-service`
- **Admin Bot**: `/admin-bot` (for staff)

---

## 📝 Development Notes

### Adding New Features

1. Customer features go in `customer-bot/bot.py`
2. Admin features go in `/admin-bot/` (different bot!)
3. Shared logic can be extracted to modules

### Testing Locally

Always test with `ENVIRONMENT=development` to avoid affecting production data:
```bash
# Wrong - will try to connect to production services
python bot.py

# Correct - uses local services and shop_id=8
ENVIRONMENT=development python bot.py
```

---

## 📞 Support

For issues or questions:
- Backend API: See `/backend/README.md`
- MCP Server: See `/mcp-server/README.md`
- Project docs: See `/CLAUDE.md`
