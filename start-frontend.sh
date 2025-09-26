#!/bin/bash

# Start Frontend on port 5176
echo "🎨 Starting Frontend UI..."
echo "=================================="
echo "Frontend URL: http://localhost:5176"
echo "Connecting to API: http://localhost:8012"
echo "=================================="

# Kill any existing process on port 5176
lsof -ti:5176 | xargs kill -9 2>/dev/null && echo "✅ Cleared port 5176"

# Start frontend
npm run dev