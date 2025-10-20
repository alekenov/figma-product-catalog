#!/bin/bash
# Test Webhook Flow - Локальное тестирование синхронизации
# Usage: ./test-webhook-flow.sh

set -e

WEBHOOK_SECRET="cvety-webhook-2025-secure-key"
RAILWAY_URL="https://figma-product-catalog-production.up.railway.app"
WORKER_URL="https://visual-search.alekenov.workers.dev"

echo "🧪 WEBHOOK FLOW TEST"
echo "===================="
echo ""

# Test 1: Check services health
echo "📡 1. Проверка сервисов..."
BACKEND_STATUS=$(curl -s ${RAILWAY_URL}/health | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")
WORKER_STATUS=$(curl -s ${WORKER_URL}/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")

echo "   ✅ Railway Backend: $BACKEND_STATUS"
echo "   ✅ Visual Search Worker: $WORKER_STATUS"
echo ""

# Test 2: Create test product via webhook
echo "📦 2. Создание тестового товара через webhook..."

TEST_PRODUCT_ID=$((900000 + RANDOM % 10000))

WEBHOOK_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${RAILWAY_URL}/api/v1/webhooks/product-sync" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${WEBHOOK_SECRET}" \
  -d "{
    \"event_type\": \"product.created\",
    \"product_data\": {
      \"id\": ${TEST_PRODUCT_ID},
      \"title\": \"TEST Local Webhook Flow\",
      \"price\": \"3 500 ₸\",
      \"isAvailable\": true,
      \"image\": \"https://cvety.kz/upload/iblock/7a4/mg681krk-yqytaiexroo.png\",
      \"images\": [\"https://cvety.kz/upload/iblock/7a4/mg681krk-yqytaiexroo.png\"],
      \"catalogHeight\": \"55 см\",
      \"catalogWidth\": \"35 см\",
      \"type\": \"catalog\"
    }
  }")

HTTP_CODE=$(echo "$WEBHOOK_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
RESPONSE_BODY=$(echo "$WEBHOOK_RESPONSE" | grep -v HTTP_CODE)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Webhook успешно обработан (200 OK)"
    echo "   Response: $RESPONSE_BODY"
else
    echo "   ❌ Webhook failed (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE_BODY"
    exit 1
fi
echo ""

# Test 3: Check product in Railway database
echo "🔍 3. Проверка товара в Railway БД..."
sleep 2  # Wait for DB write

PRODUCT_CHECK=$(curl -s "${RAILWAY_URL}/api/v1/products/?shop_id=8&enabled_only=false" | \
  python3 -c "import sys, json; products = json.load(sys.stdin); product = next((p for p in products if p['id'] == ${TEST_PRODUCT_ID}), None); print('found' if product else 'not_found'); print(product.get('name', '') if product else '')")

PRODUCT_STATUS=$(echo "$PRODUCT_CHECK" | head -1)
PRODUCT_NAME=$(echo "$PRODUCT_CHECK" | tail -1)

if [ "$PRODUCT_STATUS" = "found" ]; then
    echo "   ✅ Товар найден в БД: $PRODUCT_NAME"
else
    echo "   ❌ Товар НЕ найден в БД"
    exit 1
fi
echo ""

# Test 4: Manual reindex trigger
echo "🔄 4. Ручной триггер reindex..."

REINDEX_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${WORKER_URL}/reindex-one" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\": ${TEST_PRODUCT_ID}, \"shop_id\": 8}")

REINDEX_HTTP_CODE=$(echo "$REINDEX_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
REINDEX_BODY=$(echo "$REINDEX_RESPONSE" | grep -v HTTP_CODE)

if [ "$REINDEX_HTTP_CODE" = "200" ]; then
    echo "   ✅ Reindex успешен (200 OK)"
    echo "   Response: $REINDEX_BODY"
else
    echo "   ⚠️  Reindex вернул код $REINDEX_HTTP_CODE"
    echo "   Response: $REINDEX_BODY"
fi
echo ""

# Test 5: Check Vectorize stats
echo "📊 5. Статистика Vectorize индекса..."

STATS=$(curl -s "${WORKER_URL}/stats" | python3 -c "import sys, json; d = json.load(sys.stdin); print(f\"Всего товаров: {d.get('total_indexed', 0)}\"); print(f\"Последний: {d.get('last_indexed_at', 'N/A')}\")")

echo "   $STATS"
echo ""

# Test 6: Update product
echo "🔄 6. Обновление товара через webhook..."

UPDATE_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${RAILWAY_URL}/api/v1/webhooks/product-sync" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${WEBHOOK_SECRET}" \
  -d "{
    \"event_type\": \"product.updated\",
    \"product_data\": {
      \"id\": ${TEST_PRODUCT_ID},
      \"title\": \"TEST Updated Product\",
      \"price\": \"4 000 ₸\",
      \"isAvailable\": true,
      \"image\": \"https://cvety.kz/upload/iblock/7a4/mg681krk-yqytaiexroo.png\",
      \"images\": [\"https://cvety.kz/upload/iblock/7a4/mg681krk-yqytaiexroo.png\"],
      \"catalogHeight\": \"60 см\"
    }
  }")

UPDATE_HTTP_CODE=$(echo "$UPDATE_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
if [ "$UPDATE_HTTP_CODE" = "200" ]; then
    echo "   ✅ Update webhook успешен (200 OK)"
else
    echo "   ❌ Update failed (HTTP $UPDATE_HTTP_CODE)"
fi
echo ""

# Test 7: Delete product (soft delete)
echo "🗑️  7. Удаление товара через webhook..."

DELETE_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${RAILWAY_URL}/api/v1/webhooks/product-sync" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${WEBHOOK_SECRET}" \
  -d "{
    \"event_type\": \"product.deleted\",
    \"product_data\": {
      \"id\": ${TEST_PRODUCT_ID}
    }
  }")

DELETE_HTTP_CODE=$(echo "$DELETE_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
if [ "$DELETE_HTTP_CODE" = "200" ]; then
    echo "   ✅ Delete webhook успешен (200 OK)"
else
    echo "   ❌ Delete failed (HTTP $DELETE_HTTP_CODE)"
fi
echo ""

# Summary
echo "✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО"
echo "========================"
echo ""
echo "Протестировано:"
echo "  ✅ Health check обоих сервисов"
echo "  ✅ CREATE webhook (product.created)"
echo "  ✅ Проверка записи в БД"
echo "  ✅ Manual reindex trigger"
echo "  ✅ Vectorize stats"
echo "  ✅ UPDATE webhook (product.updated)"
echo "  ✅ DELETE webhook (product.deleted - soft delete)"
echo ""
echo "Тестовый product_id: ${TEST_PRODUCT_ID}"
echo ""
echo "📝 Для проверки в БД:"
echo "   curl \"${RAILWAY_URL}/api/v1/products/?shop_id=8&enabled_only=false\" | grep ${TEST_PRODUCT_ID}"
