# Deployment Checklist for Flower Shop Bot

## Overview

This checklist helps prevent common deployment issues like token mismatches and corrupted conversation history. Follow these steps carefully before any production deployment.

---

## 🚨 Critical: Pre-Deployment Verification

### 1. Environment Variables Validation

#### Backend Service (`figma-product-catalog`)
```bash
# Verify these variables on Railway:
railway variables --service figma-product-catalog

Required:
✅ DATABASE_URL - Should reference ${{Postgres.DATABASE_URL}}
✅ SECRET_KEY - Production secret (not default)
✅ CORS_ORIGINS - Includes all frontend domains
✅ DEBUG - Set to "false" for production
```

#### AI Agent Service (`ai-agent`)
```bash
railway variables --service ai-agent

Required:
✅ CLAUDE_API_KEY - Valid Anthropic API key
✅ BACKEND_API_URL - Points to backend service (https://...)
✅ DATABASE_URL - Should reference ${{Postgres.DATABASE_URL}}
✅ DEFAULT_SHOP_ID - Correct shop ID (8 for cvety.kz)
✅ PORT - Railway auto-assigns, don't hardcode
```

#### Telegram Bot Service (`telegram-bot`)
```bash
railway variables --service telegram-bot

Required:
✅ TELEGRAM_TOKEN - **MUST MATCH webhook bot token**
✅ AI_AGENT_URL - Points to AI Agent service (https://...)
✅ WEBHOOK_URL - Telegram bot public URL (https://...)
✅ DEFAULT_SHOP_ID - Matches AI Agent (8 for cvety.kz)

CRITICAL: Verify token matches webhook:
1. Get webhook info: curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
2. Check webhook URL matches WEBHOOK_URL variable
3. If mismatch, update TELEGRAM_TOKEN immediately
```

### 2. Token Verification (Critical!)

**Problem**: Wrong token → bot doesn't respond to messages

**Solution**: Always cross-check token with webhook configuration

```bash
# Step 1: Get current webhook info
TELEGRAM_TOKEN="your-token-here"
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"

# Step 2: Verify webhook URL matches Railway service URL
# Expected: https://telegram-bot-production-XXXX.up.railway.app/webhook

# Step 3: If mismatch, find correct token
# Check with other tokens until you find the one with correct webhook

# Step 4: Update Railway variable
railway variables set TELEGRAM_TOKEN=correct-token-here

# Step 5: Redeploy
railway service telegram-bot
railway up --ci
```

### 3. Database Connection Verification

```bash
# Verify database is accessible from all services
railway run --service ai-agent env | grep DATABASE_URL
railway run --service figma-product-catalog env | grep DATABASE_URL

# Both should show: postgresql+asyncpg://... (for AI Agent)
# Backend uses: postgresql://... (auto-converted by SQLAlchemy)
```

---

## 🛠️ Deployment Steps

### Local Testing First

```bash
# 1. Start backend
cd backend && python main.py
# ✅ Should start on port 8014

# 2. Start AI Agent
cd ai-agent-service-v2 && python main.py
# ✅ Should initialize cache, connect to backend
# ✅ Check logs for "Cache refreshed: X products loaded"

# 3. Start Telegram Bot (polling mode)
cd telegram-bot && python bot.py
# ✅ Should connect to AI Agent
# ✅ Test with: /start command

# 4. Send test message
# ✅ "привет" → Should get response
# ✅ "какие цветы есть?" → Should list products
# ✅ "выстави счет на 100 тг" → Should ask for phone
```

### Deploy to Railway

```bash
# 1. Commit all changes
git add .
git commit -m "feat: Add graceful shutdown and auto-recovery"

# 2. Push to main (triggers auto-deploy)
git push origin main

# 3. Monitor deployment
railway logs --service telegram-bot
railway logs --service ai-agent

# 4. Wait for all services to be "Active"
railway status

# Expected output:
# telegram-bot: Active
# ai-agent: Active
# figma-product-catalog: Active
```

### Post-Deployment Validation

```bash
# 1. Check health endpoints
curl https://ai-agent-service-production-XXXX.up.railway.app/health
# ✅ Should return: {"status":"healthy",...}

curl https://telegram-bot-production-XXXX.up.railway.app/health
# ✅ Should return: {"status":"ok","service":"telegram-bot"}

# 2. Check webhook status
TELEGRAM_TOKEN="your-token"
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"
# ✅ pending_update_count should be 0
# ✅ last_error_date should be absent or old

# 3. Test bot manually
# Send message to @cvetykzsupportbot
# ✅ Should respond within 5 seconds
# ✅ Should handle product queries correctly
```

---

## 🚑 Troubleshooting Common Issues

### Issue 1: Bot Not Responding

**Symptoms**: Messages sent but no reply

**Diagnosis**:
```bash
# Check Railway logs for errors
railway logs --service telegram-bot | grep -i error

# Common causes:
1. Wrong TELEGRAM_TOKEN (doesn't match webhook)
2. AI Agent service is down
3. Database connection failed
```

**Fix**:
```bash
# Fix 1: Verify token
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"

# Fix 2: Check AI Agent health
curl https://ai-agent-service-production-XXXX.up.railway.app/health

# Fix 3: Restart services
railway service telegram-bot
railway restart
```

### Issue 2: Corrupted Conversation History

**Symptoms**: "unexpected tool_use_id" error in logs

**Diagnosis**:
```bash
# Check AI Agent logs
railway logs --service ai-agent | grep "tool_use_id"

# Cause: Service restarted mid-tool-execution
```

**Fix** (Automatic with new code):
```bash
# Auto-recovery is now implemented!
# AI Agent will automatically:
1. Detect corrupted history
2. Keep only last user message
3. Retry API call with clean history
4. Log recovery action

# Manual fix (if needed):
curl -X DELETE "https://ai-agent-service-production-XXXX.up.railway.app/conversations/{user_id}?channel=telegram"
```

### Issue 3: Service Won't Start

**Symptoms**: Deployment fails, service shows "Crashed"

**Diagnosis**:
```bash
# Check build logs
railway logs --service SERVICE_NAME --build

# Check deploy logs
railway logs --service SERVICE_NAME --deploy

# Common causes:
1. Missing dependencies in requirements.txt
2. Port binding error (forgot to use $PORT)
3. Database migration needed
```

**Fix**:
```bash
# Fix 1: Update requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: Update dependencies"
git push

# Fix 2: Verify start command uses $PORT
# In Railway settings or railway.json:
"startCommand": "./start.sh"

# start.sh should have:
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT

# Fix 3: Run migrations
railway run --service ai-agent python -m alembic upgrade head
```

---

## 🔒 Security Checklist

### Before Deploying to Production

- [ ] All API keys are in Railway variables (not committed to git)
- [ ] `.env` files are in `.gitignore`
- [ ] `DEBUG=false` in production
- [ ] CORS origins limited to known domains
- [ ] Database has strong password (Railway auto-generates)
- [ ] No hardcoded secrets in code

### Token Management

- [ ] TELEGRAM_TOKEN stored securely in Railway
- [ ] CLAUDE_API_KEY has spending limits set
- [ ] Backend SECRET_KEY is cryptographically random (not "secret123")

---

## 📊 Monitoring After Deployment

### Key Metrics to Watch

```bash
# 1. Response time (should be < 10 seconds)
railway logs --service ai-agent | grep "Request cost"

# 2. Cache hit rate (should be > 70%)
curl https://ai-agent-service-production-XXXX.up.railway.app/cache-stats

# 3. Error rate (should be < 1%)
railway logs --service telegram-bot | grep -i error | wc -l

# 4. Active conversations
railway run --service ai-agent psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"
```

### Daily Health Checks

```bash
#!/bin/bash
# Save as: scripts/daily_health_check.sh

echo "🏥 Running daily health checks..."

# Check AI Agent
AI_HEALTH=$(curl -s https://ai-agent-service-production-XXXX.up.railway.app/health)
echo "AI Agent: $AI_HEALTH"

# Check Telegram Bot
TG_HEALTH=$(curl -s https://telegram-bot-production-XXXX.up.railway.app/health)
echo "Telegram Bot: $TG_HEALTH"

# Check webhook
WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo")
echo "Webhook: $WEBHOOK_INFO"

echo "✅ Health check complete"
```

---

## 🎯 Prevention Best Practices

### 1. Always Test Locally First
- Run all services locally before deploying
- Test full conversation flow
- Verify tool execution (list_products, create_order)

### 2. Use Staging Environment
- Create `staging` branch
- Deploy to separate Railway project
- Test with real tokens but staging shop_id

### 3. Gradual Rollouts
- Deploy one service at a time
- Monitor for 5 minutes before next service
- Keep previous deployment ready for rollback

### 4. Automated Testing
```bash
# Add to CI/CD pipeline
pytest backend/tests/
pytest ai-agent-service-v2/tests/

# Run before every deploy:
./scripts/test_production_readiness.sh
```

---

## 🔄 Rollback Procedure

If deployment goes wrong:

```bash
# 1. Immediate rollback via Railway dashboard
# Click service → Deployments → Previous deployment → Redeploy

# OR via CLI:
railway rollback --service SERVICE_NAME

# 2. Verify rollback successful
railway logs --service SERVICE_NAME | tail -20

# 3. Investigate issue locally
git log -n 5  # Check recent commits
railway logs --service SERVICE_NAME > /tmp/logs.txt

# 4. Fix issue and redeploy
git revert HEAD  # OR fix and commit
git push origin main
```

---

## ✅ Final Checklist Before "Go Live"

- [ ] All environment variables verified
- [ ] TELEGRAM_TOKEN matches webhook (critical!)
- [ ] Local testing passed (all commands work)
- [ ] Railway deployment successful (all services Active)
- [ ] Health checks returning 200 OK
- [ ] Cache hit rate > 70%
- [ ] Webhook has no pending updates
- [ ] Test conversation completed successfully
- [ ] Error monitoring enabled
- [ ] Team notified of deployment

---

## 📞 Emergency Contacts

- Railway Dashboard: https://railway.app/dashboard
- Telegram Bot API: https://core.telegram.org/bots/api
- Claude API Status: https://status.anthropic.com
- Team Lead: [Add contact info]

---

## 📝 Changelog

Track all production deployments:

```markdown
### 2025-10-13 - Auto-Recovery & Graceful Shutdown
- Added auto-recovery for corrupted conversation history
- Implemented graceful shutdown for AI Agent (30s timeout)
- Added health check endpoint to Telegram Bot
- Fixed TELEGRAM_TOKEN mismatch (8080729458 → 8035864354)

### 2025-10-12 - Initial Production Deploy
- Deployed Backend, AI Agent, Telegram Bot to Railway
- Integrated Kaspi Pay for payments
- Enabled Prompt Caching (80%+ hit rate)
```

---

**Last Updated**: 2025-10-13
**Version**: 1.0
**Maintained By**: Development Team
