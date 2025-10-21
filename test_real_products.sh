#!/bin/bash

echo "🔍 Testing Visual Search with REAL Production Products"
echo "========================================================"
echo ""

echo "Test 1: Поиск похожих на 'Кустовые розы Софи'"
echo "Query image: https://cvety.kz/upload/resize_cache/iblock/a97/xz49vqgvoeshj87kyqdsori263robezf/435_545_2/IMG_0021.jpeg"
curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://cvety.kz/upload/resize_cache/iblock/a97/xz49vqgvoeshj87kyqdsori263robezf/435_545_2/IMG_0021.jpeg",
    "shop_id": 17008,
    "limit": 5,
    "min_similarity": 0.0
  }' | jq -r '.results[] | "\(.name) (ID: \(.id)): similarity = \(.similarity)"'

echo ""
echo "========================================================" 
echo ""

echo "Test 2: Поиск похожих на 'Эустомы'"
echo "Query image: https://cvety.kz/upload/resize_cache/iblock/3e2/u4yrcubt06twntysswnzh8n4b8bmuyz7/435_545_2/IMG_5536.jpeg"
curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://cvety.kz/upload/resize_cache/iblock/3e2/u4yrcubt06twntysswnzh8n4b8bmuyz7/435_545_2/IMG_5536.jpeg",
    "shop_id": 17008,
    "limit": 5,
    "min_similarity": 0.6
  }' | jq -r '.results[] | "\(.name) (ID: \(.id)): similarity = \(.similarity)"'

echo ""
echo "========================================================"
echo ""

echo "Test 3: Статистика"
curl -s "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/stats?shop_id=17008" | jq .
