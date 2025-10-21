# Production API Integration Plan
# Полный цикл работы клиента через Telegram Bot

**Дата**: 2025-10-20
**Цель**: Обеспечить полный цикл работы клиента - от поиска букета до оплаты заказа
**Системы**: Production API (cvety.kz) + Railway Backend + Telegram Bot

---

## 🎯 Требуемый Customer Journey

```
1. Клиент ищет букет 
   ├─ По фото (визуальный поиск)
   └─ По каталогу (текстовый поиск)
   
2. Клиент выбирает букет
   └─ Видит цену, описание, фото
   
3. Клиент оформляет заказ
   ├─ Указывает адрес доставки
   ├─ Выбирает дату/время
   └─ Указывает данные получателя
   
4. Клиент оплачивает
   └─ Kaspi Pay (основной метод в Казахстане)
   
5. Клиент отслеживает статус
   ├─ Получает уведомления
   └─ Видит фото готового букета
```

---

## 📋 PHASE 1: Синхронизация каталога продуктов

### Проблема:
- Production API имеет ~50-100 активных товаров
- Railway Backend имеет только 10 тестовых товаров
- Клиент должен видеть актуальный каталог Production

### Решение: Односторонняя синхронизация Production → Railway

#### Задача 1.1: Создать скрипт импорта продуктов
**Приоритет**: 🔴 CRITICAL
**Срок**: 1-2 дня

**Файл**: `backend/scripts/sync_products_from_production.py`

```python
"""
Импорт продуктов из Production API в Railway PostgreSQL.

Процесс:
1. Получить все продукты из cvety.kz/api/v2/products
2. Для каждого продукта:
   - Проверить существование в Railway (по external_id)
   - Создать или обновить Product
   - Скачать изображения на Cloudflare R2
   - Создать ProductImage записи
3. Проиндексировать новые продукты в Visual Search
"""

import asyncio
import httpx
from sqlalchemy import select
from backend.models import Product, ProductImage
from backend.database import get_session

PRODUCTION_API = "https://cvety.kz/api/v2"
PRODUCTION_TOKEN = "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"

async def sync_products():
    """Sync all products from Production to Railway."""
    
    # 1. Fetch from Production
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PRODUCTION_API}/products",
            params={
                "access_token": PRODUCTION_TOKEN,
                "cityId": 2,  # Астана
                "limit": 200,
                "isAvailable": True
            }
        )
        production_products = response.json().get("data", [])
    
    # 2. Sync to Railway
    async for session in get_session():
        for p in production_products:
            # Check if exists
            existing = await session.execute(
                select(Product).where(Product.external_id == str(p["id"]))
            )
            product = existing.scalar_one_or_none()
            
            if product:
                # Update existing
                product.name = p["title"]
                product.price = parse_price(p["price"])
                product.enabled = p["isAvailable"]
            else:
                # Create new
                product = Product(
                    shop_id=8,
                    external_id=str(p["id"]),
                    name=p["title"],
                    price=parse_price(p["price"]),
                    product_type=p.get("type", "catalog"),
                    enabled=p["isAvailable"],
                    description=p.get("description", "")
                )
                session.add(product)
            
            await session.flush()
            
            # Sync images
            if p.get("images"):
                for img_url in p["images"]:
                    # Upload to R2, create ProductImage
                    await sync_product_image(session, product.id, img_url)
        
        await session.commit()

def parse_price(price_str: str) -> int:
    """Convert '17 820 ₸' to 1782000 kopecks."""
    cleaned = price_str.replace(" ", "").replace("₸", "")
    return int(cleaned) * 100
```

**Ожидаемый результат**:
- ✅ Railway имеет актуальный каталог из Production
- ✅ Все изображения хранятся в Cloudflare R2
- ✅ Visual search проиндексировал все продукты

---

#### Задача 1.2: Настроить регулярную синхронизацию
**Приоритет**: 🟡 MEDIUM
**Срок**: 3-4 дня

**Варианты**:

**Вариант A: Cron job на Railway**
```python
# backend/tasks/sync_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=6)
async def sync_products_job():
    """Sync products every 6 hours."""
    await sync_products_from_production()

scheduler.start()
```

**Вариант B: Webhook от Production**
```python
# Production (Bitrix) sends webhook when product changes
# backend/api/webhooks.py

@router.post("/webhooks/product-updated")
async def product_updated_webhook(
    product_id: int,
    webhook_secret: str = Header(...)
):
    """
    Called by Production when product is created/updated/deleted.
    """
    if webhook_secret != settings.webhook_secret:
        raise HTTPException(401)
    
    await sync_single_product(product_id)
```

**Рекомендация**: Начать с **Вариант A (cron)**, позже добавить **Вариант B (webhook)**

---

#### Задача 1.3: Индексация в Visual Search
**Приоритет**: 🟡 MEDIUM
**Срок**: 2-3 дня

**Процесс**:
1. После импорта каждого продукта
2. Если у продукта есть фото
3. Отправить фото в Cloudflare Visual Search Worker
4. Создать embeddings через Vertex AI

**Файл**: `backend/scripts/sync_products_from_production.py` (дополнение)

```python
async def index_product_in_visual_search(product: Product):
    """Index product images in Cloudflare Visual Search."""
    
    if not product.images:
        return
    
    primary_image = product.images[0]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://visual-search.alekenov.workers.dev/index",
            json={
                "product_id": product.id,
                "image_url": primary_image.url,
                "metadata": {
                    "title": product.name,
                    "price": product.price,
                    "shop_id": product.shop_id
                }
            }
        )
    
    logger.info(f"Indexed product {product.id} in visual search")
```

**Ожидаемый результат**:
- ✅ ~50-100 продуктов проиндексировано
- ✅ Визуальный поиск работает по всему каталогу
- ✅ Время индексации: ~2-3 минуты для всех продуктов

---

## 📋 PHASE 2: Синхронизация заказов Railway → Production

### Проблема:
- Клиент создаёт заказ через Telegram Bot → Railway
- Заказ должен появиться в Production (Bitrix CRM)
- Флорист видит заказ в Production админке

### Решение: Webhook от Railway к Production

#### Задача 2.1: Создать API endpoint в Production для приёма заказов
**Приоритет**: 🔴 CRITICAL
**Срок**: 2-3 дня
**Исполнитель**: Backend разработчик (PHP/Bitrix)

**Файл на Production**: `/home/bitrix/www/local/api/v2/orders/create.php`

```php
<?php
/**
 * Production API - Create Order from Railway
 * 
 * Endpoint: POST /api/v2/orders/create
 * Auth: access_token
 * 
 * Payload:
 * {
 *   "railway_order_id": 123,
 *   "customer_name": "+77015211545",
 *   "customer_phone": "+77015211545",
 *   "delivery_address": "...",
 *   "delivery_date": "2025-10-21",
 *   "delivery_time": "14:00-16:00",
 *   "recipient_name": "Мария",
 *   "items": [
 *     {"product_id": 5, "quantity": 1, "price": 15000}
 *   ],
 *   "total_amount": 17500
 * }
 */

require_once($_SERVER["DOCUMENT_ROOT"]."/bitrix/modules/main/include/prolog_before.php");

use Bitrix\Main\Request;
use Bitrix\Sale\Order;

// Validate access token
$request = Request::getInstance();
$token = $request->get('access_token');

if ($token !== 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144') {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

// Parse JSON payload
$payload = json_decode(file_get_contents('php://input'), true);

// Create order in Bitrix
$order = Order::create(SITE_ID, $payload['customer_phone']);
$order->setPersonTypeId(1);

// Add products
foreach ($payload['items'] as $item) {
    $basket = $order->getBasket();
    $basketItem = $basket->createItem('catalog', $item['product_id']);
    $basketItem->setField('QUANTITY', $item['quantity']);
    $basketItem->setField('PRICE', $item['price']);
}

// Set delivery
$shipmentCollection = $order->getShipmentCollection();
$shipment = $shipmentCollection->createItem();
$shipment->setField('DELIVERY_ID', DELIVERY_ID);

// Set properties
$propertyCollection = $order->getPropertyCollection();
$propertyCollection->getAddress()->setValue($payload['delivery_address']);
$propertyCollection->getDeliveryDate()->setValue($payload['delivery_date']);

// Save order
$result = $order->save();

if ($result->isSuccess()) {
    echo json_encode([
        'success' => true,
        'bitrix_order_id' => $order->getId(),
        'railway_order_id' => $payload['railway_order_id']
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'errors' => $result->getErrorMessages()
    ]);
}
```

**Альтернатива (если нет доступа к Production коду)**:
Использовать существующий `POST /create` endpoint, если он поддерживает создание заказов (сейчас он создаёт только продукты).

---

#### Задача 2.2: Webhook от Railway к Production
**Приоритет**: 🔴 CRITICAL
**Срок**: 1-2 дня

**Файл**: `backend/services/production_sync.py`

```python
"""
Sync orders from Railway to Production API.
"""

import httpx
from backend.models import Order
from backend.config import settings

PRODUCTION_API = "https://cvety.kz/api/v2"
PRODUCTION_TOKEN = settings.cvety_production_token

async def sync_order_to_production(order: Order):
    """
    Send newly created Railway order to Production (Bitrix).
    
    Called after order creation in Railway.
    """
    
    payload = {
        "railway_order_id": order.id,
        "customer_name": order.phone,  # or order.customer_name
        "customer_phone": order.phone,
        "delivery_address": order.delivery_address,
        "delivery_date": order.delivery_date.isoformat(),
        "delivery_time": order.delivery_time,
        "recipient_name": order.recipient_name,
        "recipient_phone": order.recipient_phone,
        "items": [
            {
                "product_id": item.product.external_id,  # Production product ID
                "quantity": item.quantity,
                "price": item.price // 100  # kopecks to tenge
            }
            for item in order.items
        ],
        "total_amount": order.total_price // 100
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{PRODUCTION_API}/orders/create",
            params={"access_token": PRODUCTION_TOKEN},
            json=payload
        )
        response.raise_for_status()
        result = response.json()
    
    # Save Production order ID for future reference
    order.external_id = str(result.get("bitrix_order_id"))
    
    logger.info(
        f"Synced order {order.id} to Production. "
        f"Bitrix order ID: {order.external_id}"
    )
```

**Интеграция в order creation**:

```python
# backend/api/orders/router.py (modify)

@router.post("/public/create", response_model=OrderRead)
async def create_order_public(...):
    # ... existing order creation logic ...
    
    order = await OrderService.create_order_with_items(...)
    
    # NEW: Sync to Production
    try:
        await sync_order_to_production(order)
    except Exception as e:
        logger.error(f"Failed to sync order {order.id} to Production: {e}")
        # Don't fail the customer's order if Production sync fails
        # We'll retry later via background job
    
    return order
```

---

#### Задача 2.3: Обратная синхронизация статусов Production → Railway
**Приоритет**: 🟡 MEDIUM
**Срок**: 3-4 дня

**Проблема**:
- Флорист меняет статус заказа в Production (Bitrix)
- Клиент должен видеть новый статус в Telegram Bot

**Решение**: Webhook от Production или polling

**Вариант A: Webhook от Production (Preferred)**

```php
// Production (Bitrix) - Event handler
// /home/bitrix/www/local/php_interface/init.php

use Bitrix\Main\EventManager;
use Bitrix\Sale\Order;

$eventManager = EventManager::getInstance();
$eventManager->addEventHandler(
    'sale',
    'OnSaleOrderSaved',
    'sendOrderStatusToRailway'
);

function sendOrderStatusToRailway($orderId) {
    $order = Order::load($orderId);
    
    // Find Railway order ID
    $railwayOrderId = $order->getPropertyCollection()
        ->getItemByOrderPropertyId('RAILWAY_ORDER_ID')
        ->getValue();
    
    if (!$railwayOrderId) {
        return; // Not a Railway order
    }
    
    // Send webhook to Railway
    $ch = curl_init('https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/order-status');
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
        'railway_order_id' => $railwayOrderId,
        'bitrix_order_id' => $orderId,
        'status' => $order->getField('STATUS_ID'),
        'webhook_secret' => 'YOUR_SECRET_KEY'
    ]));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_exec($ch);
    curl_close($ch);
}
```

**Railway webhook handler**:

```python
# backend/api/webhooks.py

@router.post("/webhooks/order-status")
async def order_status_webhook(
    webhook_data: dict,
    webhook_secret: str = Header(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Receive order status updates from Production (Bitrix).
    """
    
    if webhook_secret != settings.production_webhook_secret:
        raise HTTPException(401)
    
    order_id = webhook_data["railway_order_id"]
    new_status = map_bitrix_status_to_railway(webhook_data["status"])
    
    # Update order status
    order = await session.get(Order, order_id)
    order.status = new_status
    
    await session.commit()
    
    # Notify customer via Telegram
    await notify_customer_status_change(order)
```

**Вариант B: Polling (Fallback)**

```python
# backend/tasks/sync_scheduler.py

@scheduler.scheduled_job('interval', minutes=5)
async def poll_production_order_statuses():
    """Poll Production API for order status changes every 5 minutes."""
    
    # Get all Railway orders synced to Production
    orders = await get_orders_with_external_id()
    
    for order in orders:
        production_order = await fetch_production_order(order.external_id)
        
        if production_order["status"] != order.status:
            await update_order_status(order, production_order["status"])
            await notify_customer_status_change(order)
```

---

## 📋 PHASE 3: Интеграция оплаты (Kaspi Pay)

### Проблема:
- Клиент создал заказ в Railway
- Нужно отправить запрос на оплату через Kaspi Pay
- После оплаты обновить статус заказа

### Решение: Kaspi Pay Remote Payment API (уже интегрировано!)

#### Задача 3.1: Проверить Kaspi Pay конфигурацию
**Приоритет**: 🟡 MEDIUM
**Срок**: 1 день

**Что проверить**:

```python
# backend/config.py
class Settings(BaseSettings):
    # Kaspi Pay credentials
    kaspi_merchant_id: str = "your_merchant_id"
    kaspi_token: str = "your_kaspi_token"
    kaspi_api_url: str = "https://kaspi.kz/merchantapi"
```

**Проверить в Railway Environment Variables**:
- `KASPI_MERCHANT_ID` - ID магазина в Kaspi
- `KASPI_TOKEN` - API токен для Kaspi Pay
- `KASPI_API_URL` - Production endpoint

**Тестовый запрос**:

```bash
curl -X POST https://figma-product-catalog-production.up.railway.app/api/v1/kaspi-pay/create \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "77015211545",
    "amount": 17500,
    "message": "Оплата заказа #12345"
  }'
```

**Ожидаемый ответ**:
```json
{
  "success": true,
  "payment_id": "abc123",
  "external_id": "order-12345",
  "status": "PENDING",
  "payment_url": "https://kaspi.kz/pay/abc123"
}
```

---

#### Задача 3.2: Автоматическое создание платежа при заказе
**Приоритет**: 🟡 MEDIUM
**Срок**: 1 день

**Уже реализовано в Railway Backend!**

```python
# backend/api/orders/router.py:826-851

@router.post("/public/create", response_model=OrderRead)
async def create_order_public(...):
    # ... create order ...
    
    # Automatically create Kaspi payment if payment_method == "kaspi"
    if order_in.payment_method == "kaspi":
        try:
            await OrderService.create_kaspi_payment_for_order(session, order)
        except Exception as e:
            logger.error(f"Failed to create Kaspi payment: {e}")
```

**Проверить**, что это работает:

1. Создать заказ через MCP tool
2. Указать `payment_method: "kaspi"`
3. Проверить, что создался `KaspiPayment` в базе
4. Клиент получает ссылку на оплату

---

#### Задача 3.3: Webhook от Kaspi Pay для подтверждения оплаты
**Приоритет**: 🔴 CRITICAL
**Срок**: 2-3 дня

**Проблема**: После оплаты Kaspi должен уведомить наш backend

**Решение**: Kaspi Pay Webhook

```python
# backend/api/kaspi_pay.py

@router.post("/webhooks/payment-callback")
async def kaspi_payment_callback(
    webhook_data: dict,
    session: AsyncSession = Depends(get_session)
):
    """
    Kaspi Pay calls this endpoint when payment is completed.
    
    Payload:
    {
      "payment_id": "abc123",
      "status": "PAID",
      "amount": 17500,
      "timestamp": "2025-10-20T15:30:00Z"
    }
    """
    
    # Find payment by external_id
    payment = await session.execute(
        select(KaspiPayment).where(
            KaspiPayment.external_id == webhook_data["payment_id"]
        )
    )
    payment = payment.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(404, "Payment not found")
    
    # Update payment status
    payment.status = webhook_data["status"]
    payment.paid_at = datetime.fromisoformat(webhook_data["timestamp"])
    
    # Update order status
    order = payment.order
    if webhook_data["status"] == "PAID":
        order.status = OrderStatus.PAID
        order.payment_status = "paid"
    
    await session.commit()
    
    # Notify customer
    await notify_customer_payment_confirmed(order)
    
    return {"success": True}
```

**Зарегистрировать webhook в Kaspi Merchant Panel**:
- Webhook URL: `https://figma-product-catalog-production.up.railway.app/api/v1/kaspi-pay/webhooks/payment-callback`
- Events: `payment.paid`, `payment.failed`

---

## 📋 PHASE 4: Telegram Bot Full Integration

### Задача 4.1: Полный order flow в Telegram Bot
**Приоритет**: 🔴 CRITICAL
**Срок**: 3-4 дня

**User Flow**:

```python
# telegram-bot/handlers/order_creation.py

async def handle_order_creation(update, context):
    """
    Full order creation flow:
    1. Customer searches for bouquet (visual or text)
    2. Selects product
    3. Enters delivery details
    4. Confirms order
    5. Receives Kaspi payment link
    6. Pays
    7. Gets confirmation
    """
    
    # Step 1: Product selection (already working via visual search)
    selected_product_id = context.user_data.get("selected_product")
    
    # Step 2: Collect delivery details
    await update.message.reply_text(
        "📋 Укажите адрес доставки:",
        reply_markup=ReplyKeyboardMarkup([
            ["Использовать сохранённый адрес"],
            ["Ввести новый адрес"]
        ])
    )
    
    # ... conversation flow ...
    
    # Step 3: Create order via MCP
    order = await mcp_client.call_tool(
        "create_order",
        customer_name=context.user_data["phone"],
        phone=context.user_data["phone"],
        delivery_address=delivery_address,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
        items=[{"product_id": selected_product_id, "quantity": 1}],
        shop_id=8,
        payment_method="kaspi"
    )
    
    # Step 4: Send payment link
    payment_url = order["kaspi_payment"]["payment_url"]
    
    await update.message.reply_text(
        f"""
        ✅ Заказ #{order['tracking_id']} создан!
        
        💰 Сумма к оплате: {order['total_price'] / 100} ₸
        
        Оплатите через Kaspi:
        {payment_url}
        
        После оплаты мы начнём готовить ваш букет 🌸
        """
    )
```

---

#### Задача 4.2: Уведомления клиента о статусе заказа
**Приоритет**: 🟡 MEDIUM
**Срок**: 2-3 дня

**Интеграция с Railway webhook**:

```python
# backend/api/webhooks.py (addition)

async def notify_customer_status_change(order: Order):
    """
    Send Telegram notification when order status changes.
    """
    
    # Get customer's Telegram chat_id
    telegram_client = await get_telegram_client_by_phone(order.phone)
    
    if not telegram_client:
        logger.warning(f"No Telegram client found for order {order.id}")
        return
    
    # Send notification
    await telegram_bot.send_message(
        chat_id=telegram_client.telegram_user_id,
        text=format_status_notification(order)
    )

def format_status_notification(order: Order) -> str:
    """Format order status message for Telegram."""
    
    messages = {
        OrderStatus.PAID: "✅ Оплата получена! Готовим ваш букет.",
        OrderStatus.IN_PRODUCTION: "🌸 Букет в работе у флориста.",
        OrderStatus.READY: "📦 Букет готов к отправке!",
        OrderStatus.IN_DELIVERY: "🚗 Курьер в пути!",
        OrderStatus.DELIVERED: "🎉 Букет доставлен! Спасибо за заказ!"
    }
    
    return f"""
    📋 Заказ #{order.tracking_id}
    
    {messages.get(order.status, f"Статус: {order.status}")}
    
    Отследить заказ: /track_{order.tracking_id}
    """
```

---

## 📋 PHASE 5: Testing & Deployment

### Задача 5.1: End-to-End тестирование
**Приоритет**: 🔴 CRITICAL
**Срок**: 2-3 дня

**Сценарии тестирования**:

1. **Happy Path**:
   - Клиент отправляет фото букета
   - Находит похожий в каталоге
   - Создаёт заказ
   - Оплачивает через Kaspi
   - Получает уведомления о статусе
   - Получает фото готового букета
   - Заказ доставлен

2. **Edge Cases**:
   - Продукт не найден визуально
   - Продукт нет в наличии
   - Оплата не прошла (Kaspi declined)
   - Клиент отменяет заказ
   - Неверный адрес доставки

**Файл**: `tests/test_full_customer_flow.py`

```python
async def test_full_customer_order_flow():
    """
    Test complete customer journey from search to delivery.
    """
    
    # 1. Visual search
    search_result = await mcp_client.call_tool(
        "search_similar_bouquets",
        image_url="https://example.com/bouquet.jpg",
        topK=3
    )
    assert len(search_result["exact"]) > 0
    
    # 2. Create order
    order = await mcp_client.call_tool(
        "create_order",
        phone="+77015211545",
        items=[{"product_id": search_result["exact"][0]["id"], "quantity": 1}],
        shop_id=8,
        payment_method="kaspi"
    )
    assert order["tracking_id"]
    assert order["kaspi_payment"]["payment_url"]
    
    # 3. Simulate Kaspi payment
    await simulate_kaspi_payment(order["kaspi_payment"]["external_id"])
    
    # 4. Check order synced to Production
    production_order = await fetch_production_order(order["external_id"])
    assert production_order["status"] == "new"
    
    # 5. Simulate status changes in Production
    await update_production_order_status(order["external_id"], "in_production")
    
    # Wait for webhook
    await asyncio.sleep(2)
    
    # 6. Verify Railway order updated
    railway_order = await fetch_railway_order(order["id"])
    assert railway_order["status"] == "IN_PRODUCTION"
```

---

### Задача 5.2: Monitoring & Logging
**Приоритет**: 🟡 MEDIUM
**Срок**: 2 дня

**Что мониторить**:

1. **Sync errors** (Railway ↔ Production)
   - Failed product imports
   - Failed order sync
   - Webhook delivery failures

2. **Payment errors**
   - Kaspi API failures
   - Payment webhook not received
   - Duplicate payments

3. **Visual search performance**
   - Search latency
   - Indexing failures
   - Low similarity matches

**Logging setup**:

```python
# backend/utils/monitoring.py

import structlog
from prometheus_client import Counter, Histogram

# Metrics
order_created_counter = Counter('orders_created_total', 'Total orders created')
order_sync_failed_counter = Counter('order_sync_failed_total', 'Failed order syncs')
visual_search_duration = Histogram('visual_search_duration_seconds', 'Visual search latency')

logger = structlog.get_logger()

async def log_order_created(order: Order):
    logger.info(
        "order_created",
        order_id=order.id,
        tracking_id=order.tracking_id,
        total_price=order.total_price,
        payment_method=order.payment_method
    )
    order_created_counter.inc()

async def log_sync_failure(order_id: int, error: Exception):
    logger.error(
        "order_sync_failed",
        order_id=order_id,
        error=str(error),
        exc_info=True
    )
    order_sync_failed_counter.inc()
```

---

## 🎯 Summary: Task Checklist

### CRITICAL (Must have для запуска)

- [ ] **1.1** Создать скрипт импорта продуктов Production → Railway (1-2 дня)
- [ ] **2.1** Создать API endpoint в Production для приёма заказов (2-3 дня)
- [ ] **2.2** Webhook Railway → Production при создании заказа (1-2 дня)
- [ ] **3.3** Webhook Kaspi Pay → Railway при оплате (2-3 дня)
- [ ] **4.1** Полный order flow в Telegram Bot (3-4 дня)
- [ ] **5.1** End-to-End тестирование (2-3 дня)

**Итого CRITICAL**: ~12-17 дней

---

### MEDIUM (Важно, но можно отложить)

- [ ] **1.2** Регулярная синхронизация продуктов (cron job) (3-4 дня)
- [ ] **1.3** Индексация всех продуктов в Visual Search (2-3 дня)
- [ ] **2.3** Webhook Production → Railway для обновления статусов (3-4 дня)
- [ ] **3.1** Проверить Kaspi Pay конфигурацию (1 день)
- [ ] **3.2** Автоматическое создание платежа (уже готово, проверить) (1 день)
- [ ] **4.2** Telegram уведомления о статусе заказа (2-3 дня)
- [ ] **5.2** Monitoring & Logging (2 дня)

**Итого MEDIUM**: ~14-18 дней

---

### LOW (Nice to have)

- [ ] Retry logic для failed syncs
- [ ] Admin dashboard для мониторинга sync errors
- [ ] Auto-reindex visual search при обновлении продукта
- [ ] A/B testing similarity thresholds
- [ ] Analytics dashboard (популярные запросы, conversion rate)

---

## 🚀 Deployment Timeline

### Week 1 (Days 1-7): Core Infrastructure
- Import products script (1.1)
- Production order creation endpoint (2.1)
- Railway → Production sync (2.2)
- Basic testing

### Week 2 (Days 8-14): Payment & Bot
- Kaspi Pay webhook (3.3)
- Telegram Bot order flow (4.1)
- End-to-end testing (5.1)

### Week 3 (Days 15-21): Refinement
- Visual search indexing (1.3)
- Status sync webhook (2.3)
- Notifications (4.2)
- Monitoring (5.2)

### Week 4 (Days 22-28): Production Launch
- Final testing
- Bug fixes
- Soft launch (limited customers)
- Monitor and iterate

---

**Total Estimated Time**: 3-4 weeks for full production-ready system

**MVP (Minimum Viable Product)**: 2 weeks for basic order flow
- Products synced
- Orders created and synced to Production
- Kaspi payment working
- Basic Telegram Bot flow

---

**Prepared by**: Claude Code
**Date**: October 20, 2025
**Next Action**: Review with team, prioritize CRITICAL tasks, assign developers
