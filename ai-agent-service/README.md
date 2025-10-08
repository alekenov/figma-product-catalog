# AI Agent Service

Universal AI agent for omnichannel customer service in the Flower Shop application.

## Features

- 🤖 **Claude Sonnet 4.5** - Advanced AI for natural language understanding
- 🌐 **Multi-channel support** - Telegram, WhatsApp, Web, Instagram
- 💬 **Conversation history** - Context-aware multi-turn dialogues
- 🔧 **Function calling** - Automatic tool execution via MCP Server
- 🎨 **Channel-specific prompts** - Different tone for each channel

## Architecture

```
┌─────────────────┐
│  Telegram Bot   │─┐
│  WhatsApp Bot   │─┤
│  Web Widget     │─┼───▶ AI Agent Service ───▶ MCP Server ───▶ Backend API
│  Instagram Bot  │─┘
└─────────────────┘
```

## API Endpoints

### POST /chat
Universal chat endpoint for all channels.

**Request:**
```json
{
  "message": "покажи букеты",
  "user_id": "123456789",
  "channel": "telegram",
  "context": {"username": "johndoe"}
}
```

**Response:**
```json
{
  "text": "Вот наши букеты...",
  "tracking_id": "903757396",
  "order_number": "#12357"
}
```

### POST /clear-history/{user_id}
Clear conversation history.

### GET /products/{user_id}
Get last fetched products for a user.

### GET /health
Health check endpoint.

## Setup

### Local Development

1. **Install dependencies:**
```bash
cd ai-agent-service
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run server:**
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

4. **Test API:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "покажи букеты",
    "user_id": "test123",
    "channel": "telegram"
  }'
```

### Railway Deployment

1. **Create new service:**
```bash
railway link
railway up --ci
```

2. **Set environment variables in Railway:**
```
CLAUDE_API_KEY=sk-ant-...
MCP_SERVER_URL=https://mcp-server.railway.app
DEFAULT_SHOP_ID=8
```

3. **Deploy:**
```bash
git push
# Railway auto-deploys on push
```

## Channel Configuration

Each channel has a customized system prompt:

- **Telegram**: Friendly, uses emojis ✅
- **WhatsApp**: Professional, no emojis
- **Instagram**: Youth style, energetic
- **Web**: Structured, consultant tone

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `CLAUDE_API_KEY` | ✅ | Anthropic API key | - |
| `MCP_SERVER_URL` | ✅ | MCP Server URL | http://localhost:8000 |
| `DEFAULT_SHOP_ID` | ❌ | Shop ID for multi-tenancy | 8 |
| `PORT` | ❌ | HTTP server port | 8000 |

## Adding New Channels

To add a new channel (e.g., Kaspi):

1. **Create adapter** (50 lines of code):
```python
# channel-adapters/kaspi/bot.py
async def handle_message(user_id, message):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": message,
                "user_id": user_id,
                "channel": "kaspi"
            }
        )
        return response.json()
```

2. **Add channel prompt** in `agent.py`:
```python
elif channel == "kaspi":
    return base + "\n\nСтиль: Краткие ответы для Kaspi Shop."
```

3. **Deploy adapter** - done!

## Monitoring

**Logs:**
```bash
railway logs --service ai-agent-service
```

**Metrics:**
- Request count: `/metrics` endpoint (todo)
- AI token usage: Check Anthropic dashboard
- Error rate: Railway metrics

## Testing

**Test chat endpoint:**
```bash
pytest tests/test_agent.py
```

**Test specific channel:**
```python
import httpx

async def test_telegram():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json={
                "message": "покажи букеты",
                "user_id": "test123",
                "channel": "telegram"
            }
        )
        print(response.json())
```

## License

MIT
