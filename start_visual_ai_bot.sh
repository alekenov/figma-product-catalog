#!/bin/bash
#
# Start Visual Search AI Bot (shop_id=17008)
# Requires: Backend API, AI Agent Service running
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🌸 Visual Search AI Bot - Startup Script"
echo "========================================"
echo ""

# Check if .env.visual_search exists
if [ ! -f ".env.visual_search" ]; then
    echo -e "${RED}❌ Error: .env.visual_search not found!${NC}"
    echo ""
    echo "Please create .env.visual_search with your configuration:"
    echo "  cp .env.visual_search.example .env.visual_search"
    echo "  # Edit .env.visual_search and set TELEGRAM_TOKEN"
    echo ""
    exit 1
fi

# Check if TELEGRAM_TOKEN is set
source .env.visual_search
if [ -z "$TELEGRAM_TOKEN" ] || [ "$TELEGRAM_TOKEN" = "your_visual_search_bot_token_here" ]; then
    echo -e "${RED}❌ Error: TELEGRAM_TOKEN not configured!${NC}"
    echo ""
    echo "Please edit .env.visual_search and set your Telegram bot token."
    echo "Get your token from @BotFather on Telegram."
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Configuration loaded from .env.visual_search${NC}"
echo "   Shop ID: $DEFAULT_SHOP_ID"
echo "   AI Agent: $AI_AGENT_URL"
echo "   MCP Server: $MCP_SERVER_URL"
echo ""

# Check if required services are running
echo "🔍 Checking required services..."

# Check Backend API
if ! curl -s -f "$BACKEND_API_URL/health" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend API not running at $BACKEND_API_URL${NC}"
    echo "   Start it with: cd backend && python3 main.py"
    echo ""
fi

# Check AI Agent Service
if ! curl -s -f "$AI_AGENT_URL/health" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  AI Agent Service not running at $AI_AGENT_URL${NC}"
    echo "   Start it with: cd ai-agent-service && python3 main.py"
    echo ""
fi

# Check MCP Server (optional - bot can work without it for basic features)
# if ! curl -s -f "$MCP_SERVER_URL/health" > /dev/null 2>&1; then
#     echo -e "${YELLOW}⚠️  MCP Server not running at $MCP_SERVER_URL${NC}"
#     echo "   (Optional - needed for advanced tool execution)"
#     echo ""
# fi

echo -e "${GREEN}✅ Service checks complete${NC}"
echo ""

# Check if Python dependencies are installed
echo "🔍 Checking Python dependencies..."
if ! python3 -c "import telegram" 2>/dev/null; then
    echo -e "${RED}❌ python-telegram-bot not installed!${NC}"
    echo "   Install with: pip3 install -r telegram-bot/requirements.txt"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Python dependencies OK${NC}"
echo ""

# Start the bot
echo "🚀 Starting Visual Search AI Bot..."
echo "   Press Ctrl+C to stop"
echo ""

python3 visual_search_ai_bot.py
