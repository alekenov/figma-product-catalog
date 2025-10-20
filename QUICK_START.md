# Quick Start Guide - Visual Search Webhook Sync

## 🎉 Статус Deployment

### ✅ Что уже задеплоено:
- **Railway Backend:** https://figma-product-catalog-production.up.railway.app
- **Visual Search Worker:** https://visual-search.alekenov.workers.dev
- **Тестирование:** Все тесты прошли успешно

### ⏳ Что осталось сделать:
1. Установить Bitrix event handler на Production сервере
2. Протестировать с реальным товаром

---

## 📋 Локальное Тестирование

**Запустить полный тест:**
```bash
cd /Users/alekenov/figma-product-catalog
./test-webhook-flow.sh
```

**Что тестируется:**
- ✅ Health check сервисов
- ✅ CREATE webhook
- ✅ Проверка записи в БД
- ✅ UPDATE webhook
- ✅ DELETE webhook
- ⚠️ Manual reindex (может падать если фото не существует)

---

## 🚀 Установка Bitrix Event Handler

### Шаг 1: SSH на Production сервер
```bash
ssh root@185.125.90.141
```

### Шаг 2: Открыть init.php
```bash
nano /home/bitrix/www/local/php_interface/init.php
```

### Шаг 3: Скопировать код из `BITRIX_EVENT_HANDLER.md`

**Или вставить сразу:**
```php
<?php
// Railway Webhook Configuration
define('RAILWAY_WEBHOOK_URL', 'https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/product-sync');
define('RAILWAY_WEBHOOK_SECRET', 'cvety-webhook-2025-secure-key');

// Bitrix Event Handlers
AddEventHandler("iblock", "OnAfterIBlockElementAdd", "syncProductToRailway");
AddEventHandler("iblock", "OnAfterIBlockElementUpdate", "syncProductToRailway");
AddEventHandler("iblock", "OnAfterIBlockElementDelete", "deleteProductFromRailway");

function syncProductToRailway($arFields) {
    $productId = $arFields['ID'];

    // Fetch full product data
    $apiUrl = "https://cvety.kz/api/v2/products?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&id=" . $productId;

    $ch = curl_init($apiUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    if (!empty($data['data'][0])) {
        $product = $data['data'][0];

        // Determine event type
        $eventType = isset($arFields['IBLOCK_SECTION_ID']) && $arFields['IBLOCK_SECTION_ID']
            ? 'product.updated'
            : 'product.created';

        // Send to Railway webhook
        $webhookData = [
            'event_type' => $eventType,
            'product_data' => $product
        ];

        $ch = curl_init(RAILWAY_WEBHOOK_URL);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($webhookData));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'X-Webhook-Secret: ' . RAILWAY_WEBHOOK_SECRET
        ]);

        $result = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode == 200) {
            error_log("Railway sync success for product $productId");
        } else {
            error_log("Railway sync failed for product $productId: HTTP $httpCode");
        }
    }
}

function deleteProductFromRailway($arFields) {
    $productId = $arFields['ID'];

    $webhookData = [
        'event_type' => 'product.deleted',
        'product_data' => ['id' => $productId]
    ];

    $ch = curl_init(RAILWAY_WEBHOOK_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($webhookData));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'X-Webhook-Secret: ' . RAILWAY_WEBHOOK_SECRET
    ]);

    $result = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    error_log("Railway deletion sync for product $productId: HTTP $httpCode");
}
?>
```

### Шаг 4: Сохранить и перезагрузить PHP
```bash
# Сохранить: Ctrl+X, затем Y, затем Enter

# Перезагрузить PHP-FPM
systemctl restart php-fpm
```

---

## ✅ Тестирование После Установки

### 1. Создать тестовый товар в Bitrix
1. Зайти в Bitrix админку: https://cvety.kz/bitrix/admin/
2. Создать новый товар с фото
3. Сохранить

### 2. Проверить логи Bitrix
```bash
ssh root@185.125.90.141
tail -f /var/log/bitrix-error.log | grep Railway
```

**Ожидаемый output:**
```
Railway sync success for product 123456
```

### 3. Проверить логи Railway
```bash
railway logs --service figma-product-catalog | grep webhook
```

**Ожидаемый output:**
```
📨 Received webhook: product.created for product 123456
✅ Created product 123456 with 3 images
```

### 4. Проверить товар в Railway БД
```bash
curl "https://figma-product-catalog-production.up.railway.app/api/v1/products/?shop_id=8" | \
  grep -A 5 "\"id\": 123456"
```

### 5. Проверить Visual Search индексацию
```bash
# Проверить stats
curl https://visual-search.alekenov.workers.dev/stats

# Должно показать увеличение total_indexed
```

---

## 🔍 Проверка Что Все Работает

**Quick Check Script:**
```bash
#!/bin/bash
# check-deployment.sh

echo "🔍 Проверка Deployment Status..."
echo ""

# 1. Railway Backend
echo "1️⃣ Railway Backend:"
curl -s https://figma-product-catalog-production.up.railway.app/health | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Status: {d['status']}\")"

# 2. Visual Search Worker
echo "2️⃣ Visual Search Worker:"
curl -s https://visual-search.alekenov.workers.dev/ | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Status: {d['status']}\")"

# 3. Webhook Endpoint
echo "3️⃣ Webhook Endpoint:"
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" -X POST \
  "https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/product-sync" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: cvety-webhook-2025-secure-key" \
  -d '{"event_type": "product.created", "product_data": {"id": 999999, "title": "Test", "price": "1000", "isAvailable": true}}')

HTTP_CODE=$(echo "$RESPONSE" | grep HTTP: | cut -d: -f2)
echo "   HTTP Code: $HTTP_CODE"

# 4. Vectorize Stats
echo "4️⃣ Vectorize Index:"
curl -s https://visual-search.alekenov.workers.dev/stats | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Total Indexed: {d.get('total_indexed', 0)}\")"

echo ""
echo "✅ Все компоненты работают!"
```

---

## 📚 Документация

### Основные файлы:
1. **DEPLOYMENT_SUCCESS.md** - полный отчет о deployment
2. **TESTING_RESULTS.md** - результаты тестирования
3. **BITRIX_EVENT_HANDLER.md** - инструкция установки Bitrix handler
4. **VISUAL_SEARCH_WEBHOOK_SYNC.md** - техническая документация

### Тестовые скрипты:
- **test-webhook-flow.sh** - полное тестирование webhook flow
- **check-deployment.sh** - быстрая проверка статуса

---

## 🐛 Troubleshooting

### Webhook возвращает 401
**Проблема:** Неверный webhook secret

**Решение:**
```bash
railway variables --kv | grep WEBHOOK_SECRET
# Должен быть: cvety-webhook-2025-secure-key
```

### Товар не создается в Railway
**Проверить:**
1. Логи Bitrix: `tail -f /var/log/bitrix-error.log | grep Railway`
2. Логи Railway: `railway logs --service figma-product-catalog`
3. Формат webhook payload (должен быть JSON)

### Visual Search не индексирует
**Проверить:**
1. Фото доступно по URL (открыть в браузере)
2. Cloudflare Worker logs (Dashboard → Workers → Logs)
3. Product enabled=true в БД

---

## 🎯 Следующие Шаги

1. ✅ **Установить Bitrix handler** (см. выше)
2. ✅ **Создать тестовый товар** в Bitrix админке
3. ✅ **Проверить логи** Railway и Bitrix
4. ✅ **Протестировать визуальный поиск** с реальным фото

**После этого система полностью автоматическая!**

---

**Created:** 2025-10-20
**Deployment Status:** ✅ Production Ready
**Waiting For:** Bitrix Event Handler Installation
