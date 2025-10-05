#!/bin/sh
# MCP Server start script for Railway deployment

PORT=${PORT:-8000}

echo "🚀 Starting MCP Server on port $PORT"
echo "📡 API_BASE_URL: ${API_BASE_URL}"
echo "🏪 DEFAULT_SHOP_ID: ${DEFAULT_SHOP_ID}"

# Run MCP server with streamable HTTP transport using fastmcp CLI
exec fastmcp run server.py --transport streamable-http --host 0.0.0.0 --port $PORT
