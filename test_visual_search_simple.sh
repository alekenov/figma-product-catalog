#!/bin/bash

echo "🔍 Simple Visual Search Test"
echo "=============================="
echo ""

echo "Тестируем с изображением того же продукта (должен вернуть similarity=1.0)..."
echo ""

curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
    "shop_id": 8,
    "limit": 5,
    "min_similarity": 0.0
  }' | jq .

echo ""
echo "Ожидаем:"
echo "  - total_results: 1"
echo "  - similarity: 1.0 (или очень близко)"
echo "  - product_id: 999888"
