# Flower Shop Telegram Bot with Claude AI

AI-powered Telegram bot for flower shop with natural language ordering and catalog browsing.

## Architecture

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Telegram Bot   │  ◄── bot.py (this service)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Claude Sonnet   │  ◄── ai_handler.py
│  4.5 (AI)       │      (function calling)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Server    │  ◄── mcp_client.py
│  (API Tools)    │      (HTTP transport)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │  ◄── FastAPI on Railway
│  (PostgreSQL)   │
└─────────────────┘
```

## Features

- 🤖 **Natural Language AI**: Powered by Claude Sonnet 4.5
- 🌹 **Product Catalog**: Browse flowers, bouquets, subscriptions
- 🛒 **Smart Ordering**: AI collects order details conversationally
- 📦 **Order Tracking**: Track orders by phone number
- ⏰ **Shop Info**: Working hours, settings, contact info
- 🔧 **Function Calling**: AI determines which API tools to use
- 🌐 **Dual Mode**: Polling (local dev) or Webhook (Railway production)

## Prerequisites

1. **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
   ```
   /newbot
   Name: Flower Shop Bot
   Username: your_shop_bot
   ```

2. **Claude API Key**: Get from [console.anthropic.com](https://console.anthropic.com)

3. **MCP Server**: Must be deployed on Railway (see `/mcp-server/`)

4. **Backend API**: FastAPI service on Railway (already deployed)

## Local Development Setup

### 1. Clone and Navigate
```bash
cd telegram-bot
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Required
TELEGRAM_TOKEN=your_bot_token_from_botfather
CLAUDE_API_KEY=your_anthropic_api_key
BACKEND_API_URL=http://localhost:8014/api/v1  # Backend API
MCP_SERVER_URL=http://localhost:8000  # Local MCP server
DEFAULT_SHOP_ID=8

# Optional (for local testing, use polling mode)
# WEBHOOK_URL=  # Leave empty for polling
```

### 5. Start MCP Server (in another terminal)
```bash
cd ../mcp-server
python server.py --transport streamable-http --port 8000
```

### 6. Run Bot
```bash
python bot.py
```

Bot will run in **polling mode** (no webhook needed for local dev).

## Railway Deployment

### 1. Create Railway Service
```bash
railway service create
# Name: telegram-bot
```

### 2. Set Environment Variables
```bash
railway variables --set TELEGRAM_TOKEN=your_token
railway variables --set CLAUDE_API_KEY=your_key
railway variables --set BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1
railway variables --set MCP_SERVER_URL=https://your-mcp-server.railway.app
railway variables --set AI_AGENT_URL=https://your-ai-agent.railway.app
railway variables --set DEFAULT_SHOP_ID=8
railway variables --set WEBHOOK_URL=https://telegram-bot-production.up.railway.app
railway variables --set WEBHOOK_PORT=8080
```

### 3. Deploy
```bash
railway up --ci
```

Railway will:
- Detect Python project (Nixpacks)
- Install dependencies from `requirements.txt`
- Run `./start-railway.sh`
- Bot will use **webhook mode** (WEBHOOK_URL is set)

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and introduction |
| `/catalog` | Browse product categories |
| `/myorders` | Track orders by phone number |
| `/clear` | Clear conversation history |
| `/help` | Show help and usage examples |

## Usage Examples

### Browse Catalog
```
User: Покажи готовые букеты
Bot: [AI lists ready-made bouquets using list_products]

User: Есть что-то до 10000 тенге?
Bot: [AI filters by price and shows results]
```

### Create Order
```
User: Хочу заказать букет роз на завтра
Bot: Отлично! Как вас зовут?
User: Айгуль
Bot: Спасибо! Укажите номер телефона
User: +77011234567
Bot: На какой адрес доставить?
User: Алматы, Абая 150
Bot: В какое время удобно? (например, 15:00)
User: 15:00
Bot: [AI creates order using create_order]
     ✅ Заказ #123 создан! Общая сумма: 12000 тенге
```

### Track Orders
```
User: Где мой заказ?
Bot: Укажите номер телефона
User: +77011234567
Bot: [AI uses track_order_by_phone]
     📦 Заказ #123 - В обработке
     📦 Заказ #118 - Доставлен (2025-09-28)
```

## File Structure

```
telegram-bot/
├── bot.py                 # Main bot logic (commands, handlers)
├── ai_handler.py          # Claude AI integration (function calling)
├── mcp_client.py          # MCP HTTP client (tool execution)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── railway.json          # Railway deployment config
├── start-railway.sh      # Railway startup script
└── README.md             # This file
```

## Available MCP Tools

The bot can use these tools via Claude AI function calling:

### Product Tools
- `list_products` - Search/filter products by name, type, price
- `get_product` - Get detailed product info by ID

### Order Tools
- `create_order` - Create new order with delivery details
- `track_order_by_phone` - Track orders by customer phone

### Shop Tools
- `get_shop_settings` - Get shop configuration
- `get_working_hours` - Get weekly schedule

## AI Conversation Flow

1. **User sends message** → Telegram bot receives
2. **Bot → AI Handler** → Passes message to Claude
3. **Claude analyzes** → Determines if tools needed
4. **AI → MCP Client** → Calls required tools
5. **MCP Client → MCP Server** → HTTP request to tool
6. **MCP Server → Backend API** → Fetches data
7. **Backend → MCP → AI** → Tool results returned
8. **AI generates response** → Natural language answer
9. **Bot → User** → Sends formatted reply

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TELEGRAM_TOKEN` | ✅ | Bot token from @BotFather | `1234567890:ABCdef...` |
| `CLAUDE_API_KEY` | ✅ | Anthropic API key | `sk-ant-api03-...` |
| `BACKEND_API_URL` | ✅ | Backend API URL (critical for auth) | `http://localhost:8014/api/v1` (local) or `https://figma-product-catalog-production.up.railway.app/api/v1` (prod) |
| `MCP_SERVER_URL` | ✅ | MCP server HTTP URL | `http://localhost:8000` (local) or `https://mcp.railway.app` (prod) |
| `AI_AGENT_URL` | ✅ | AI Agent Service URL | `http://localhost:8000` (local) or `https://ai-agent.railway.app` (prod) |
| `DEFAULT_SHOP_ID` | ✅ | Default shop ID | `8` |
| `CLAUDE_MODEL` | ❌ | Claude model to use | `claude-sonnet-4-20250514` |
| `WEBHOOK_URL` | ❌ | Webhook URL (Railway only) | `https://telegram-bot-production.up.railway.app` |
| `WEBHOOK_PORT` | ❌ | Webhook port (Railway only) | `8080` |
| `LOG_LEVEL` | ❌ | Logging level | `INFO` (DEBUG, INFO, WARNING, ERROR) |

## Troubleshooting

### Bot doesn't respond
1. Check `TELEGRAM_TOKEN` is valid
2. Verify MCP server is running: `curl $MCP_SERVER_URL/health`
3. Check logs: `railway logs` (production) or console output (local)

### AI calls wrong functions
1. Check `MCP_SERVER_URL` points to correct server
2. Verify `DEFAULT_SHOP_ID` is correct
3. Review AI system prompt in `ai_handler.py`

### Webhook errors (Railway)
1. Ensure `WEBHOOK_URL` matches Railway domain
2. Check Railway logs: `railway logs --deploy`
3. Verify Railway port is `8080` (default)

### MCP connection fails
1. Test MCP server: `curl -X POST $MCP_SERVER_URL/call-tool -H "Content-Type: application/json" -d '{"name": "get_shop_settings", "arguments": {"shop_id": 8}}'`
2. Check MCP server logs
3. Verify firewall/network settings

## Development Tips

### Testing AI Responses
Use `/clear` command to reset conversation history between tests.

### Debugging Function Calls
Add logging in `ai_handler.py`:
```python
logger.info(f"Tool call: {tool_name} with {tool_input}")
logger.info(f"Tool result: {tool_result}")
```

### Local vs Production
- **Local**: Polling mode, `MCP_SERVER_URL=http://localhost:8000`
- **Production**: Webhook mode, `MCP_SERVER_URL=https://...railway.app`

## Security Notes

⚠️ **Important**:
- Never commit `.env` file (in `.gitignore`)
- Rotate `TELEGRAM_TOKEN` if exposed
- Protect `CLAUDE_API_KEY` (costs money!)
- MCP server only exposes **public** endpoints (no admin tools)

## Next Steps

1. **Get credentials**: Telegram token, Claude API key
2. **Deploy MCP server**: See `/mcp-server/README.md`
3. **Test locally**: Run bot in polling mode
4. **Deploy to Railway**: Auto-deploy from GitHub
5. **Monitor usage**: Track Claude API costs, bot metrics

## Support

For issues or questions:
- MCP Server: See `/mcp-server/README.md`
- Backend API: See `/backend/README.md`
- Project: Check main repository CLAUDE.md
