# Cvety Bot - Railway Deployment Guide

## 🎯 Quick Start

### 1. Create Railway Service (via UI)

1. Open [Railway Dashboard](https://railway.app/project/positive-exploration)
2. Click **"+ New Service"**
3. Select **"GitHub Repo"** → `alekenov/figma-product-catalog`
4. Configure service:
   - **Service Name**: `cvety-bot`
   - **Root Directory**: `cvety-bot/`
   - Railway will auto-detect `railway.json`

### 2. Configure Environment Variables

After creating the service, link to it locally:

```bash
cd /Users/alekenov/figma-product-catalog/cvety-bot
railway service cvety-bot
```

Then set environment variables:

```bash
railway variables --set "TELEGRAM_TOKEN=<YOUR_BOT_TOKEN_FROM_BOTFATHER>"
railway variables --set "DEFAULT_SHOP_ID=17008"
railway variables --set "AI_AGENT_URL=https://ai-agent-service-production-c331.up.railway.app"
railway variables --set "MCP_SERVER_URL=https://mcp-server-production-00cd.up.railway.app"
railway variables --set "BACKEND_API_URL=https://figma-product-catalog-production.up.railway.app/api/v1"
railway variables --set "WEBHOOK_SECRET=<GENERATE_WITH_OPENSSL_RAND>"
railway variables --set "WEBHOOK_URL=<RAILWAY_PUBLIC_DOMAIN>"
railway variables --set "LOG_LEVEL=INFO"
```

**Generate WEBHOOK_SECRET:**
```bash
openssl rand -hex 32
```

### 3. Railway Auto-Deploy

Railway will automatically:
- Detect Python project from `requirements.txt`
- Use Nixpacks builder
- Run `python3 bot.py` (from `railway.json`)
- Assign public domain (e.g., `cvety-bot-production.up.railway.app`)
- Assign PORT environment variable

### 4. Configure Telegram Webhook

After deployment, get the public URL from Railway dashboard, then:

```bash
# Replace <RAILWAY_URL> with actual URL from Railway
curl -X POST "https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=https://<RAILWAY_URL>/webhook/<YOUR_WEBHOOK_SECRET>"
```

**Verify webhook:**

```bash
curl "https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

### 5. Monitor Deployment

```bash
# View deployment logs
railway logs --service cvety-bot

# Check service status
railway status --service cvety-bot
```

## 🔐 Security Notes

- ✅ TELEGRAM_TOKEN stored in Railway UI only (not in Git)
- ✅ WEBHOOK_SECRET protects webhook endpoint
- ✅ .gitignore prevents `.env` commits
- ✅ HTTPS required by Telegram for webhooks

## 📊 Environment Variables Reference

| Variable | Value | Source |
|----------|-------|--------|
| `TELEGRAM_TOKEN` | `5348517393:AAF...` | @BotFather |
| `DEFAULT_SHOP_ID` | `17008` | Production cvety.kz |
| `AI_AGENT_URL` | `https://ai-agent-service-...` | Railway service |
| `MCP_SERVER_URL` | `https://mcp-server-...` | Railway service |
| `BACKEND_API_URL` | `https://figma-product-catalog-...` | Railway service |
| `WEBHOOK_SECRET` | `7a80c46fa4ed4b1a...` | Generated via `openssl rand -hex 32` |
| `WEBHOOK_URL` | Auto-assigned | Railway sets `${{RAILWAY_PUBLIC_DOMAIN}}` |
| `PORT` | Auto-assigned | Railway provides |
| `LOG_LEVEL` | `INFO` | Manual config |

## 🛠️ Troubleshooting

### Webhook not receiving updates

1. Check webhook status:
```bash
curl "https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

2. Verify Railway service is running:
```bash
railway status --service cvety-bot
```

3. Check logs for errors:
```bash
railway logs --service cvety-bot
```

### Bot not responding

1. Check AI Agent Service health
2. Verify MCP Server is running
3. Check backend API: `https://figma-product-catalog-production.up.railway.app/health`

## 🔗 Related Services

- **Backend**: https://figma-product-catalog-production.up.railway.app
- **AI Agent**: https://ai-agent-service-production-c331.up.railway.app
- **MCP Server**: https://mcp-server-production-00cd.up.railway.app
- **Admin Bot**: `/admin-bot` (internal)

## 📝 Bot Info

- **Bot Username**: @cvetykzbot
- **Bot Token**: `<YOUR_TELEGRAM_BOT_TOKEN>`
- **Shop ID**: 17008 (cvety.kz production)
- **Database**: 185.125.90.141
