# Visual Search AI Bot - Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### Step 1: Get Telegram Bot Token
1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. **Save the token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Bot
```bash
cd /Users/alekenov/figma-product-catalog

# Edit configuration file
nano .env.visual_search
```

**Replace this line:**
```bash
TELEGRAM_TOKEN=your_visual_search_bot_token_here
```

**With your actual token:**
```bash
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 3: Start Required Services

**Terminal 1 - Backend API:**
```bash
cd backend
python3 main.py
```
Wait for: `✅ Application startup complete`

**Terminal 2 - AI Agent Service:**
```bash
cd ai-agent-service
python3 main.py
```
Wait for: `✅ All services initialized successfully!`

**Terminal 3 - Visual Search AI Bot:**
```bash
./start_visual_ai_bot.sh
```

**Expected output:**
```
🌸 Visual Search AI Bot - Startup Script
========================================

✅ Configuration loaded from .env.visual_search
   Shop ID: 17008
   AI Agent: http://localhost:8002
   MCP Server: http://localhost:8000

✅ Service checks complete
✅ Python dependencies OK

🚀 Starting Visual Search AI Bot...
   Press Ctrl+C to stop

2025-01-21 17:15:00 - INFO - visual_search_ai_bot_starting shop_id=17008
2025-01-21 17:15:01 - INFO - bot_initialized_successfully shop_id=17008
```

## ✅ Test the Bot

### Test 1: Authorization
1. Open Telegram and find your bot
2. Send: `/start`
3. Click "📱 Поделиться контактом"
4. Confirm contact sharing
5. ✅ Should receive: "Спасибо, [Name]! Вы успешно авторизованы."

### Test 2: Text Query
Send message:
```
Покажи букеты до 15000 тенге
```

Expected response:
- AI processes request
- Calls `list_products` tool with price filter
- Shows matching products with photos

### Test 3: Visual Search
1. Find a bouquet photo online or take a picture
2. Send photo to bot
3. Expected response:
   - "🔍 Нашел похожие букеты:"
   - Shows top 5 similar products

### Test 4: Order Creation
Send message:
```
Хочу заказать букет номер 5 с доставкой на завтра
```

Expected response:
- AI parses request
- Creates order via `create_order` tool
- Returns order confirmation with tracking ID

## 🛠️ Troubleshooting

### Bot doesn't start

**Error: "TELEGRAM_TOKEN not configured"**
```bash
# Check if token is set
cat .env.visual_search | grep TELEGRAM_TOKEN

# Should show your actual token, not "your_visual_search_bot_token_here"
```

**Error: "Backend API not running"**
```bash
# Test backend
curl http://localhost:8014/api/v1/health

# Should return: {"status":"healthy"}
```

**Error: "AI Agent Service not running"**
```bash
# Test AI Agent
curl http://localhost:8002/health

# Should return: {"status":"healthy", ...}
```

### Bot starts but doesn't respond

**Check logs:**
```bash
# In bot terminal, look for errors
# Common issues:
# - Authorization failed → Check backend connection
# - Empty AI response → Check AI Agent Service logs
# - Tool execution failed → Check MCP server logs
```

**Verify services are running:**
```bash
# Should see 3 processes:
ps aux | grep -E "(main.py|visual_search_ai_bot)"

# Should show:
# - python3 backend/main.py
# - python3 ai-agent-service/main.py
# - python3 visual_search_ai_bot.py
```

## 📊 Architecture Diagram

```
┌─────────────────────────────────┐
│    You (Telegram User)          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Visual Search AI Bot           │
│  (shop_id=17008)                │
│  Port: N/A (polling mode)       │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌─────────┐   ┌──────────────┐
│ AI Agent│   │ Backend API  │
│ :8002   │   │ :8014        │
└─────────┘   └──────────────┘
      │             │
      └──────┬──────┘
             ▼
      ┌──────────────┐
      │ PostgreSQL   │
      │ (Railway)    │
      └──────────────┘
```

## 🎯 Next Steps

1. **Test all features** (authorization, search, visual search, orders)
2. **Review logs** to understand AI tool execution
3. **Experiment with queries** to test AI understanding
4. **Read full docs**: `VISUAL_SEARCH_AI_BOT.md`

## 🆘 Need Help?

- **Full documentation**: `VISUAL_SEARCH_AI_BOT.md`
- **Main bot docs**: `telegram-bot/README.md`
- **MCP tools**: `mcp-server/README.md`
- **AI Agent docs**: `ai-agent-service/README.md`

---

**Ready to go! 🎉**

Your Visual Search AI Bot is now configured and ready to use.
Try sending a photo of a bouquet to see the magic happen! ✨
