#!/bin/bash

# Запуск всех 4 сервисов как background процессов с логированием
# Usage: ./run-all-services.sh

PROJECT_ROOT="/Users/alekenov/figma-product-catalog"
LOGS_DIR="${PROJECT_ROOT}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Создаем директорию логов
mkdir -p "$LOGS_DIR"
mkdir -p "$PROJECT_ROOT/backend/logs"
mkdir -p "$PROJECT_ROOT/mcp-server/logs"
mkdir -p "$PROJECT_ROOT/ai-agent-service-v2/logs"
mkdir -p "$PROJECT_ROOT/telegram-bot/logs"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  STARTING ALL SERVICES IN BACKGROUND                       ║"
echo "║  Timestamp: $TIMESTAMP                          ║"
echo "╚════════════════════════════════════════════════════════════╝"

# ============================================================================
# 1. BACKEND
# ============================================================================
echo ""
echo "1️⃣  Starting Backend (port 8014)..."
cd "$PROJECT_ROOT/backend"

# Kill previous instance if exists
lsof -ti:8014 | xargs kill -9 2>/dev/null || true

# Start backend and log
LOG_FILE="$PROJECT_ROOT/backend/logs/backend_${TIMESTAMP}.log"
python3 main.py > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!
echo "   ✅ Started (PID: $BACKEND_PID)"
echo "   📝 Logs: $LOG_FILE"

# Wait for backend to be ready
sleep 3
if lsof -Pi :8014 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✓ Backend is ready on http://localhost:8014"
else
    echo "   ⚠️  Backend might not be ready yet, trying anyway..."
fi

# ============================================================================
# 2. MCP SERVER
# ============================================================================
echo ""
echo "2️⃣  Starting MCP Server (port 8000)..."
cd "$PROJECT_ROOT/mcp-server"

# Kill previous instance
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start MCP and log
LOG_FILE="$PROJECT_ROOT/mcp-server/logs/mcp_${TIMESTAMP}.log"
./start.sh > "$LOG_FILE" 2>&1 &
MCP_PID=$!
echo "   ✅ Started (PID: $MCP_PID)"
echo "   📝 Logs: $LOG_FILE"

# Wait for MCP to be ready
sleep 3
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✓ MCP Server is ready on http://localhost:8000"
else
    echo "   ⚠️  MCP Server might not be ready yet, trying anyway..."
fi

# ============================================================================
# 3. AI AGENT
# ============================================================================
echo ""
echo "3️⃣  Starting AI Agent V2 (port 8001)..."
cd "$PROJECT_ROOT/ai-agent-service-v2"

# Kill previous instance
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Start AI Agent and log
LOG_FILE="$PROJECT_ROOT/ai-agent-service-v2/logs/ai_agent_${TIMESTAMP}.log"
python3 main.py > "$LOG_FILE" 2>&1 &
AI_PID=$!
echo "   ✅ Started (PID: $AI_PID)"
echo "   📝 Logs: $LOG_FILE"

# Wait for AI Agent to be ready
sleep 3
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✓ AI Agent is ready on http://localhost:8001"
else
    echo "   ⚠️  AI Agent might not be ready yet, trying anyway..."
fi

# ============================================================================
# 4. TELEGRAM BOT
# ============================================================================
echo ""
echo "4️⃣  Starting Telegram Bot (polling mode)..."
cd "$PROJECT_ROOT/telegram-bot"

# Start Bot and log
LOG_FILE="$PROJECT_ROOT/telegram-bot/logs/bot_${TIMESTAMP}.log"
python3 bot.py > "$LOG_FILE" 2>&1 &
BOT_PID=$!
echo "   ✅ Started (PID: $BOT_PID)"
echo "   📝 Logs: $LOG_FILE"

# ============================================================================
# STATUS
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ALL SERVICES STARTED                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "📊 Service Status:"
echo "  Backend:        PID=$BACKEND_PID (port 8014)"
echo "  MCP Server:     PID=$MCP_PID (port 8000)"
echo "  AI Agent:       PID=$AI_PID (port 8001)"
echo "  Telegram Bot:   PID=$BOT_PID (polling)"

echo ""
echo "📁 Log Files:"
echo "  Backend:    tail -f $PROJECT_ROOT/backend/logs/backend_${TIMESTAMP}.log"
echo "  MCP:        tail -f $PROJECT_ROOT/mcp-server/logs/mcp_${TIMESTAMP}.log"
echo "  AI Agent:   tail -f $PROJECT_ROOT/ai-agent-service-v2/logs/ai_agent_${TIMESTAMP}.log"
echo "  Bot:        tail -f $PROJECT_ROOT/telegram-bot/logs/bot_${TIMESTAMP}.log"

echo ""
echo "🧪 Testing:"
echo "  Health checks:"
echo "    curl http://localhost:8014/health"
echo "    curl http://localhost:8000/health"
echo "    curl http://localhost:8001/health"

echo ""
echo "📁 Main Log Directory:"
echo "  $LOGS_DIR"

echo ""
echo "💾 Save all PIDs for killing later:"
echo "  export PIDS=\"$BACKEND_PID $MCP_PID $AI_PID $BOT_PID\""
echo "  kill $PIDS  # To stop all services"

# Save PIDs to file for easy access
echo "$BACKEND_PID" > "$LOGS_DIR/pids.txt"
echo "$MCP_PID" >> "$LOGS_DIR/pids.txt"
echo "$AI_PID" >> "$LOGS_DIR/pids.txt"
echo "$BOT_PID" >> "$LOGS_DIR/pids.txt"

echo ""
echo "✅ Setup complete! Services are running in background."
echo "📝 Tail logs to see what's happening:"
echo "   tail -f $PROJECT_ROOT/telegram-bot/logs/bot_${TIMESTAMP}.log"
