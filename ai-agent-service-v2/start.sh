#!/bin/sh
# AI Agent Service V2 start script for Railway

PORT=${PORT:-8001}
HOST=${HOST:-0.0.0.0}

echo "🚀 Starting AI Agent Service V2"
echo "📡 PORT: $PORT"
echo "🏪 SHOP_ID: ${DEFAULT_SHOP_ID}"
echo "💾 DATABASE_URL: ${DATABASE_URL:0:50}..."

# Run the application
exec python main.py
