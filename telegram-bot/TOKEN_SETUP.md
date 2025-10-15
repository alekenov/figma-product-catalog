# Telegram Bot Token Setup Guide

## Current Token Configuration

Your bot has two tokens set up:

### Production Token
- **Status**: ✅ In Railway environment
- **Location**: Railway `TELEGRAM_TOKEN` env var
- **Usage**: Live bot in production
- **Security**: Protected by Railway environment variables

### Test Token
- **Value**: `[ALREADY EXPOSED - SEE SECURITY_INCIDENT_LOG.md]`
- **Status**: ✅ Available for local development
- **Location**: `.env` file (not committed to Git)
- **Usage**: Local testing with separate bot instance

## Setup for Local Development

### 1. Create `.env` file from template
```bash
cp .env.example .env
```

### 2. Update `.env` with your tokens
```bash
# For production token - get from Railway dashboard or BotFather
TELEGRAM_TOKEN=your_production_token

# For local testing (already set):
TEST_TELEGRAM_TOKEN=your_test_token_from_botfather
```

### 3. Start local bot with test token (polling mode)
```bash
source .venv/bin/activate
python bot.py  # Will use TEST_TELEGRAM_TOKEN for local testing
```

## Diagnostic Scripts Usage

### Check Production Bot
```bash
cd tooling
export TELEGRAM_TOKEN=your_production_token
python diagnose_bot.py
```

### Check Both Bots
```bash
cd tooling
export TELEGRAM_TOKEN=your_production_token
export TEST_TELEGRAM_TOKEN=your_test_token_from_botfather
python diagnose_bot.py
```

## Important: Compromised Token Action

⚠️ **URGENT**: The old production token was exposed in GitHub:
```
8035864354:AAHch7_0sT--M0xunghsWbyNS3pn_nKASVQ  (COMPROMISED - DO NOT USE)
```

✅ **ALREADY DONE**: You've rotated this token in Railway

### Verify Token Rotation
1. Go to @BotFather in Telegram
2. Select your bot (@cvetykzsupportbot)
3. Verify you've revoked the old token
4. Confirm new token is set in Railway

## Railway Environment Variables

Make sure Railway has:
```
TELEGRAM_TOKEN=<your_new_production_token>
TEST_TELEGRAM_TOKEN=<optional, usually not needed in production>
WEBHOOK_URL=https://your-railway-domain/webhook
```

## Security Best Practices

✅ **DO:**
- Keep `.env` file with local tokens in `.gitignore`
- Use separate tokens for production and testing
- Rotate tokens if they're exposed
- Store production token only in Railway (not in code)

❌ **DON'T:**
- Commit `.env` files to Git
- Share token values in logs or messages
- Hardcode tokens in scripts
- Use production token for local testing
