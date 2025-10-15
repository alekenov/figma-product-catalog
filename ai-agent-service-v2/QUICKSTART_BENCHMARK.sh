#!/bin/bash

# ✨ Quick Start: Model Comparison Benchmark
# Claude Haiku 4.5 vs Claude Sonnet 4.5

set -e

echo "🚀 Starting Claude Model Benchmark..."
echo ""

# Check if we're in the right directory
if [ ! -f "benchmark_models.py" ]; then
    echo "❌ Error: benchmark_models.py not found"
    echo "Make sure you're in ai-agent-service-v2 directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo ""
    echo "Please create .env file with:"
    echo "  CLAUDE_API_KEY=sk-ant-..."
    echo "  BACKEND_API_URL=http://localhost:8014/api/v1"
    echo ""
    exit 1
fi

# Load environment
set -a
source .env
set +a

# Check API key
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ Error: CLAUDE_API_KEY not set in .env"
    exit 1
fi

echo "✅ Environment loaded"
echo ""

# Check backend is running
echo "🔍 Checking if backend API is available..."
if ! curl -s http://localhost:8014/health > /dev/null 2>&1; then
    echo "⚠️  Backend API not available on port 8014"
    echo ""
    echo "Start it with:"
    echo "  cd ../backend"
    echo "  python main.py"
    echo ""
    echo "Or run full setup:"
    echo "  ./scripts/start.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Backend is ready"
echo ""

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "⚠️  Missing pyyaml, installing..."
    pip install pyyaml
fi

echo "✅ Dependencies ready"
echo ""

# Run benchmark
echo "================================"
echo "🧪 Running benchmark with:"
echo "  • Claude Haiku 4.5 (fast & cheap)"
echo "  • Claude Sonnet 4.5 (quality)"
echo "================================"
echo ""

python3 benchmark_models.py

# Check if results were generated
if [ -f "benchmark_results.json" ]; then
    echo ""
    echo "✅ Benchmark complete!"
    echo ""
    echo "📊 Results:"
    echo "  • benchmark_results.json (detailed metrics)"
    echo "  • benchmark_results_report.txt (human-readable)"
    echo ""
    echo "📖 To read the report:"
    echo "  cat benchmark_results_report.txt"
    echo ""
    echo "📈 To view JSON results:"
    echo "  cat benchmark_results.json | jq"
    echo ""
else
    echo "❌ Benchmark failed - no results generated"
    exit 1
fi
