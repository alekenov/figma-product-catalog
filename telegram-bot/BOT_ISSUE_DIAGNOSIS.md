# Telegram Bot Issue Diagnosis - 2025-10-13

## Problem Summary

Production bot `@cvetykzsupportbot` is experiencing conflicts with error:
```
telegram.error.Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

## Findings

### Bot Configuration

**Production Bot** (`@cvetykzsupportbot`):
- Token: `8035864354:AAHch7_0sT--M0xunghsWbyNS3pn_nKASVQ`
- Username: `@cvetykzsupportbot`
- ID: `8035864354`
- Webhook: `https://telegram-bot-production-75a7.up.railway.app/webhook` ✅ SET
- Webhook Status: **ACTIVE** (pending_update_count: 0)
- Webhook IP: `66.33.22.76`

**Test Bot** (local):
- Token: `5261424288:AAEDEY3pfLVIHIkFJnRtLGM_qLNjJcbbjrs`
- Username: `@Dflowersbot`
- Mode: Polling (webhook NOT set) ✅

### Railway Service Status

**Webhook URL**: `https://telegram-bot-production-75a7.up.railway.app/webhook`
- Returns: **405 Method Not Allowed** (correct - GET not supported, only POST)
- Health endpoint: **404 Not Found** ❌

**Critical Issue**: Railway service is NOT responding correctly. The bot application is either:
1. Not running on Railway
2. Crashed during startup
3. Running but not listening on correct port

### Local Environment

- ✅ No bot processes running locally (`ps aux` check)
- ✅ No conflicts in local `.env` (uses test bot token)
- ✅ No old bot instances in cvety-local running

### Root Cause

**Conflict Error (409)** when attempting `getUpdates` is caused by:
1. Webhook is properly set on Telegram API side
2. BUT the Railway service is not running/responding
3. When webhook fails, some process may be attempting fallback to polling mode
4. This creates a conflict since webhook is still registered

## Solution Plan

### Immediate Actions

1. **Check Railway Deployment Status**
   ```bash
   railway logs --service telegram-bot
   ```

2. **Check Railway Environment Variables**
   Ensure these are set on Railway:
   - `TELEGRAM_TOKEN` = `8035864354:AAHch7_0sT--M0xunghsWbyNS3pn_nKASVQ`
   - `WEBHOOK_URL` = `https://telegram-bot-production-75a7.up.railway.app`
   - `WEBHOOK_PORT` = `8080` (or Railway $PORT)
   - `AI_AGENT_URL` = `https://ai-agent-production.up.railway.app` (or correct URL)
   - `MCP_SERVER_URL` = `https://mcp-server-production.up.railway.app` (or correct URL)
   - `DEFAULT_SHOP_ID` = `8`

3. **Redeploy Bot on Railway**
   ```bash
   cd telegram-bot
   railway up --ci
   ```

4. **If Redeployment Fails, Clear Webhook and Reset**
   ```bash
   # Run locally to clear webhook
   python clear_webhook.py

   # Then redeploy with proper env vars
   railway up --ci
   ```

### Verification Steps

After redeployment:

1. **Check Health Endpoint**
   ```bash
   curl https://telegram-bot-production-75a7.up.railway.app/health
   # Should return 200 OK (if health endpoint exists)
   # OR return proper response (not 404)
   ```

2. **Test Webhook**
   ```bash
   curl -X POST https://api.telegram.org/bot8035864354:AAHch7_0sT--M0xunghsWbyNS3pn_nKASVQ/getWebhookInfo
   # Should show URL: https://telegram-bot-production-75a7.up.railway.app/webhook
   # pending_update_count should be 0
   ```

3. **Test Bot in Telegram**
   - Send `/start` to `@cvetykzsupportbot`
   - Should receive welcome message
   - No conflict errors in logs

### Long-term Prevention

1. **Add Health Check Endpoint**
   Add to `bot.py`:
   ```python
   from aiohttp import web

   async def health_check(request):
       return web.Response(text="OK")

   # In run_webhook():
   app.web_app = web.Application()
   app.web_app.router.add_get('/health', health_check)
   ```

2. **Railway Configuration**
   - Ensure `railway.json` has correct `startCommand`
   - Set restart policy to handle crashes
   - Monitor Railway metrics for service health

3. **Monitoring**
   - Set up alerts for webhook failures
   - Log all bot errors to Railway logs
   - Monitor Telegram API error rate

## Next Steps

1. ✅ Check Railway logs for crash/error details
2. ⏳ Verify environment variables on Railway
3. ⏳ Redeploy bot service
4. ⏳ Test bot functionality
5. ⏳ Add health check endpoint if missing

## Files to Check

- `/telegram-bot/bot.py` - Main bot code (bot.py:514-520)
- `/telegram-bot/start-railway.sh` - Railway startup script
- `/telegram-bot/railway.json` - Railway deployment config
- `/telegram-bot/.env` - Local environment (NOT used on Railway)

## Railway Service Name

Based on diagnostic checks, the Railway service should be named:
- `telegram-bot` or `telegram-bot-production`

Use `railway service` to list all services and identify the correct one.
