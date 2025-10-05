#!/bin/bash
# Start Flower Shop MCP Server

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌸 Starting Flower Shop MCP Server${NC}\n"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3.12 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

# Set environment variables
export API_BASE_URL="${API_BASE_URL:-http://localhost:8014/api/v1}"
export DEFAULT_SHOP_ID="${DEFAULT_SHOP_ID:-8}"

echo -e "${GREEN}📡 API URL: ${API_BASE_URL}${NC}"
echo -e "${GREEN}🏪 Shop ID: ${DEFAULT_SHOP_ID}${NC}\n"

# Run the server
exec .venv/bin/python server.py
