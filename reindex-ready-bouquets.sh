#!/bin/bash
# Reindex ready bouquets from vitrina
# Date: 2025-10-20

set -e

WORKER_URL="https://visual-search.alekenov.workers.dev"
SHOP_ID=8

# IDs готовых букетов с фото
READY_BOUQUET_IDS=(698868 698871 698872 698874 698875 698876 698877 698878 698879 698882 698883)

echo "========================================="
echo "ИНДЕКСАЦИЯ ГОТОВЫХ БУКЕТОВ ИЗ ВИТРИНЫ"
echo "========================================="
echo ""
echo "Всего букетов для индексации: ${#READY_BOUQUET_IDS[@]}"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for i in "${!READY_BOUQUET_IDS[@]}"; do
    PRODUCT_ID="${READY_BOUQUET_IDS[$i]}"
    INDEX=$((i + 1))

    echo "[$INDEX/${#READY_BOUQUET_IDS[@]}] Индексация букета ID $PRODUCT_ID..."

    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
        "$WORKER_URL/reindex-one" \
        -H "Content-Type: application/json" \
        -d "{\"product_id\": $PRODUCT_ID, \"shop_id\": $SHOP_ID}")

    HTTP_CODE=$(echo "$RESPONSE" | grep HTTP_CODE | cut -d: -f2)
    BODY=$(echo "$RESPONSE" | grep -v HTTP_CODE)

    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ SUCCESS (200 OK)"
        SUCCESS=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Success:' if d.get('success') else 'Failed:', d.get('reason', d.get('indexed_at', '')))")
        echo "   $SUCCESS"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ❌ FAILED (HTTP $HTTP_CODE)"
        echo "   Response: $BODY"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""

    # Пауза 2 секунды между запросами
    if [ $INDEX -lt ${#READY_BOUQUET_IDS[@]} ]; then
        sleep 2
    fi
done

echo "========================================="
echo "ИТОГИ ИНДЕКСАЦИИ"
echo "========================================="
echo "Успешно проиндексировано: $SUCCESS_COUNT"
echo "Ошибок: $FAIL_COUNT"
echo ""

# Проверка Vectorize stats
echo "Проверка Vectorize статистики..."
STATS=$(curl -s "$WORKER_URL/stats")
echo "$STATS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Всего проиндексировано: {data.get(\"total_indexed\", 0)}')
    print(f'Последняя индексация: {data.get(\"last_indexed_at\", \"N/A\")}')
except:
    print('Ошибка получения статистики')
"
echo ""

echo "✅ Индексация завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Проверить логи Cloudflare Worker"
echo "2. Протестировать визуальный поиск:"
echo "   curl -X POST \"$WORKER_URL/search\" -F \"image=@/path/to/bouquet.jpg\""
echo ""
