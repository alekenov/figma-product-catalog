#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/alekenov/figma-product-catalog"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  LOCAL DEVELOPMENT ENVIRONMENT SETUP                       ║${NC}"
echo -e "${BLUE}║  Backend + MCP Server + AI Agent + Telegram Bot           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Function to print section header
print_section() {
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check if port is available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}✗ Port $port ($service) is already in use!${NC}"
        return 1
    else
        echo -e "${GREEN}✓ Port $port available for $service${NC}"
        return 0
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓ Found: $1${NC}"
        return 0
    else
        echo -e "${RED}✗ Not found: $1${NC}"
        return 1
    fi
}

# ============================================================================
# ENVIRONMENT CHECKS
# ============================================================================
print_section "1. CHECKING ENVIRONMENT"

echo -e "${YELLOW}Checking directories...${NC}"
check_dir "$PROJECT_ROOT/backend" && backend_ok=1 || backend_ok=0
check_dir "$PROJECT_ROOT/mcp-server" && mcp_ok=1 || mcp_ok=0
check_dir "$PROJECT_ROOT/ai-agent-service" && ai_ok=1 || ai_ok=0
check_dir "$PROJECT_ROOT/telegram-bot" && bot_ok=1 || bot_ok=0

echo -e "\n${YELLOW}Checking available ports...${NC}"
check_port 8014 "Backend" && port_8014_ok=1 || port_8014_ok=0
check_port 8000 "MCP Server" && port_8000_ok=1 || port_8000_ok=0
check_port 8002 "AI Agent" && port_8002_ok=1 || port_8002_ok=0

# ============================================================================
# INSTRUCTIONS
# ============================================================================
print_section "2. STARTUP INSTRUCTIONS"

echo -e "${YELLOW}Open 4 NEW TERMINAL WINDOWS and run each command in order:${NC}"

echo -e "\n${BLUE}[TERMINAL 1] - Backend (FastAPI)${NC}"
echo -e "${YELLOW}cd $PROJECT_ROOT/backend${NC}"
echo -e "${YELLOW}python3 main.py${NC}"
echo -e "Expected: ${GREEN}\"Application startup complete\"${NC}"
echo -e "Port: ${GREEN}http://localhost:8014${NC}"

echo -e "\n${BLUE}[TERMINAL 2] - MCP Server${NC}"
echo -e "${YELLOW}cd $PROJECT_ROOT/mcp-server${NC}"
echo -e "${YELLOW}./start.sh${NC}"
echo -e "Expected: ${GREEN}\"Server running on\"${NC}"
echo -e "Port: ${GREEN}http://localhost:8000${NC}"

echo -e "\n${BLUE}[TERMINAL 3] - AI Agent Service V2${NC}"
echo -e "${YELLOW}cd $PROJECT_ROOT/ai-agent-service${NC}"
echo -e "${YELLOW}python3 main.py${NC}"
echo -e "Expected: ${GREEN}\"Application startup complete\"${NC}"
echo -e "Port: ${GREEN}http://localhost:8002${NC}"

echo -e "\n${BLUE}[TERMINAL 4] - Telegram Bot${NC}"
echo -e "${YELLOW}cd $PROJECT_ROOT/telegram-bot${NC}"
echo -e "${YELLOW}python3 bot.py${NC}"
echo -e "Expected: ${GREEN}\"Bot started in polling mode\"${NC}"

# ============================================================================
# VERIFICATION
# ============================================================================
print_section "3. AFTER STARTUP - VERIFY SERVICES"

echo -e "${YELLOW}Run these commands to verify all services are running:${NC}"

echo -e "\n${BLUE}Backend Health:${NC}"
echo -e "curl http://localhost:8014/health"

echo -e "\n${BLUE}MCP Server Status:${NC}"
echo -e "curl http://localhost:8000/health"

echo -e "\n${BLUE}AI Agent Status:${NC}"
echo -e "curl http://localhost:8002/health"

echo -e "\n${BLUE}Telegram Bot:${NC}"
echo -e "Should show polling messages in the terminal"

# ============================================================================
# EXPECTED LOGS
# ============================================================================
print_section "4. EXPECTED LOGS"

echo -e "${GREEN}Backend (8014):${NC}"
echo -e '  [INFO] Uvicorn running on http://0.0.0.0:8014'
echo -e '  [INFO] Application startup complete'

echo -e "\n${GREEN}MCP Server (8000):${NC}"
echo -e '  Server running on http://0.0.0.0:8000'
echo -e '  Listening for requests...'

echo -e "\n${GREEN}AI Agent (8002):${NC}"
echo -e '  [INFO] Uvicorn running on http://0.0.0.0:8002'
echo -e '  [INFO] Application startup complete'
echo -e '  [INFO] Cache stats: hits=0, misses=0'

echo -e "\n${GREEN}Telegram Bot:${NC}"
echo -e '  [INFO] message_received: user_id=...'
echo -e '  [INFO] authorization_check: is_authorized=True'
echo -e '  [INFO] message_handling_success'

# ============================================================================
# TESTING
# ============================================================================
print_section "5. TEST THE BOT"

echo -e "${YELLOW}To test the bot locally without Telegram:${NC}"

echo -e "\n${BLUE}Option A: Run automated tests${NC}"
echo -e "${YELLOW}cd $PROJECT_ROOT/telegram-bot${NC}"
echo -e "${YELLOW}pytest tests/ -v${NC}"
echo -e "${YELLOW}python test_scenarios.py${NC}"

echo -e "\n${BLUE}Option B: Use the real Telegram bot${NC}"
echo -e "1. Open Telegram: Search for @cvetykzsupportbot"
echo -e "2. Send: /start"
echo -e "3. Share your contact"
echo -e "4. Try: /catalog, /myorders, or type a message"

echo -e "\n${BLUE}Option C: Send test messages via curl${NC}"
echo -e "curl -X POST http://localhost:8002/chat \\"
echo -e "  -H 'Content-Type: application/json' \\"
echo -e "  -d '{\"message\":\"Hello\",\"user_id\":\"test_user\",\"channel\":\"telegram\"}'"

# ============================================================================
# ARCHITECTURE
# ============================================================================
print_section "6. ARCHITECTURE OVERVIEW"

cat << 'EOF'
┌────────────────────────────────────────────────────────────────┐
│                    LOCAL DEV ARCHITECTURE                      │
└────────────────────────────────────────────────────────────────┘

    Telegram Bot (polling mode)
    ┌─────────────────────┐
    │  Polling Messages   │
    │  PORT: (local only) │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────────────────────┐
    │  AI Agent Service V2                │
    │  PORT: 8002                         │
    │  • Chat endpoint                    │
    │  • Product recommendations          │
    │  • Conversation history (SQLite)    │
    │  • Prompt caching                   │
    └──────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    MCP Server    Backend API
    PORT: 8000    PORT: 8014
    • Tools       • Products
    • Auth        • Orders
    • Orders      • Shop Settings
               │
               ▼
    PostgreSQL Database
    (Railway or local)

EOF

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
print_section "7. TROUBLESHOOTING"

cat << 'EOF'
❌ "Port already in use"
   → Kill process: lsof -ti:8014 | xargs kill -9
   → Or use different port: PORT=8015 python3 main.py

❌ "ModuleNotFoundError: No module named 'X'"
   → Install dependencies: pip install -r requirements.txt

❌ "Connection refused" error
   → Check all 4 services are running
   → Check ports 8014, 8000, 8002 are available
   → Check .env files have correct URLs

❌ Bot shows "authorization_check_failed"
   → Verify MCP Server (port 8000) is running
   → Check BACKEND_API_URL in bot.py environment

❌ No PostgreSQL connection
   → Use local SQLite (Backend has fallback)
   → Or connect to Railway PostgreSQL
   → Check DATABASE_URL in backend .env

EOF

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================
print_section "8. ENVIRONMENT VARIABLES NEEDED"

cat << 'EOF'
Create .env files if they don't exist:

Backend (.env):
  DATABASE_URL=postgresql://...  (or leave for SQLite)
  DEBUG=true
  CORS_ORIGINS=http://localhost:3000,http://localhost:8002

MCP Server (.env):
  BACKEND_API_URL=http://localhost:8014/api/v1
  DEFAULT_SHOP_ID=8

AI Agent V2 (.env):
  CLAUDE_API_KEY=sk-ant-...
  CLAUDE_MODEL=claude-haiku-4-5-20251001
  MCP_SERVER_URL=http://localhost:8000
  BACKEND_API_URL=http://localhost:8014/api/v1
  DEFAULT_SHOP_ID=8
  PORT=8002

Telegram Bot (.env):
  TELEGRAM_TOKEN=...  (from @BotFather)
  MCP_SERVER_URL=http://localhost:8000
  AI_AGENT_URL=http://localhost:8002
  BACKEND_API_URL=http://localhost:8014/api/v1
  DEFAULT_SHOP_ID=8

EOF

# ============================================================================
# SUMMARY
# ============================================================================
print_section "9. QUICK START SUMMARY"

cat << 'EOF'
1. Open 4 terminals
2. Run commands from section "2. STARTUP INSTRUCTIONS"
3. Check logs from section "4. EXPECTED LOGS"
4. Test using section "5. TEST THE BOT"

Once running:
  • Backend: http://localhost:8014
  • MCP Server: http://localhost:8000
  • AI Agent: http://localhost:8002
  • Bot: Polling mode (no HTTP port)

All services will share:
  • Same shop_id (8)
  • Same PostgreSQL database (or SQLite)
  • Claude API (AI Agent)

Ready to test! 🚀

EOF

print_section "READY TO START"
echo -e "${GREEN}✓ Environment check complete${NC}"
echo -e "${GREEN}✓ All required directories found${NC}"
echo -e "${GREEN}✓ Ports available${NC}"
echo -e "\n${YELLOW}Next: Open 4 terminals and follow the commands in section 2${NC}\n"
