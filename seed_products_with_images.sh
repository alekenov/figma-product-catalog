#!/bin/bash

echo "🌸 Добавляем продукты с реальными изображениями из Production..."
echo ""

# Webhook secret
SECRET="cvety-webhook-2025-secure-key"
URL="https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/product-sync"

# Функция для создания продукта
create_product() {
  local id=$1
  local title=$2
  local price=$3
  local image=$4

  echo "📦 Создаю: $title (ID: $id)"

  curl -X POST "$URL" \
    -H "Content-Type: application/json" \
    -H "X-Webhook-Secret: $SECRET" \
    -d "{
      \"event_type\": \"product.created\",
      \"product_data\": {
        \"id\": $id,
        \"title\": \"$title\",
        \"price\": $price,
        \"isAvailable\": true,
        \"image\": \"$image\",
        \"images\": [\"$image\"],
        \"catalogHeight\": 40,
        \"catalogWidth\": 30,
        \"type\": \"catalog\"
      }
    }" | jq -r '.status, .embedding_generated'

  echo ""
  sleep 3  # Даем время на обработку embedding
}

# Добавляем 5 продуктов с разными изображениями
echo "Используем изображения из Cloudflare R2..."
echo ""

create_product 100001 "Букет роз красные" 25000 "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png"
create_product 100002 "Букет тюльпанов" 18000 "https://flower-shop-images.alekenov.workers.dev/mg67xybu-q7yboowkco.png"
create_product 100003 "Букет пионов" 35000 "https://flower-shop-images.alekenov.workers.dev/mg681krk-yqytaiexroo.png"

echo ""
echo "✅ Продукты добавлены! Проверяем embeddings..."
echo ""

# Проверяем сколько embeddings создалось
sleep 10

PGPASSWORD=ua4k2kfhzypqpqlolvtsfx382w4ravqw psql \
  -h maglev.proxy.rlwy.net -p 49800 -U postgres -d railway \
  -c "SELECT COUNT(*) as total_embeddings FROM product_embeddings;"

echo ""
echo "🎉 Готово! Теперь можно тестировать Visual Search с несколькими продуктами"
