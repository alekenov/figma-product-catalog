#!/bin/bash
# Test pickup (самовывоз) scenarios

echo "🏪 Testing Pickup Functionality"
echo "================================"
echo ""

# Check if CLAUDE_API_KEY is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ Error: CLAUDE_API_KEY environment variable is not set"
    echo "Please set it with: export CLAUDE_API_KEY=your-key-here"
    exit 1
fi

cd /Users/alekenov/figma-product-catalog/testing-framework

echo "1️⃣ Test 14: Simple Pickup (прямая фраза 'самовывоз')"
python3 test_orchestrator.py scenarios/14_pickup_simple.yaml
echo ""

echo "2️⃣ Test 15: Natural Language Pickup (естественный язык)"
python3 test_orchestrator.py scenarios/15_pickup_natural_language.yaml
echo ""

echo "3️⃣ Test 16: Pickup vs Delivery Comparison (сравнение доставки и самовывоза)"
python3 test_orchestrator.py scenarios/16_pickup_vs_delivery_comparison.yaml
echo ""

echo "✅ Pickup tests completed!"
