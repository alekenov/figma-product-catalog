# Production API Order Endpoints - Findings

**Date**: 2025-10-20
**Investigation**: Поиск endpoint для создания заказов в Production API

---

## 🔍 Что нашли в `/api/v2/`:

### Существующие endpoints:

#### Orders (Read-only):
- ✅ `GET /api/v2/orders` - Список заказов (только активные: N, AP, CO, DE)
  - Поддерживает фильтры: `status`, `limit`, `offset`
  - Pagination included
  - Auth: `access_token` или `Authorization: Bearer`

- ✅ `GET /api/v2/orders/{id}` - Детали заказа
  - Делегируется к `/orders/detail/index.php`

- ✅ `GET /api/v2/customers/orders.php` - Заказы клиента
- ✅ `GET /api/v2/customers/orders_by_id.php` - Заказы по ID клиента

#### Order Status:
- ✅ `POST /api/v2/order/change-status/` - Изменение статуса заказа
  - Принимает: `id`, `status`
  - **Важно**: Есть только смена статуса, не создание

#### Products:
- ✅ `POST /api/v2/create/` - Создание **продуктов** (НЕ заказов!)
  - Payload: `id`, `title`, `price`, `images_urls`, `owner`, `properties`

---

## ❌ Что НЕ нашли:

### Отсутствующие endpoints:

- ❌ `POST /api/v2/orders` - Создание заказа **НЕ СУЩЕСТВУЕТ**
- ❌ `POST /api/v2/orders/create` - **НЕ НАЙДЕНО**
- ❌ `POST /api/v2/order/create` - **НЕ НАЙДЕНО**

**Вывод**: В Production API (`/api/v2/`) **нет публичного endpoint для создания заказов**.

---

## 🛠️ Возможные решения:

### Вариант 1: Создать новый endpoint (RECOMMENDED)

**Путь**: `/home/bitrix/www/api/v2/orders/create/index.php`

**Структура**:
```
/api/v2/orders/
├── index.php          # GET список заказов (существует)
├── detail/
│   └── index.php      # GET детали заказа (существует)
├── delete/
│   └── index.php      # DELETE заказ (существует)
└── create/            # ← НОВАЯ ПАПКА
    └── index.php      # POST создание заказа (СОЗДАТЬ)
```

**Endpoint**: `POST https://cvety.kz/api/v2/orders/create`

**Expected Payload**:
```json
{
  "railway_order_id": 123,
  "customer_name": "Иван Иванов",
  "customer_phone": "+77015211545",
  "delivery_address": "ул. Абая 150, кв 25",
  "delivery_date": "2025-10-21",
  "delivery_time": "14:00-16:00",
  "recipient_name": "Мария Петрова",
  "recipient_phone": "+77778889900",
  "items": [
    {"product_id": 5, "quantity": 1, "price": 15000}
  ],
  "total_amount": 17500,
  "payment_method": "kaspi",
  "notes": "Позвонить за 10 минут"
}
```

**Implementation Template**:
```php
<?php
// POST /api/v2/orders/create
// Creates new order in Bitrix from Railway

define('NO_KEEP_STATISTIC', true);
define('NOT_CHECK_PERMISSIONS', true);
require($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_before.php');

use Bitrix\Main\Context;
use Bitrix\Main\Loader;
use Bitrix\Sale\Order;
use Bitrix\Sale\Basket;

header('Content-Type: application/json; charset=UTF-8');
header("Access-Control-Allow-Origin: *");

// Validate token
$token = $_GET['access_token'] ?? '';
if ($token !== 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144') {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// Parse JSON payload
$payload = json_decode(file_get_contents('php://input'), true);

if (!Loader::includeModule('sale')) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Sale module unavailable']);
    exit;
}

// Create order
$order = Order::create(SITE_ID, $payload['customer_phone']);
$order->setPersonTypeId(1); // Physical person

// Add products to basket
$basket = $order->getBasket();
foreach ($payload['items'] as $item) {
    $basketItem = $basket->createItem('catalog', $item['product_id']);
    $basketItem->setField('QUANTITY', $item['quantity']);
    $basketItem->setField('PRICE', $item['price']);
}

// Set delivery
$shipmentCollection = $order->getShipmentCollection();
$shipment = $shipmentCollection->createItem();
$shipment->setField('DELIVERY_ID', 1); // Your delivery service ID

// Set order properties
$propertyCollection = $order->getPropertyCollection();

// Address
$addressProp = $propertyCollection->getAddress();
if ($addressProp) {
    $addressProp->setValue($payload['delivery_address']);
}

// Delivery date/time
$dateProp = $propertyCollection->getItemByOrderPropertyCode('DELIVERY_DATE');
if ($dateProp) {
    $dateProp->setValue($payload['delivery_date']);
}

$timeProp = $propertyCollection->getItemByOrderPropertyCode('DELIVERY_TIME');
if ($timeProp) {
    $timeProp->setValue($payload['delivery_time']);
}

// Recipient info
$recipientNameProp = $propertyCollection->getItemByOrderPropertyCode('RECIPIENT_NAME');
if ($recipientNameProp) {
    $recipientNameProp->setValue($payload['recipient_name']);
}

// Store Railway order ID for reference
$railwayIdProp = $propertyCollection->getItemByOrderPropertyCode('RAILWAY_ORDER_ID');
if ($railwayIdProp) {
    $railwayIdProp->setValue($payload['railway_order_id']);
}

// Save order
$result = $order->save();

if ($result->isSuccess()) {
    echo json_encode([
        'success' => true,
        'bitrix_order_id' => $order->getId(),
        'railway_order_id' => $payload['railway_order_id'],
        'order_number' => $order->getId()
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'errors' => $result->getErrorMessages()
    ]);
}
```

**Необходимые действия**:
1. Создать папку `/home/bitrix/www/api/v2/orders/create/`
2. Создать файл `index.php` с кодом выше
3. Настроить DELIVERY_ID (ID службы доставки в Bitrix)
4. Добавить кастомные поля заказа:
   - `RAILWAY_ORDER_ID` - для связи с Railway
   - `DELIVERY_DATE`, `DELIVERY_TIME` - если не существует
   - `RECIPIENT_NAME`, `RECIPIENT_PHONE` - информация о получателе

---

### Вариант 2: Использовать Bitrix REST API

**Endpoint**: `POST https://cvety.kz/rest/sale.order.add`

**Pros**:
- Не нужно писать PHP код
- Официальный Bitrix API
- Автоматическая валидация

**Cons**:
- Требует настройки REST API ключей
- Более сложная авторизация (webhooks или OAuth)
- Не все поля могут быть доступны

**Проверить доступность**:
```bash
curl https://cvety.kz/rest/sale.order.add
```

---

### Вариант 3: Webhook от Railway к существующему CRM

Если в Bitrix есть интеграция с внешними заказами (например, через интернет-магазин), можно использовать существующий механизм.

**Проверить**:
- Есть ли в Bitrix обработчик для внешних заказов?
- Используется ли webhook для синхронизации с Telegram/WhatsApp?

---

## 📝 Рекомендация:

**Вариант 1 (создать endpoint)** - самое простое и надёжное решение:

1. ✅ Полный контроль над структурой данных
2. ✅ Аналогичен существующему `/api/v2/create` для продуктов
3. ✅ Легко тестировать и отлаживать
4. ✅ Минимум зависимостей

**Время реализации**: 1-2 дня разработки + тестирование

---

## 🧪 Тестирование нового endpoint:

После создания, проверить:

```bash
# 1. Создать заказ
curl -X POST "https://cvety.kz/api/v2/orders/create?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  -H "Content-Type: application/json" \
  -d '{
    "railway_order_id": 999,
    "customer_name": "Test User",
    "customer_phone": "+77015211545",
    "delivery_address": "Test Address",
    "delivery_date": "2025-10-21",
    "delivery_time": "14:00-16:00",
    "items": [{"product_id": 5, "quantity": 1, "price": 15000}],
    "total_amount": 15000
  }'

# 2. Проверить созданный заказ
curl "https://cvety.kz/api/v2/orders?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&limit=1"

# 3. Проверить детали
curl "https://cvety.kz/api/v2/orders/{NEW_ORDER_ID}?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"
```

---

**Prepared by**: Claude Code  
**Date**: October 20, 2025  
**Status**: Investigation Complete, Implementation Needed
