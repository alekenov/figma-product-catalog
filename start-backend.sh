#!/bin/bash

# Start Backend API on port 8012
echo "🔧 Starting Backend API..."
echo "=================================="
echo "API URL: http://localhost:8012"
echo "API Docs: http://localhost:8012/docs"
echo "=================================="

# Kill any existing process on port 8012
lsof -ti:8012 | xargs kill -9 2>/dev/null && echo "✅ Cleared port 8012"

# Start backend
cd backend
python3 main.py