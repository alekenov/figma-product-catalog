#!/bin/sh
# Start script for Telegram Bot on Railway deployment

PORT=${PORT:-8080}
echo "Starting Telegram Bot on port $PORT"

# Install dependencies if needed
pip install -q -r requirements.txt

# Run the bot
python bot.py
