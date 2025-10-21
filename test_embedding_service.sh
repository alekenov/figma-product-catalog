#!/bin/bash

echo "🧪 Test 1: Проверка Embedding Service"
echo "======================================"
curl -X POST "https://embedding-service-production-4aaa.up.railway.app/embed/image" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png", "product_id": 123}' \
  | jq '{success, dimensions, model, duration_ms}'

echo ""
echo "🧪 Test 2: Проверка Health"
echo "======================================"
curl -s "https://embedding-service-production-4aaa.up.railway.app/health" | jq .

echo ""
echo "🧪 Test 3: Проверка Stats"
echo "======================================"
curl -s "https://embedding-service-production-4aaa.up.railway.app/stats" | jq .

echo ""
echo "🧪 Test 4: Проверка сохраненных embeddings в базе"
echo "======================================"
PGPASSWORD=ua4k2kfhzypqpqlolvtsfx382w4ravqw psql \
  -h maglev.proxy.rlwy.net -p 49800 -U postgres -d railway \
  -c "SELECT product_id, embedding_type, model_version, vector_dims(embedding) as dims, created_at FROM product_embeddings ORDER BY created_at DESC LIMIT 5;"
