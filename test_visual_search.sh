#!/bin/bash

echo "🔍 Visual Search API Tests"
echo "=========================="
echo ""

# Test 1: Check search stats
echo "📊 Test 1: Check search statistics"
echo "-----------------------------------"
curl -s "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/stats?shop_id=8" | jq .
echo ""

# Test 2: Search for similar products
echo "🔎 Test 2: Search for similar products"
echo "---------------------------------------"
curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
    "shop_id": 8,
    "limit": 5,
    "min_similarity": 0.0
  }' | jq .
echo ""

# Test 3: Search with high similarity threshold
echo "🎯 Test 3: Search with min_similarity=0.8"
echo "------------------------------------------"
curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
    "shop_id": 8,
    "limit": 10,
    "min_similarity": 0.8
  }' | jq '{success, total_results, search_duration_ms, results: [.results[] | {id, name, similarity}]}'
echo ""

echo "✅ Visual Search tests completed!"
