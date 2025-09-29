#!/bin/bash

# Start Website Development Server
cd "$(dirname "$0")/../website" || exit 1

echo "🌐 Starting Website on http://localhost:5177"
npm run dev