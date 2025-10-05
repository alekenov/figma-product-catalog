#!/bin/bash
# Local MCP server startup script with logging

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Create logs directory if not exists
mkdir -p logs

# Kill all existing MCP server processes
pkill -f "mcp-server\|fastmcp\|server.py"
sleep 1

# Set environment variables
export API_BASE_URL="https://figma-product-catalog-production.up.railway.app/api/v1"
export DEFAULT_SHOP_ID="8"

echo "🚀 Starting MCP Server locally on port 8000..."
echo "📡 API_BASE_URL: $API_BASE_URL"
echo "🏪 DEFAULT_SHOP_ID: $DEFAULT_SHOP_ID"

# Start MCP server using direct Python (avoiding asyncio conflict with fastmcp CLI)
nohup python -c "
import asyncio
from server import mcp

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await mcp.run(read, write, mcp.create_initialization_options())

if __name__ == '__main__':
    asyncio.run(main())
" > logs/mcp.log 2>&1 &

MCP_PID=$!
echo "✅ MCP Server started with PID: $MCP_PID"
echo $MCP_PID > logs/mcp.pid

sleep 2
echo "📋 Server logs:"
tail -20 logs/mcp.log
