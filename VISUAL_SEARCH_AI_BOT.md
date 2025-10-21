# Visual Search AI Bot - Documentation

## Overview

Visual Search AI Bot is an AI-powered Telegram bot for shop_id=17008 that provides:
- 🔍 Visual product search (AI-powered image recognition)
- 💬 Natural language ordering via Claude Haiku 4.5
- 📦 Full MCP tools integration (40+ tools)
- 💳 Kaspi Pay integration
- 📊 Order tracking and management

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Visual Search AI Bot                      │
│                   (shop_id=17008)                           │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │ Telegram   │  │ MCP Client │  │ Formatters         │  │
│  │ Handlers   │  │ (shared)   │  │ (shared)           │  │
│  └────────────┘  └────────────┘  └────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
┌────────────┐  ┌─────────────┐  ┌────────────┐
│ AI Agent   │  │ Backend API │  │ MCP Server │
│ Service    │  │ (FastAPI)   │  │ (FastMCP)  │
│ :8002      │  │ :8014       │  │ :8000      │
│            │  │             │  │            │
│ Claude     │  │ Products    │  │ 40+ Tools  │
│ Haiku 4.5  │  │ Orders      │  │ (auth,     │
│ + Caching  │  │ Users       │  │ products,  │
│            │  │ PostgreSQL  │  │ orders,    │
└────────────┘  └─────────────┘  │ payments)  │
                                 └────────────┘
```

## Key Features

### 1. AI-Powered Conversation
- **Claude Haiku 4.5** with prompt caching (80-90% token savings)
- **Natural language understanding** for product search and ordering
- **Conversation history** maintained per user
- **Multi-turn dialogues** for order refinement

### 2. Visual Product Search
- **CLIP embeddings** for image similarity
- **Auto-trigger** on photo upload
- **Safety net architecture**: Pre-searches before Claude for 100% reliability
- **Top-5 results** with similarity scores

### 3. MCP Tools Integration
The bot has access to 40+ tools via MCP server:

**Authentication:**
- `login` - User authentication
- `get_current_user` - Get user profile

**Products:**
- `list_products` - Search with filters (price, type, etc.)
- `get_product` - Product details
- `search_similar_bouquets` - Visual search
- `check_product_availability` - Stock check
- `get_bestsellers` - Popular products
- `get_featured_products` - Curated picks

**Orders:**
- `create_order` - Place new order (AI-powered)
- `track_order` - Track by tracking_id
- `track_order_by_phone` - Customer's orders
- `update_order_status` - Admin only
- `cancel_order` - Cancel order
- `preview_order_cost` - Calculate total

**Payments (Kaspi Pay):**
- `kaspi_create_payment` - Request payment
- `kaspi_check_payment_status` - Check status
- `kaspi_refund_payment` - Process refund

**Shop Settings:**
- `get_shop_settings` - Shop info
- `get_working_hours` - Schedule
- `get_faq` - Frequently asked questions
- `get_reviews` - Customer reviews

### 4. Multi-Tenancy
- **shop_id=17008** (vs shop_id=8 for main bot)
- **Isolated data** in database
- **Separate Telegram bot token**
- **Shared infrastructure** (AI Agent, MCP, Backend)

## Comparison: Visual Search AI Bot vs Main Telegram Bot

| Feature | Visual Search AI Bot | Main Telegram Bot |
|---------|---------------------|-------------------|
| **Shop ID** | 17008 | 8 |
| **Deployment** | Local (polling) | Railway (webhook + polling) |
| **Location** | `/visual_search_ai_bot.py` | `/telegram-bot/bot.py` |
| **Configuration** | `.env.visual_search` | `.env` |
| **Startup Script** | `./start_visual_ai_bot.sh` | `./telegram-bot/start.sh` |
| **AI Integration** | ✅ Claude Haiku 4.5 + MCP | ✅ Claude Haiku 4.5 + MCP |
| **Visual Search** | ✅ Full support | ✅ Full support |
| **Order Creation** | ✅ Via MCP tools | ✅ Via MCP tools |
| **Webhook Mode** | ❌ Not supported | ✅ Railway production |
| **Auto-deploy** | ❌ Manual start | ✅ GitHub push → Railway |
| **Health Endpoint** | ❌ Not needed locally | ✅ `/health` for Railway |
| **Code Reuse** | ✅ Shares MCP client, formatters, logging | Original implementation |

## File Structure

```
figma-product-catalog/
├── visual_search_ai_bot.py          # Main bot file (shop_id=17008)
├── .env.visual_search               # Configuration
├── start_visual_ai_bot.sh           # Startup script
├── VISUAL_SEARCH_AI_BOT.md          # This file
│
├── telegram-bot/                    # Shared modules (imported via sys.path)
│   ├── mcp_client.py               # MCP client (authorization)
│   ├── formatters.py               # Product image formatting
│   └── logging_config.py           # Structured logging
│
├── ai-agent-service/                # AI service (shared)
│   └── main.py                     # FastAPI server on :8002
│
├── mcp-server/                      # MCP tools (shared)
│   └── server.py                   # FastMCP server on :8000
│
└── backend/                         # Backend API (shared)
    └── main.py                     # FastAPI server on :8014
```

## Setup Instructions

### Prerequisites

1. **Backend API** running on port 8014:
   ```bash
   cd backend
   python3 main.py
   ```

2. **AI Agent Service** running on port 8002:
   ```bash
   cd ai-agent-service
   python3 main.py
   ```

3. **MCP Server** (optional, for advanced features) on port 8000:
   ```bash
   cd mcp-server
   ./start.sh
   ```

### Configuration

1. **Create Telegram Bot:**
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram
   - Create new bot: `/newbot`
   - Save the token

2. **Configure Environment:**
   ```bash
   cp .env.visual_search .env.visual_search.local
   nano .env.visual_search.local
   ```

   Set your values:
   ```bash
   TELEGRAM_TOKEN=your_actual_bot_token_here
   DEFAULT_SHOP_ID=17008
   AI_AGENT_URL=http://localhost:8002
   BACKEND_API_URL=http://localhost:8014/api/v1
   MCP_SERVER_URL=http://localhost:8000
   LOG_LEVEL=INFO
   ```

3. **Install Dependencies:**
   ```bash
   pip3 install -r telegram-bot/requirements.txt
   ```

### Running the Bot

**Quick Start:**
```bash
./start_visual_ai_bot.sh
```

**Manual Start:**
```bash
python3 visual_search_ai_bot.py
```

**Expected Output:**
```
🌸 Visual Search AI Bot - Starting...
📍 Shop ID: 17008
🤖 AI Agent: http://localhost:8002
🔧 MCP Server: http://localhost:8000

2025-01-21 16:42:00 - INFO - visual_search_ai_bot_starting shop_id=17008
2025-01-21 16:42:00 - INFO - bot_configuration shop_id=17008
2025-01-21 16:42:01 - INFO - bot_initialized_successfully shop_id=17008
2025-01-21 16:42:01 - INFO - starting_visual_search_ai_bot_polling_mode shop_id=17008
```

## Testing Scenarios

### 1. Authorization Flow
1. Open Telegram and find your bot
2. Send `/start`
3. Bot requests contact: "📱 Поделиться контактом"
4. Share contact → Registration in shop_id=17008
5. Confirmation: "✅ Спасибо, [Name]! Вы успешно авторизованы."

### 2. Visual Search (Photo)
1. Send a photo of a bouquet
2. Bot shows typing indicator
3. AI analyzes image → calls `search_similar_bouquets` tool
4. Response with similar products:
   ```
   🔍 Нашел похожие букеты:

   1. Букет "Розовая мечта" - 18,500₸
   2. Букет "Нежность" - 15,000₸
   ...
   ```

### 3. Natural Language Search
**Example 1: Price filter**
```
User: Покажи букеты до 15000 тенге
Bot:  [Calls list_products with max_price=1500000 kopecks]
      📦 Вот букеты до 15,000₸:
      [Shows 5 products with photos]
```

**Example 2: Type filter**
```
User: Хочу купить розы
Bot:  [Calls list_products with product_type="bouquet", search="розы"]
      🌹 Букеты с розами:
      [Shows matching products]
```

### 4. Order Creation
```
User: Хочу заказать букет номер 123 с доставкой на завтра к 15:00
Bot:  [AI analyzes request]
      [Calls create_order with parsed data]
      ✅ Заказ #ABC123 создан!

      📦 Детали:
      - Товар: Букет "Розовая мечта"
      - Доставка: 2025-01-22, 15:00
      - Адрес: [будет запрошен]
      - Стоимость: 20,500₸
```

### 5. Order Tracking
```
User: Где мой заказ ABC123?
Bot:  [Calls track_order tool]
      📦 Заказ #ABC123
      Статус: В доставке 🚚
      Ожидаемое время: 15:00
```

## Troubleshooting

### Bot Not Starting

**Error: "TELEGRAM_TOKEN not configured"**
```bash
# Check .env.visual_search file
cat .env.visual_search
# Ensure TELEGRAM_TOKEN is set correctly
```

**Error: "Failed to connect to AI Agent Service"**
```bash
# Check if AI Agent Service is running
curl http://localhost:8002/health

# If not running:
cd ai-agent-service
python3 main.py
```

**Error: "Backend API not responding"**
```bash
# Check backend
curl http://localhost:8014/api/v1/health

# If not running:
cd backend
python3 main.py
```

### Authorization Issues

**User not authorized after sharing contact:**
```bash
# Check backend logs
cd backend && tail -f *.log

# Check if telegram_client was created
# Database query (if needed):
# SELECT * FROM telegram_client WHERE shop_id = 17008;
```

### Visual Search Not Working

**Photo uploaded but no results:**
1. Check AI Agent logs: `cd ai-agent-service && tail -f *.log`
2. Verify visual search endpoint: `curl http://localhost:8014/api/v1/products/search/similar`
3. Check if products have embeddings: `curl http://localhost:8014/api/v1/products/search/stats?shop_id=17008`

## Architecture Insights

`★ Insight ─────────────────────────────────────`
**Code Reuse Strategy:**
1. **Shared Modules via sys.path**: Instead of copying files, we add `telegram-bot/` to Python path and import directly
2. **MCP Client Isolation**: Authorization checks happen via backend API, MCP server is optional
3. **AI Agent as Universal Service**: Same service handles both bots (shop_id differentiation)

**Multi-Tenancy Pattern:**
- Database: `WHERE shop_id = ?` on all queries
- JWT tokens: Include shop_id claim
- MCP tools: Auto-filter by shop_id from token
- No data leakage between shops

**Prompt Caching Benefits:**
- First request: ~2500 tokens (policies + instructions)
- Cached requests: ~250 tokens (only new message)
- **90% token reduction** = **90% cost reduction**
- Cache refresh: Every 1 hour automatically
`─────────────────────────────────────────────────`

## Production Deployment (Future)

When ready for production:

1. **Deploy to Railway:**
   - Add `railway.json` to root
   - Enable webhook mode (add `WEBHOOK_URL` env var)
   - Set production `TELEGRAM_TOKEN`

2. **Environment Variables:**
   ```bash
   TELEGRAM_TOKEN=<production_token>
   DEFAULT_SHOP_ID=17008
   AI_AGENT_URL=https://ai-agent-production.up.railway.app
   BACKEND_API_URL=https://backend-production.up.railway.app/api/v1
   WEBHOOK_URL=https://visual-search-bot-production.up.railway.app
   WEBHOOK_PORT=8080
   ```

3. **Health Endpoint:**
   - Uncomment webhook code in `visual_search_ai_bot.py`
   - Test: `curl https://your-bot.up.railway.app/health`

## Support

For issues or questions:
1. Check logs: `tail -f telegram-bot/logs/*.log`
2. Review structured logs for request tracing
3. Test MCP tools directly: `cd mcp-server && python -m fastmcp dev server.py`
4. Consult main bot documentation: `telegram-bot/README.md`

---

**Last Updated:** 2025-01-21
**Version:** 1.0.0
**Status:** ✅ Ready for local testing
