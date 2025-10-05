#!/bin/sh
# MCP Server start script for Railway deployment

PORT=${PORT:-8000}

echo "🚀 Starting MCP Server on port $PORT"
echo "📡 API_BASE_URL: ${API_BASE_URL}"
echo "🏪 DEFAULT_SHOP_ID: ${DEFAULT_SHOP_ID}"

# Run HTTP wrapper server (FastAPI)
exec python http_server.py
