#!/bin/sh
# AI Agent Service start script for Railway deployment

PORT=${PORT:-8000}

echo "🤖 Starting AI Agent Service on port $PORT"
echo "📡 MCP_SERVER_URL: ${MCP_SERVER_URL}"
echo "🏪 DEFAULT_SHOP_ID: ${DEFAULT_SHOP_ID}"

# Run FastAPI server
exec uvicorn main:app --host 0.0.0.0 --port $PORT
