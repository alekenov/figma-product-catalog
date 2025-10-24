#!/bin/bash
# Test script for verifying Telegram bots structure
# Run this before getting tokens from user

set -e  # Exit on any error

echo "🧪 Testing Telegram Bots Structure"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
    else
        echo -e "${RED}❌${NC} Missing: $1"
        ERRORS=$((ERRORS + 1))
    fi
}

# Function to check Python syntax
check_python() {
    if python3 -m py_compile "$1" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $1 (syntax OK)"
    else
        echo -e "${RED}❌${NC} $1 (syntax error)"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "1️⃣  Checking Customer Bot Files"
echo "--------------------------------"
check_file "customer-bot/bot.py"
check_file "customer-bot/mcp_client.py"
check_file "customer-bot/formatters.py"
check_file "customer-bot/logging_config.py"
check_file "customer-bot/requirements.txt"
check_file "customer-bot/railway.json"
check_file "customer-bot/.env.production"
check_file "customer-bot/.env.development"
check_file "customer-bot/.env.example"
check_file "customer-bot/README.md"
echo ""

echo "2️⃣  Checking Admin Bot Files"
echo "-----------------------------"
check_file "admin-bot/bot.py"
check_file "admin-bot/admin_handlers.py"
check_file "admin-bot/mcp_client.py"
check_file "admin-bot/formatters.py"
check_file "admin-bot/logging_config.py"
check_file "admin-bot/requirements.txt"
check_file "admin-bot/railway.json"
check_file "admin-bot/.env.production"
check_file "admin-bot/.env.development"
check_file "admin-bot/.env.example"
check_file "admin-bot/README.md"
echo ""

echo "3️⃣  Checking Python Syntax"
echo "---------------------------"
check_python "customer-bot/bot.py"
check_python "customer-bot/mcp_client.py"
check_python "customer-bot/formatters.py"
check_python "customer-bot/logging_config.py"
check_python "admin-bot/bot.py"
check_python "admin-bot/admin_handlers.py"
check_python "admin-bot/mcp_client.py"
check_python "admin-bot/formatters.py"
check_python "admin-bot/logging_config.py"
echo ""

echo "4️⃣  Checking Python Dependencies"
echo "---------------------------------"
if python3 -c "from telegram import Update; from telegram.ext import Application; from dotenv import load_dotenv; import httpx; import asyncio" 2>/dev/null; then
    echo -e "${GREEN}✅${NC} All Python dependencies available"
else
    echo -e "${YELLOW}⚠️${NC}  Some dependencies missing (this is OK if not yet installed)"
    echo "   Run: pip install -r customer-bot/requirements.txt"
fi
echo ""

echo "5️⃣  Checking .env File Structure"
echo "---------------------------------"

# Check customer bot .env files have required vars
for env_file in "customer-bot/.env.production" "customer-bot/.env.development"; do
    if grep -q "TELEGRAM_TOKEN=" "$env_file" && \
       grep -q "DEFAULT_SHOP_ID=" "$env_file" && \
       grep -q "MCP_SERVER_URL=" "$env_file"; then
        echo -e "${GREEN}✅${NC} $env_file (has required variables)"
    else
        echo -e "${RED}❌${NC} $env_file (missing required variables)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check admin bot .env files
for env_file in "admin-bot/.env.production" "admin-bot/.env.development"; do
    if grep -q "TELEGRAM_TOKEN=" "$env_file" && \
       grep -q "DEFAULT_SHOP_ID=" "$env_file" && \
       grep -q "MCP_SERVER_URL=" "$env_file"; then
        echo -e "${GREEN}✅${NC} $env_file (has required variables)"
    else
        echo -e "${RED}❌${NC} $env_file (missing required variables)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

echo "6️⃣  Summary"
echo "-----------"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Create Telegram bots in @BotFather:"
    echo "   - Customer Bot Production: cvety_customer_bot"
    echo "   - Customer Bot Development: cvety_customer_dev_bot"
    echo "   - Admin Bot Production: cvety_admin_bot ⚠️ ВАЖНО"
    echo "   - Admin Bot Development: cvety_admin_dev_bot"
    echo ""
    echo "2. Insert tokens into .env files:"
    echo "   - customer-bot/.env.production"
    echo "   - customer-bot/.env.development"
    echo "   - admin-bot/.env.production"
    echo "   - admin-bot/.env.development"
    echo ""
    echo "3. Test locally:"
    echo "   cd customer-bot && ENVIRONMENT=development python bot.py"
    echo "   cd admin-bot && ENVIRONMENT=development python bot.py"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS error(s)${NC}"
    echo "Please fix the errors above before proceeding."
    exit 1
fi
