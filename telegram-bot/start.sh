#!/bin/sh
# Telegram Bot start script for Railway deployment

PORT=${PORT:-8080}

echo "🤖 Starting Telegram Bot"
echo "📡 MCP_SERVER_URL: ${MCP_SERVER_URL}"
echo "🏪 DEFAULT_SHOP_ID: ${DEFAULT_SHOP_ID}"

# Check if webhook mode is enabled
if [ -n "$WEBHOOK_URL" ]; then
    echo "🌐 Running in WEBHOOK mode on port $PORT"
    echo "🔗 Webhook URL: ${WEBHOOK_URL}"
else
    echo "🔄 Running in POLLING mode"
fi

# Run bot
exec python bot.py
