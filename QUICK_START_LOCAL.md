# 🚀 Quick Start - Local Testing

## ✅ Current Status

- ✅ Backend: http://localhost:8014 (RUNNING)
- ⏳ MCP Server: http://localhost:8000 (need to start)
- ⏳ AI Agent: http://localhost:8002 (need to start)
- ⏳ Telegram Bot: polling mode (need to start)

---

## 📋 COPY-PASTE COMMANDS (Open 3 New Terminals)

### Terminal 1: MCP Server

```bash
cd /Users/alekenov/figma-product-catalog/mcp-server
./start.sh
```

**Expected output:**
```
Server running on http://0.0.0.0:8000
Listening for requests...
```

---

### Terminal 2: AI Agent Service V2

```bash
cd /Users/alekenov/figma-product-catalog/ai-agent-service
python3 main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8002
INFO:     Application startup complete
```

---

### Terminal 3: Telegram Bot

```bash
cd /Users/alekenov/figma-product-catalog/telegram-bot
python3 bot.py
```

**Expected output:**
```
[INFO] Bot started in polling mode
[INFO] Waiting for messages...
```

---

## ✅ Verify All Services Running

Run these in a NEW terminal to check:

```bash
# Backend
curl http://localhost:8014/health

# MCP Server
curl http://localhost:8000/health

# AI Agent
curl http://localhost:8002/health

# Should all return: {"status": "ok"} or similar
```

---

## 🧪 TEST THE BOT - 3 OPTIONS

### Option 1: Quick Test (Automated)

```bash
cd /Users/alekenov/figma-product-catalog/telegram-bot
pytest tests/ -v
python test_scenarios.py
```

---

### Option 2: Test via API (curl)

**New user authorization:**
```bash
curl -X POST http://localhost:8002/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Привет, я хочу заказать розы",
    "user_id": "test_user_123",
    "channel": "telegram"
  }'
```

**Expected response:**
```json
{
  "text": "Привет! Я помогу вам выбрать букет...",
  "show_products": true
}
```

---

### Option 3: Real Telegram Bot

1. Open Telegram: **Search @cvetykzsupportbot**
2. Send: `/start`
3. **Share your contact** (button will appear)
4. Bot should say: ✅ "Спасибо, вы авторизованы"
5. Try: `/catalog`, `/myorders`, or **type any message**

**Test commands:**
- `/start` - Welcome
- `/help` - Help
- `/catalog` - Show categories
- `/myorders` - Track orders
- `/clear` - Clear history
- Type anything to chat with AI

---

## 📊 What's Happening Behind The Scenes

```
Your Message
    ↓
Telegram Bot (polling mode)
    ↓
AI Agent Service (port 8002)
    ├─ Claude Sonnet 4.5 processes text
    ├─ Determines what user wants
    ├─ Calls MCP tools if needed
    ↓
MCP Server (port 8000)
    ├─ Authorization check
    ├─ Product search
    ├─ Order tracking
    ↓
Backend API (port 8014)
    ├─ Queries database
    ├─ Returns products/orders
    ↓
PostgreSQL Database
    └─ Stores all data

Response flows back through the same path
    ↓
Telegram Bot formats and sends to user
```

---

## 🔍 Monitor Logs in Real Time

### Terminal 1: Backend
```bash
# Watch backend logs
tail -f /tmp/backend.log  # if logging to file
# Or just look at terminal output
```

### Terminal 2: MCP Server
```
# You'll see connection logs like:
[INFO] Incoming request: GET /telegram/client
[INFO] Response: 200 OK
```

### Terminal 3: AI Agent
```
# You'll see logs like:
[INFO] Chat endpoint called
[INFO] User: test_user_123
[INFO] Model: claude-haiku-4-5-20251001
[INFO] Tokens used: 145 (input), 89 (output)
[INFO] Cache stats: hits=2, misses=1
```

### Terminal 4: Telegram Bot
```
# You'll see logs like:
[INFO] message_received: user_id=626599, text="Hello"
[INFO] authorization_check: user_id=626599, is_authorized=True
[INFO] message_handling_success: response_length=250
```

---

## 📈 Expected Flow Example

### User Types: "Мне нужны красные розы"

**Bot logs:**
```
[INFO] message_received: user_id=626599, text="Мне нужны красные розы"
[INFO] authorization_check: is_authorized=True (from cache)
[INFO] POST to AI Agent: /chat
```

**AI Agent logs:**
```
[INFO] Chat endpoint called
[INFO] User message: "Мне нужны красные розы"
[INFO] Calling MCP tool: list_products
[INFO] MCP response: 5 products found
[INFO] Generating response with Claude
[INFO] Response: "Вот красные розы..." (with show_products=True)
```

**Bot logs:**
```
[INFO] AI response received
[INFO] Fetching product images...
[INFO] Sending 5 products + text to user
[INFO] message_handling_success
```

---

## ⚡ Performance Metrics

**First message (cache miss):**
- Total time: ~2-3 seconds
- MCP call: ~100ms
- AI processing: ~1-2 seconds
- Bot response: ~500ms

**Second identical message (cache hit):**
- Total time: <100ms
- MCP call: ~5ms (cached)
- AI processing: ~50ms (prompt cache hit!)
- Bot response: <50ms

---

## 🛠️ Troubleshooting

### "Connection refused" on port 8002
```bash
# Check if AI Agent is running
lsof -i :8002

# If not, start it in Terminal 2
cd /Users/alekenov/figma-product-catalog/ai-agent-service
python3 main.py
```

### "Port already in use"
```bash
# Kill the process using that port
lsof -ti:8002 | xargs kill -9

# Then restart
python3 main.py
```

### Bot shows "authorization_check_failed"
```bash
# 1. Verify MCP Server is running
curl http://localhost:8000/health

# 2. Check environment variables in bot
cd telegram-bot
python3 -c "import os; print(os.getenv('MCP_SERVER_URL'))"
# Should output: http://localhost:8000
```

### "No module named 'anthropic'" in AI Agent
```bash
# Install dependencies
cd /Users/alekenov/figma-product-catalog/ai-agent-service
pip install -r requirements.txt
```

---

## 📝 Environment Variables Check

**AI Agent needs:**
```bash
echo $CLAUDE_API_KEY        # Should show sk-ant-...
echo $MCP_SERVER_URL        # Should show http://localhost:8000
echo $BACKEND_API_URL       # Should show http://localhost:8014/api/v1
```

**Telegram Bot needs:**
```bash
echo $TELEGRAM_TOKEN        # Should show bot token
echo $AI_AGENT_URL          # Should show http://localhost:8002
echo $MCP_SERVER_URL        # Should show http://localhost:8000
```

---

## 🎯 Testing Checklist

- [ ] Backend running on 8014 (curl works)
- [ ] MCP Server running on 8000 (curl works)
- [ ] AI Agent running on 8002 (curl works)
- [ ] Telegram Bot polling mode active (logs show "waiting for messages")
- [ ] Automated tests pass: `pytest tests/ -v`
- [ ] Scenarios pass: `python test_scenarios.py`
- [ ] Bot responds to `/start` command
- [ ] Bot accepts contact sharing
- [ ] Bot recognizes authorized user
- [ ] `/myorders` shows order tracking
- [ ] Regular messages processed by AI Agent

---

## 🚀 Ready to Deploy?

Once everything works locally:

```bash
# Run full test suite
cd /Users/alekenov/figma-product-catalog/telegram-bot
pytest tests/ -v && python test_scenarios.py

# If all green, ready for Railway deployment!
git add .
git commit -m "feat: Add local testing setup"
git push origin main
# Railway auto-deploys!
```

---

**Status**: ✅ Ready to test locally!

Questions? Check:
- `/Users/alekenov/figma-product-catalog/README_TESTING.md` - Testing guide
- `/Users/alekenov/figma-product-catalog/telegram-bot/README.md` - Bot setup
- `/Users/alekenov/figma-product-catalog/ai-agent-service/README.md` - AI Agent docs
