#!/bin/bash
# Local telegram bot startup script with logging

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Create logs directory if not exists
mkdir -p logs

# Stop any existing bot processes
pkill -f "python bot.py"

# Start bot in background with logging
echo "🤖 Starting Telegram Bot locally..."
python bot.py > logs/bot.log 2>&1 &

BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"
echo $BOT_PID > logs/bot.pid

# Show initial logs
sleep 2
tail -f logs/bot.log
