# Bitrix Webhook Setup для синхронизации статусов заказов

## Задача
Настроить автоматическую отправку уведомлений из Bitrix в Railway при изменении статуса заказа.

**Production Bitrix:** cvety.kz (shop_id=17008)
**Railway API:** https://figma-product-catalog-production.up.railway.app

---

## Шаг 1: Добавить Event Handler в Bitrix

Отредактируйте или создайте файл:
```
/home/bitrix/www/local/php_interface/init.php
```

Добавьте следующий код:

```php
<?php
// Webhook for order status changes
// Send notifications to Railway backend when order status changes

if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED !== true) {
    die();
}

use Bitrix\Main\EventManager;
use Bitrix\Sale\OrderStatus;

// Register event handler for order status changes
EventManager::getInstance()->registerEventHandler(
    "sale",
    "OnSaleStatusOrderChange",
    "cvety_modules",
    "CvetyOrderStatusWebhook",
    "onOrderStatusChange"
);

class CvetyOrderStatusWebhook
{
    /**
     * Send order status update to Railway backend
     *
     * @param int $orderId - Order ID in Bitrix
     * @param string $oldStatus - Previous status
     * @param string $newStatus - New status
     * @return bool
     */
    public static function onOrderStatusChange($orderId, $oldStatus, $newStatus)
    {
        global $USER;

        // Don't send webhook for test orders
        if ($orderId <= 0) {
            return true;
        }

        // Railway webhook configuration
        $railwayUrl = "https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/order-status-sync";
        $webhookSecret = "YOUR_WEBHOOK_SECRET_HERE";  // Replace with actual secret from Railway env
        $currentUserId = $USER->GetID();

        // Prepare webhook payload
        $payload = [
            "order_id" => (int)$orderId,
            "status" => (string)$newStatus,
            "changed_by_id" => (int)$currentUserId,
            "notes" => "Status changed in Bitrix: {$oldStatus} → {$newStatus}"
        ];

        // Send webhook via curl
        $ch = curl_init($railwayUrl);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            "Content-Type: application/json",
            "X-Webhook-Secret: {$webhookSecret}"
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        // Log webhook activity
        if ($httpCode >= 200 && $httpCode < 300) {
            error_log("[Railway Webhook] ✅ Order {$orderId} status synced: {$newStatus}");
            return true;
        } else {
            error_log("[Railway Webhook] ❌ Failed to sync order {$orderId} (HTTP {$httpCode}): {$response}");
            return false;  // Don't fail order status change if webhook fails
        }
    }
}
```

---

## Шаг 2: Получить WEBHOOK_SECRET

Значение `YOUR_WEBHOOK_SECRET_HERE` должно совпадать с `WEBHOOK_SECRET` в Railway:

```bash
# Get current Railway webhook secret:
railway variables --kv | grep WEBHOOK_SECRET
```

**Пример:**
```
WEBHOOK_SECRET=super-secret-key-12345
```

Скопируйте это значение и замените в PHP коде выше.

---

## Шаг 3: Протестировать

### На Production Bitrix:
1. Откройте заказ (например, #123456)
2. Измените статус, например: `Новый (N)` → `Принят (AP)`
3. Сохраните заказ

### На Railway:
Проверьте логи:
```bash
railway logs --deploy | grep "order-status-sync"
```

Ожидаемый результат:
```
INFO: Received order status webhook: order_id=123456, status=AP
INFO: Updated order 789 (bitrix_id=123456): new → accepted
```

---

## Шаг 4: Проверить в Railway Backend

Получите заказ из API и проверьте статус:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://figma-product-catalog-production.up.railway.app/api/v1/orders/789

# Response должен содержать:
# "status": "accepted"
```

Проверьте историю изменений:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://figma-product-catalog-production.up.railway.app/api/v1/orders/789/history

# Response должен содержать запись:
# {
#   "field_name": "status",
#   "old_value": "new",
#   "new_value": "accepted",
#   "changed_by": "bitrix",
#   "changed_at": "2025-10-24T15:30:00Z"
# }
```

---

## Маппинг статусов

Статусы автоматически конвертируются:

| Bitrix | Railway | Описание |
|--------|---------|----------|
| N | new | Новый заказ |
| PD | paid | Оплачен |
| AP | accepted | Принят флористом |
| CO | in_production | В процессе сборки |
| DE | in_delivery | В доставке |
| F | delivered | Доставлен |
| RF | cancelled | Возврат |
| UN | cancelled | Не реализован |

---

## Troubleshooting

### Webhook не срабатывает

1. **Проверьте init.php:**
   ```bash
   grep -n "CvetyOrderStatusWebhook" /home/bitrix/www/local/php_interface/init.php
   ```

2. **Проверьте логи Bitrix:**
   ```bash
   tail -f /home/bitrix/www/bitrix/logs/error_log
   ```

3. **Проверьте WEBHOOK_SECRET:**
   ```bash
   railway variables --kv | grep WEBHOOK_SECRET
   # Убедитесь что значение совпадает в init.php
   ```

### Webhook отправляется но не обрабатывается

1. **Проверьте лог Railway:**
   ```bash
   railway logs --deploy --filter "@level:error" | grep webhook
   ```

2. **Проверьте HTTP статус код:**
   - 401 = Неверный WEBHOOK_SECRET
   - 404 = Заказ не найден (bitrix_order_id не установлен)
   - 500 = Ошибка на Railway

3. **Вручную отправьте тестовый webhook:**
   ```bash
   curl -X POST \
     https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/order-status-sync \
     -H "Content-Type: application/json" \
     -H "X-Webhook-Secret: $(railway variables --kv | grep WEBHOOK_SECRET | cut -d= -f2)" \
     -d '{
       "order_id": 123456,
       "status": "AP",
       "changed_by_id": 42,
       "notes": "Test webhook"
     }'
   ```

---

## Отладка: Увидеть все webhook запросы

Добавьте в init.php логирование всех webhook запросов:

```php
error_log("[Railway Webhook] Sending: " . json_encode($payload));
error_log("[Railway Webhook] Response ({$httpCode}): " . substr($response, 0, 200));
```

Затем смотрите логи:
```bash
tail -f /home/bitrix/www/bitrix/logs/error_log | grep "Railway Webhook"
```

---

## Что дальше?

После успешной настройки webhook'а для статусов:

1. ✅ Railway получает обновления статусов из Bitrix
2. ⏳ Следующий этап: создать endpoint в Bitrix для приема обновлений товаров из Railway
3. ⏳ Затем: Интегрировать BitrixSyncService в product update flow

---

## Контакты

- **Railway API:** https://figma-product-catalog-production.up.railway.app
- **Production Bitrix:** https://cvety.kz
- **Webhook Endpoint:** POST `/api/v1/webhooks/order-status-sync`
- **Webhook Authentication:** Header `X-Webhook-Secret`
