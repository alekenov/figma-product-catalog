#!/bin/bash
# Sync ready bouquets from Production to Railway via webhook
# Date: 2025-10-20

set -e

RAILWAY_URL="https://figma-product-catalog-production.up.railway.app"
WEBHOOK_SECRET="cvety-webhook-2025-secure-key"
CVETY_API="https://cvety.kz/api/v2/products"
ACCESS_TOKEN="ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"

# IDs готовых букетов
READY_BOUQUET_IDS=(698868 698871 698872 698874 698875 698876 698877 698878 698879 698882 698883)

echo "========================================="
echo "СИНХРОНИЗАЦИЯ ГОТОВЫХ БУКЕТОВ"
echo "Production → Railway → Visual Search"
echo "========================================="
echo ""
echo "Всего букетов для синхронизации: ${#READY_BOUQUET_IDS[@]}"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for i in "${!READY_BOUQUET_IDS[@]}"; do
    PRODUCT_ID="${READY_BOUQUET_IDS[$i]}"
    INDEX=$((i + 1))

    echo "[$INDEX/${#READY_BOUQUET_IDS[@]}] Синхронизация букета ID $PRODUCT_ID..."

    # Step 1: Get product data from Production API
    echo "   Получение данных из Production API..."
    PRODUCT_DATA=$(curl -s "$CVETY_API/?access_token=$ACCESS_TOKEN&id=$PRODUCT_ID" | \
        python3 -c "import sys, json; data = json.load(sys.stdin); print(json.dumps(data['data'][0]) if data.get('data') else '{}')")

    if [ -z "$PRODUCT_DATA" ] || [ "$PRODUCT_DATA" = "{}" ]; then
        echo "   ❌ Товар не найден в Production API"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo ""
        continue
    fi

    # Step 2: Send to Railway webhook
    echo "   Отправка webhook в Railway..."
    WEBHOOK_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
        "$RAILWAY_URL/api/v1/webhooks/product-sync" \
        -H "Content-Type: application/json" \
        -H "X-Webhook-Secret: $WEBHOOK_SECRET" \
        -d "{\"event_type\": \"product.created\", \"product_data\": $PRODUCT_DATA}")

    HTTP_CODE=$(echo "$WEBHOOK_RESPONSE" | grep HTTP_CODE | cut -d: -f2)

    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ SUCCESS - товар создан в Railway БД"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ❌ FAILED (HTTP $HTTP_CODE)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""

    # Пауза 1 секунда между запросами
    if [ $INDEX -lt ${#READY_BOUQUET_IDS[@]} ]; then
        sleep 1
    fi
done

echo "========================================="
echo "ИТОГИ СИНХРОНИЗАЦИИ"
echo "========================================="
echo "Успешно синхронизировано: $SUCCESS_COUNT"
echo "Ошибок: $FAIL_COUNT"
echo ""

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo "✅ Товары синхронизированы в Railway БД!"
    echo ""
    echo "Следующий шаг: Запустить индексацию"
    echo "./reindex-ready-bouquets.sh"
else
    echo "❌ Синхронизация не удалась. Проверьте логи выше."
fi
echo ""
