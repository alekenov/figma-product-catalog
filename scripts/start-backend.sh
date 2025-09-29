#!/bin/bash

# Start Backend API on port 8014
echo "🔧 Starting Backend API..."
echo "=================================="
echo "API URL: http://localhost:8014"
echo "API Docs: http://localhost:8014/docs"
echo "=================================="

# Kill any existing process on port 8014
lsof -ti:8014 | xargs kill -9 2>/dev/null && echo "✅ Cleared port 8014"

# Navigate to backend directory and start
cd "$(dirname "$0")/../backend"
python3 main.py