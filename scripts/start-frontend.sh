#!/bin/bash

# Start Frontend on port 5176
echo "🎨 Starting Frontend UI..."
echo "=================================="
echo "Frontend URL: http://localhost:5176"
echo "Connecting to API: http://localhost:8014"
echo "=================================="

# Kill any existing process on port 5176
lsof -ti:5176 | xargs kill -9 2>/dev/null && echo "✅ Cleared port 5176"

# Navigate to frontend directory and start
cd "$(dirname "$0")/../frontend"
npm run dev