# AI Agent Service - Deployment Guide

## ✅ Migration Complete

The AI Agent Service has been successfully created and tested. The new omnichannel architecture allows connecting multiple channels (Telegram, WhatsApp, Web, Instagram) to a centralized AI agent.

## Architecture

```
┌─────────────┐
│ Telegram    │─┐
│ (adapter)   │ │
└─────────────┘ │
                ├─────▶ AI Agent Service ───▶ MCP Server ───▶ Backend API
┌─────────────┐ │       [Claude Sonnet 4.5]      [Tools]      [PostgreSQL]
│ WhatsApp    │─┤       [Conversation history]
│ (adapter)   │ │       [Multi-channel]
└─────────────┘ │
                │
┌─────────────┐ │
│ Web Widget  │─┘
│ (adapter)   │
└─────────────┘
```

## Local Testing

### 1. Start all services

```bash
# Terminal 1 - Backend API (if not running)
cd backend
python main.py
# → http://localhost:8014

# Terminal 2 - MCP Server
cd mcp-server
PORT=8001 .venv/bin/python http_server.py
# → http://localhost:8001

# Terminal 3 - AI Agent Service
cd ai-agent-service
python3 main.py
# → http://localhost:8000

# Terminal 4 - Telegram Bot (OPTIONAL - conflicts with Railway production)
# NOTE: Stop Railway telegram-bot service first!
cd telegram-bot
python3 bot.py
```

### 2. Test via HTTP API

```bash
# Test simple query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"покажи букеты","user_id":"test123","channel":"telegram"}'

# Check health
curl http://localhost:8000/health

# Clear conversation history
curl -X POST http://localhost:8000/clear-history/test123?channel=telegram
```

### 3. Verified Flow

✅ User request → AI Agent Service (port 8000)
✅ Claude Sonnet 4.5 processes message
✅ AI calls MCP Server tools (port 8001)
✅ MCP Server fetches data from Backend API (port 8014)
✅ AI formats response with product catalog
✅ Response returned to user

**Test Result:** Successfully retrieved 12 bouquets with prices and descriptions in Russian.

## Railway Deployment

### Services to Deploy

1. **ai-agent-service** (NEW - needs deployment)
2. **telegram-bot** (UPDATE - already deployed, needs new env vars)
3. **mcp-server** (existing)
4. **backend** (existing)

### Step 1: Deploy AI Agent Service

```bash
cd ai-agent-service

# Link to Railway project
railway link

# Set environment variables (Railway dashboard or CLI)
railway variables set CLAUDE_API_KEY=sk-ant-api03-...
railway variables set MCP_SERVER_URL=https://mcp-server-production.up.railway.app
railway variables set DEFAULT_SHOP_ID=8

# Deploy with logs
railway up --ci
```

**Required Environment Variables:**
- `CLAUDE_API_KEY` - Anthropic API key
- `MCP_SERVER_URL` - URL of deployed MCP Server
- `DEFAULT_SHOP_ID` - Default shop ID (8 for cvety.kz)
- `PORT` - Auto-assigned by Railway

### Step 2: Update Telegram Bot

The Telegram bot is already deployed on Railway. Update its environment variable to point to the new AI Agent Service:

```bash
cd telegram-bot
railway link

# Update AI Agent URL
railway variables set AI_AGENT_URL=https://ai-agent-service-production.up.railway.app

# Redeploy (will auto-trigger on env var change)
```

**Updated Environment Variables:**
- `TELEGRAM_TOKEN` - Existing bot token
- `AI_AGENT_URL` - NEW: URL of AI Agent Service
- `MCP_SERVER_URL` - Can be removed (no longer needed)
- `CLAUDE_API_KEY` - Can be removed (moved to AI Agent)

### Step 3: Verify Deployment

```bash
# Check AI Agent Service
curl https://ai-agent-service-production.up.railway.app/health

# Check Telegram Bot (send message via Telegram app)
# Bot should respond using new architecture
```

## Local Development with Railway Production

**⚠️ Important:** The Telegram bot token can only be used by ONE instance at a time.

**Options:**

1. **Test via HTTP API** (recommended for development)
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"тест","user_id":"dev123","channel":"telegram"}'
   ```

2. **Test with Telegram** (requires stopping Railway bot)
   - Option A: Stop Railway telegram-bot service temporarily
   - Option B: Use a different bot token for local testing

## Adding New Channels

To add WhatsApp, Web, or Instagram:

1. **Create adapter** (50 lines of code):
   ```python
   # channel-adapters/whatsapp/bot.py
   async def handle_message(phone, message):
       async with httpx.AsyncClient() as client:
           response = await client.post(
               f"{AI_AGENT_URL}/chat",
               json={
                   "message": message,
                   "user_id": phone,
                   "channel": "whatsapp"
               }
           )
           return response.json()["text"]
   ```

2. **Deploy adapter** - That's it! The AI Agent Service handles everything else.

## Monitoring

### Logs

```bash
# AI Agent Service
railway logs -s ai-agent-service

# Telegram Bot
railway logs -s telegram-bot

# MCP Server
railway logs -s mcp-server
```

### Key Metrics

- Response time: ~15-20 seconds (Claude API + tool calls)
- Conversation history: Stored in memory per user/channel
- Token usage: ~1000-3000 tokens per request with tool use

## Troubleshooting

### Issue: Telegram bot conflict
**Symptom:** `Error: Conflict: terminated by other getUpdates request`
**Solution:** Only one bot instance can poll at a time. Stop Railway service or test via HTTP API.

### Issue: MCP Server 500 error
**Symptom:** `500 Internal Server Error` from MCP Server
**Solution:** Check MCP Server logs, ensure Backend API is accessible, verify tool arguments.

### Issue: Claude API timeout
**Symptom:** Requests taking >60 seconds
**Solution:** Increase httpx timeout in AI Agent Service, check Claude API status.

## Next Steps

- [ ] Deploy AI Agent Service to Railway
- [ ] Update Telegram Bot environment variables
- [ ] Test production deployment via Telegram
- [ ] Add WhatsApp channel (optional)
- [ ] Add Web chat widget (optional)
- [ ] Monitor Claude API usage and costs

## Files Modified

**Created:**
- `ai-agent-service/agent.py` (500 lines)
- `ai-agent-service/main.py` (260 lines)
- `ai-agent-service/requirements.txt`
- `ai-agent-service/.env.example`
- `ai-agent-service/railway.json`
- `ai-agent-service/README.md`
- `ai-agent-service/DEPLOYMENT.md` (this file)

**Modified:**
- `telegram-bot/bot.py` (~100 lines changed)
- `telegram-bot/requirements.txt` (removed anthropic dependency)

**Unchanged:**
- `mcp-server/` - all files unchanged
- `backend/` - all files unchanged
