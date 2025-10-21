# Cvety.kz Production Customer Bot

Production Telegram bot for cvety.kz customers with Claude AI integration for visual product search and natural language ordering.

## 🌸 Features

- **Visual Search**: Send a photo of a bouquet to find similar products
- **Natural Language Ordering**: Order flowers using conversational language
- **AI-Powered Assistance**: Claude Sonnet 4.5 with 40+ MCP tools
- **Kaspi Pay Integration**: Seamless payment processing
- **Order Tracking**: Real-time order status updates

## 🏗️ Architecture

```
Customer (Telegram)
    ↓
Cvety Bot (Railway) - webhook mode
    ↓
AI Agent Service (Claude Sonnet 4.5)
    ↓
MCP Server (40+ tools)
    ↓
Backend API (shop_id=17008)
    ↓
Production Database (cvety.kz - 185.125.90.141)
```

## 🚀 Deployment (Railway)

### Prerequisites
1. Production Telegram bot token from @BotFather
2. Railway account linked to GitHub repo
3. Environment variables configured

### Environment Variables

**Set via Railway UI (NOT in .env file):**

```bash
# Telegram (from @BotFather)
TELEGRAM_TOKEN=your_production_token

# Shop Configuration
DEFAULT_SHOP_ID=17008

# Service URLs (Railway auto-detects)
AI_AGENT_URL=https://ai-agent-service-production-c331.up.railway.app
MCP_SERVER_URL=https://mcp-server-production-00cd.up.railway.app
BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1

# Webhook (Railway auto-sets)
WEBHOOK_URL=${{RAILWAY_PUBLIC_DOMAIN}}
WEBHOOK_SECRET=<generate-random-string>

# Logging
LOG_LEVEL=INFO
```

### Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add cvety-bot/
   git commit -m "feat: Add cvety-bot production customer bot"
   git push origin main
   ```

2. **Create Railway Service:**
   - Go to Railway dashboard
   - Create new service from GitHub repo
   - Select `cvety-bot/` as root directory
   - Railway auto-detects `railway.json` config

3. **Configure Environment Variables:**
   - Add all required variables via Railway UI
   - Generate `WEBHOOK_SECRET`: `openssl rand -hex 32`

4. **Set Webhook in Telegram:**
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
     -d "url=https://cvety-bot-production.up.railway.app/webhook/<WEBHOOK_SECRET>"
   ```

5. **Verify Deployment:**
   ```bash
   railway logs --service cvety-bot
   ```

## 🧪 Local Development

**NOT RECOMMENDED** - this bot is designed for production webhook mode only.

For local testing, use the original `visual_search_ai_bot.py` (polling mode).

## 📁 Project Structure

```
cvety-bot/
├── bot.py              # Main bot application (webhook mode)
├── mcp_client.py       # MCP server client
├── formatters.py       # Product image formatters
├── logging_config.py   # Structured logging setup
├── requirements.txt    # Python dependencies
├── railway.json        # Railway deployment config
├── .env.example        # Example environment variables
└── README.md           # This file
```

## 🔐 Security

- **Tokens in Railway UI only** - NEVER commit to Git
- **Webhook secret** - Protects webhook endpoint
- **HTTPS only** - Telegram requires SSL for webhooks
- **Environment isolation** - Production vs development separation

## 📊 Monitoring

### Railway Logs
```bash
railway logs --service cvety-bot --deployment
```

### Health Check
```bash
curl https://cvety-bot-production.up.railway.app/health
```

### Webhook Info
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

## 🛠️ Troubleshooting

### Webhook not receiving updates
1. Check webhook is set: `getWebhookInfo`
2. Verify Railway service is running: `railway status`
3. Check logs: `railway logs`
4. Verify WEBHOOK_URL includes https://

### Bot not responding
1. Check AI Agent Service status (Railway)
2. Verify MCP Server is running
3. Check backend API health
4. Review bot logs for errors

## 📝 Related Services

- **Backend**: https://figma-product-catalog-production.up.railway.app
- **AI Agent**: https://ai-agent-service-production-c331.up.railway.app
- **MCP Server**: https://mcp-server-production-00cd.up.railway.app
- **Admin Bot**: `/admin-bot` (internal management)

## 🔗 Links

- [Railway Dashboard](https://railway.app/project/positive-exploration)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Docs](https://docs.python-telegram-bot.org/)
