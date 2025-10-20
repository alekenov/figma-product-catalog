# Bitrix Event Handler для синхронизации с Railway

## Назначение

Автоматическая синхронизация товаров из Production Bitrix (cvety.kz) в Railway backend при создании/обновлении/удалении товаров.

## Установка

### 1. SSH на Production сервер

```bash
ssh root@185.125.90.141
```

### 2. Создать/редактировать init.php

```bash
nano /home/bitrix/www/local/php_interface/init.php
```

### 3. Добавить следующий код

```php
<?php
// Railway Webhook Configuration
define('RAILWAY_WEBHOOK_URL', 'https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/product-sync');
define('RAILWAY_WEBHOOK_SECRET', 'production-secret-change-me');  // ВАЖНО: изменить на production

// Bitrix Event Handlers
AddEventHandler("iblock", "OnAfterIBlockElementAdd", "syncProductToRailway");
AddEventHandler("iblock", "OnAfterIBlockElementUpdate", "syncProductToRailway");
AddEventHandler("iblock", "OnAfterIBlockElementDelete", "deleteProductFromRailway");

/**
 * Sync product to Railway when created/updated
 */
function syncProductToRailway($arFields) {
    // Get product ID
    $productId = $arFields['ID'];

    // Fetch full product data via Bitrix API
    $apiUrl = "https://cvety.kz/api/v2/products?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&id=" . $productId;

    $ch = curl_init($apiUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    if (!empty($data['data'][0])) {
        $product = $data['data'][0];

        // Determine event type
        $eventType = isset($arFields['IBLOCK_SECTION_ID']) && $arFields['IBLOCK_SECTION_ID'] ? 'product.updated' : 'product.created';

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

        // Log result
        if ($httpCode == 200) {
            error_log("Railway sync success for product $productId");
        } else {
            error_log("Railway sync failed for product $productId: HTTP $httpCode");
        }
    }
}

/**
 * Sync product deletion to Railway
 */
function deleteProductFromRailway($arFields) {
    $productId = $arFields['ID'];

    // Send deletion webhook
    $webhookData = [
        'event_type' => 'product.deleted',
        'product_data' => [
            'id' => $productId
        ]
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

### 4. Настроить WEBHOOK_SECRET

В Railway backend добавить environment variable:

```bash
railway variables --set WEBHOOK_SECRET=production-secret-change-me
```

### 5. Перезагрузить Bitrix

```bash
systemctl restart php-fpm
systemctl restart nginx
```

## Тестирование

### 1. Создать тестовый товар в Bitrix админке

1. Зайти в админку Bitrix
2. Создать новый товар
3. Проверить логи:

```bash
tail -f /var/log/bitrix-error.log | grep Railway
```

### 2. Проверить в Railway

```bash
# Railway logs
railway logs --service figma-product-catalog | grep webhook

# SQL query
SELECT * FROM product WHERE id = <product_id>;
```

## Troubleshooting

### Webhook не вызывается

1. Проверить что init.php загружен:
   ```bash
   php -r 'include "/home/bitrix/www/local/php_interface/init.php"; echo "OK\n";'
   ```

2. Проверить логи Bitrix:
   ```bash
   tail -100 /var/log/bitrix-error.log
   ```

### Ошибка 401 Unauthorized

- Проверить что `RAILWAY_WEBHOOK_SECRET` совпадает в обоих местах
- Railway: `railway variables --kv | grep WEBHOOK_SECRET`
- Bitrix: посмотреть в `init.php`

### Ошибка 500 в webhook

- Проверить логи Railway: `railway logs`
- Проверить формат JSON payload
- Протестировать локально с curl

## Мониторинг

Добавить в cron проверку синхронизации:

```bash
# /etc/cron.d/railway-sync-check
*/5 * * * * root /usr/bin/php /home/bitrix/www/local/scripts/check_railway_sync.php
```

## Безопасность

- ✅ Webhook secret для авторизации
- ✅ HTTPS только
- ✅ Логирование всех запросов
- ⚠️ Rate limiting (TODO: добавить в Railway endpoint)

---

**Created:** 2025-10-20
**Last Updated:** 2025-10-20
**Status:** Ready for Production
