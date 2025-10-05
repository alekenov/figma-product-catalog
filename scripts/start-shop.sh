#!/bin/bash
# Start customer-facing shop (new version)

cd "$(dirname "$0")/../shop"

echo "🛍️  Starting Shop (New Version) on port 5180..."
echo "📁 Working directory: $(pwd)"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start development server
npm run dev
