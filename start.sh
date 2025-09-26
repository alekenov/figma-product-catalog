#!/bin/bash

# Start script for Figma Product Catalog
# Backend: http://localhost:8012
# Frontend: http://localhost:5176

echo "🚀 Starting Figma Product Catalog..."
echo "=================================="
echo "Backend API: http://localhost:8012"
echo "Frontend UI: http://localhost:5176"
echo "API Docs: http://localhost:8012/docs"
echo "=================================="

# Kill any existing processes on our ports
echo "📋 Checking for existing processes..."
lsof -ti:8012 | xargs kill -9 2>/dev/null && echo "✅ Cleared port 8012"
lsof -ti:5176 | xargs kill -9 2>/dev/null && echo "✅ Cleared port 5176"

# Start backend in background
echo ""
echo "🔧 Starting Backend API on port 8012..."
cd backend
python3 main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 2

# Start frontend
echo ""
echo "🎨 Starting Frontend on port 5176..."
cd ..
npm run dev

# When frontend is stopped, kill backend too
echo ""
echo "🛑 Shutting down..."
kill $BACKEND_PID 2>/dev/null
echo "✅ Services stopped"