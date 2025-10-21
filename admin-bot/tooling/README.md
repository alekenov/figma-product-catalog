# Telegram Bot Tooling Scripts

This directory contains utility and diagnostic scripts for the Telegram bot. These are **NOT** part of the main bot application and should only be used for development/debugging.

## Files

### `diagnose_bot.py`
Diagnostic script to check Telegram bot status and webhook configuration.

**Usage:**
```bash
cd tooling

# For production bot:
export TELEGRAM_TOKEN=your_production_token
python diagnose_bot.py

# For separate test bot (optional):
export TELEGRAM_TOKEN=your_production_token
export TEST_TELEGRAM_TOKEN=your_test_token
python diagnose_bot.py
```

**What it does:**
- Checks production bot validity
- Checks test bot (if TEST_TELEGRAM_TOKEN is set)
- Verifies webhook status
- Tests polling/webhook mode
- Provides recommendations

**Requirements:** `requests` library (install from bot requirements.txt)

**Environment Variables:**
- `TELEGRAM_TOKEN` - Production bot token (required)
- `TEST_TELEGRAM_TOKEN` - Test bot token (optional, for local testing)

### `clear_webhook.py`
Utility to clear webhook and reset bot to polling mode.

**Usage:**
```bash
cd tooling
export TELEGRAM_TOKEN=your_token_here
python clear_webhook.py
```

**What it does:**
- Deletes webhook configuration
- Resets bot to polling mode
- Drops pending updates

**Requirements:** `requests` library

## Important Security Notes

⚠️ **NEVER hardcode tokens** - Always use environment variables:
```bash
# ✅ Correct:
export TELEGRAM_TOKEN=your_token
python diagnose_bot.py

# ❌ Wrong:
# Don't add tokens to scripts or .env files that get committed!
```

🔒 **Best Practices:**
- Only run these scripts during development/debugging
- Never share token values in logs or output
- Never commit `.env` files with tokens to Git
- Keep these scripts out of production deployments
- Use separate tokens for production and testing (if possible)

## Token Separation (Recommended)

For best security, use different tokens for different environments:

**Production (Railway):**
```bash
TELEGRAM_TOKEN=prod_token_here
```

**Local Testing (optional):**
```bash
# In .env (not committed):
TELEGRAM_TOKEN=prod_token_here
TEST_TELEGRAM_TOKEN=test_token_here
```

Then `diagnose_bot.py` will check both if both are set.
