# Bitrix API v2 - Полная документация

> **Производственный API** для управления заказами и товарами флористического магазина cvety.kz

**Версия API**: v2
**Базовый URL**: `https://cvety.kz/api/v2`
**Аутентификация**: Bearer Token
**Дата обновления**: 2025-10-25

---

## 📖 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Аутентификация](#аутентификация)
3. [Структура ответов](#структура-ответов)
4. [Endpoints: Заказы](#endpoints-заказы)
5. [Endpoints: Товары](#endpoints-товары)
6. [Endpoints: Пользователи](#endpoints-пользователи)
7. [Маппинг полей (Property Codes)](#маппинг-полей-property-codes)
8. [Обработка ошибок](#обработка-ошибок)
9. [Debug Mode](#debug-mode)
10. [Частые проблемы](#частые-проблемы)

---

## 🚀 Быстрый старт

### Установка зависимостей (если используете готовый клиент)

```bash
npm install
```

### Пример запроса (curl)

```bash
# Получить список заказов
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/orders/?limit=10"

# Получить список товаров
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/?type=catalog&limit=20"
```

### Пример запроса (JavaScript)

```javascript
const BITRIX_TOKEN = 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144';
const BASE_URL = 'https://cvety.kz/api/v2';

async function fetchOrders() {
  const response = await fetch(`${BASE_URL}/orders/?limit=10`, {
    headers: {
      'Authorization': `Bearer ${BITRIX_TOKEN}`,
      'X-City': 'almaty'
    }
  });

  const data = await response.json();
  console.log(data);
}

fetchOrders();
```

---

## 🔐 Аутентификация

Все endpoints требуют Bearer Token в заголовке `Authorization`.

### Заголовки запроса

| Заголовок | Обязательно | Описание |
|-----------|-------------|----------|
| `Authorization` | ✅ Да | `Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144` |
| `X-City` | ⚠️ Рекомендуется | Город для фильтрации: `almaty`, `astana` (по умолчанию: `astana`) |
| `Content-Type` | ✅ Для POST/PUT/PATCH | `application/json` |

**⚠️ Важно**: Не добавляйте `Content-Type` для GET/DELETE запросов, иначе Bitrix API вернет ошибку!

### Пример правильных заголовков

```javascript
// GET запрос - БЕЗ Content-Type
const getHeaders = {
  'Authorization': 'Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144',
  'X-City': 'almaty'
};

// POST запрос - С Content-Type
const postHeaders = {
  'Authorization': 'Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144',
  'X-City': 'almaty',
  'Content-Type': 'application/json'
};
```

---

## 📦 Структура ответов

Все endpoints возвращают JSON в одном из двух форматов:

### Формат 1: Legacy Bitrix Response (список объектов)

```json
{
  "success": true,
  "data": [
    { /* объект 1 */ },
    { /* объект 2 */ }
  ],
  "pagination": {
    "total": 33,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

### Формат 2: FastAPI Response (одиночный объект)

```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Розы красные",
    /* другие поля */
  }
}
```

### Формат ошибки

```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Order not found"
  }
}
```

---

## 📋 Endpoints: Заказы

### 1. GET /orders/ - Список заказов

Получить список заказов с фильтрацией и пагинацией.

**Query Parameters:**

| Параметр | Тип | Обязательно | По умолчанию | Описание |
|----------|-----|-------------|--------------|----------|
| `limit` | integer | ❌ | 20 | Кол-во заказов на странице (1-100) |
| `offset` | integer | ❌ | 0 | Смещение для пагинации |
| `status` | string | ❌ | - | Фильтр по статусу: `new`, `paid`, `accepted`, `assembled`, `in_delivery`, `delivered`, `cancelled` |

**Пример запроса:**

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/orders/?limit=10&status=accepted"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": [
    {
      "id": 12345,
      "number": "2025-10-001",
      "status_key": "accepted",
      "paymentAmount": "12 990 ₸",
      "paymentStatus": "Оплачен",
      "sender": {
        "name": "Иван Петров",
        "phone": "+77771234567"
      },
      "recipient": {
        "name": "Мария Иванова",
        "phone": "+77779876543"
      },
      "deliveryAddress": "ул. Абая 150, кв. 25",
      "deliveryDate": "2025-10-26",
      "deliveryTime": "14:00-16:00",
      "createdAt": "2025-10-24T10:30:00Z",
      "mainImage": "https://cvety.kz/upload/.../IMG_0255.jpeg",
      "itemImages": [
        "https://cvety.kz/upload/.../IMG_0255.jpeg",
        "https://cvety.kz/upload/.../IMG_0256.jpeg"
      ],
      "executors": [
        {
          "id": 42,
          "name": "Анна Флорист",
          "source": "Cvety.kz"
        }
      ],
      "items": [
        {
          "id": 1,
          "productName": "Розы красные 15 шт",
          "amount": 1,
          "price": "12990",
          "currency": "KZT",
          "productImage": "https://cvety.kz/upload/.../rose.jpg"
        }
      ]
    }
  ],
  "pagination": {
    "total": 33,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

---

### 2. GET /orders/detail/ - Детали заказа

Получить полную информацию о заказе, включая историю изменений.

**Query Parameters:**

| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `id` | integer | ✅ Да | ID заказа |

**Пример запроса:**

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/orders/detail/?id=12345"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 12345,
    "number": "2025-10-001",
    "status_key": "accepted",
    "raw": {
      "id": 12345,
      "dateCreated": "24.10.2025",
      "statusId": "AP",
      "price": "12990",
      "currency": "KZT",
      "senderName": "Иван Петров",
      "senderPhone": "+77771234567",
      "recipientName": "Мария Иванова",
      "recipientPhone": "+77779876543",
      "deliveryAddress": "ул. Абая 150, кв. 25",
      "deliveryDate": "26.10.2025",
      "deliveryType": "14:00-16:00",
      "deliveryPrice": "1500",
      "isPayed": true,
      "paySystem": "Kaspi Pay",
      "payLink": "https://kaspi.kz/pay/...",
      "postcardText": "С днем рождения!",
      "comment": "Позвонить за час",
      "responsibleId": 42,
      "basket": [
        {
          "id": 1,
          "productName": "Розы красные 15 шт",
          "amount": 1,
          "price": "12990",
          "currency": "KZT",
          "productImage": "https://cvety.kz/upload/.../rose.jpg",
          "productImageBig": "https://cvety.kz/upload/.../rose_big.jpg"
        }
      ],
      "executors": [
        {
          "id": 42,
          "name": "Анна Флорист",
          "source": "Cvety.kz"
        }
      ],
      "history": [
        {
          "status": "Новый",
          "timestamp": "2025-10-24T10:30:00Z",
          "user": "Система"
        },
        {
          "status": "Оплачен",
          "timestamp": "2025-10-24T10:35:00Z",
          "user": "Kaspi Pay"
        },
        {
          "status": "Принят",
          "timestamp": "2025-10-24T11:00:00Z",
          "user": "Анна Флорист"
        }
      ],
      "urls": {
        "status": "https://cvety.kz/track/abc123"
      },
      "assembledImage": "https://cvety.kz/upload/.../assembled.jpg",
      "recipientPhoto": "https://cvety.kz/upload/.../delivered.jpg"
    },
    "createdAt": "2025-10-24T10:30:00Z",
    "updatedAt": "2025-10-24T11:00:00Z"
  }
}
```

---

### 3. PATCH /orders/{id}/status/ - Изменить статус заказа

Обновить статус заказа.

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID заказа |

**Request Body:**

```json
{
  "status": "ACCEPTED"
}
```

**Доступные статусы:**

| Код | Русский | Описание |
|-----|---------|----------|
| `NEW` | Новый | Заказ создан |
| `PAID` | Оплачен | Оплата получена |
| `ACCEPTED` | Принят | Флорист принял заказ |
| `IN_PRODUCTION` | Собран | Букет собран |
| `IN_DELIVERY` | В доставке | Передано курьеру |
| `DELIVERED` | Доставлен | Заказ доставлен |
| `CANCELLED` | Отменен | Заказ отменен |

**Пример запроса:**

```bash
curl -X PATCH \
  -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  -H "Content-Type: application/json" \
  -d '{"status":"ACCEPTED"}' \
  "https://cvety.kz/api/v2/orders/12345/status/"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 12345,
    "status": "accepted",
    "updated_at": "2025-10-24T11:05:00Z"
  }
}
```

---

### 4. POST /orders/ - Создать заказ

Создать новый заказ (используется редко, обычно заказы создаются через клиентский интерфейс).

**Request Body:**

```json
{
  "senderName": "Иван Петров",
  "senderPhone": "+77771234567",
  "recipientName": "Мария Иванова",
  "recipientPhone": "+77779876543",
  "deliveryAddress": "ул. Абая 150, кв. 25",
  "deliveryDate": "2025-10-26",
  "deliveryTime": "14:00-16:00",
  "items": [
    {
      "productId": 697695,
      "quantity": 1
    }
  ],
  "postcardText": "С днем рождения!",
  "comment": "Позвонить за час"
}
```

**Пример запроса:**

```bash
curl -X POST \
  -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  -H "Content-Type: application/json" \
  -d '{ /* JSON */ }' \
  "https://cvety.kz/api/v2/orders/"
```

---

## 🌸 Endpoints: Товары

### 1. GET /products/ - Список товаров

Получить список товаров с фильтрацией.

**Query Parameters:**

| Параметр | Тип | Обязательно | По умолчанию | Описание |
|----------|-----|-------------|--------------|----------|
| `type` | string | ❌ | - | Тип товара: `vitrina` (готовые), `catalog` (на заказ) |
| `isAvailable` | boolean | ❌ | - | Показывать только активные товары: `true`, `false` |
| `limit` | integer | ❌ | 20 | Кол-во товаров (1-100) |
| `offset` | integer | ❌ | 0 | Смещение |
| `search` | string | ❌ | - | Поиск по названию |

**Пример запроса:**

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/?type=catalog&limit=10"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": [
    {
      "id": 697695,
      "image": "https://cvety.kz/upload/resize_cache/.../IMG_0255.jpeg",
      "images": [
        "https://cvety.kz/upload/.../IMG_0255.jpeg",
        "https://cvety.kz/upload/.../IMG_0253.jpeg"
      ],
      "title": "Эустомы в пачке",
      "price": "7 500 ₸",
      "isAvailable": true,
      "createdAt": "2025-09-26T14:59:39+0500",
      "type": "catalog",
      "width": null,
      "height": null,
      "video": null,
      "duration": null,
      "discount": "0",
      "composition": null,
      "colors": false,
      "catalogWidth": "",
      "catalogHeight": "",
      "productionTime": null
    }
  ],
  "pagination": {
    "total": 21,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

---

### 2. GET /products/detail - Детали товара

Получить полную информацию о товаре.

**Query Parameters:**

| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `id` | integer | ✅ Да | ID товара |

**Пример запроса:**

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/detail?id=697695"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 697695,
    "image": "https://cvety.kz/upload/.../IMG_0255.jpeg",
    "images": [
      "https://cvety.kz/upload/.../IMG_0255.jpeg",
      "https://cvety.kz/upload/.../IMG_0253.jpeg"
    ],
    "title": "Эустомы в пачке",
    "price": "7 500 ₸",
    "isAvailable": true,
    "createdAt": "2025-09-26T14:59:39+0500",
    "type": "catalog",
    "width": "",
    "height": "",
    "video": null,
    "duration": null,
    "discount": null,
    "composition": [
      {
        "id": 123,
        "name": "Эустомы белые",
        "amount": 7
      }
    ],
    "colors": false,
    "catalogWidth": null,
    "catalogHeight": null,
    "productionTime": "short"
  }
}
```

---

### 3. DELETE /products/delete - Деактивировать товар

Деактивировать товар (soft delete, устанавливает `ACTIVE='N'`).

**Query Parameters:**

| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `id` | integer | ✅ Да | ID товара |

**Пример запроса:**

```bash
curl -X DELETE \
  -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/delete?id=697695"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 697695,
    "deleted": true
  }
}
```

---

### 4. GET /products/composition - Состав товара

Получить рецепт товара (состав из складских позиций).

**Query Parameters:**

| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `id` | integer | ✅ Да | ID товара |

**Пример запроса:**

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/composition?id=697695"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 697695,
    "availableQuantity": 5,
    "composition": [
      {
        "id": 123,
        "name": "Розы красные",
        "amount": 7
      },
      {
        "id": 456,
        "name": "Зелень",
        "amount": 1
      }
    ]
  }
}
```

---

### 5. POST /products/composition - Установить состав товара

Задать рецепт для товара.

**Request Body:**

```json
{
  "id": 697695,
  "composition": [
    {
      "id": 123,
      "amount": 7
    },
    {
      "id": 456,
      "amount": 1
    }
  ]
}
```

**Пример запроса:**

```bash
curl -X POST \
  -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  -H "Content-Type: application/json" \
  -d '{"id":697695,"composition":[{"id":123,"amount":7}]}' \
  "https://cvety.kz/api/v2/products/composition"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 697695,
    "count": 2,
    "stored_as": "json"
  }
}
```

---

## 👥 Endpoints: Пользователи

### 1. GET /users/{id}/ - Информация о пользователе

Получить данные пользователя (флорист, курьер, менеджер).

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID пользователя |

**Пример запроса:**

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/users/42/"
```

**Пример ответа:**

```json
{
  "success": true,
  "data": {
    "id": 42,
    "name": "Анна Флорист",
    "userName": "anna.florist",
    "email": "anna@cvety.kz",
    "phone": "+77771234567"
  }
}
```

---

## 🗺️ Маппинг полей (Property Codes)

### Заказы: Bitrix → API

| Bitrix Property Code | API Field | Тип | Пример значения | Описание |
|---------------------|-----------|-----|-----------------|----------|
| `ID` | `id` | integer | `12345` | ID заказа |
| `number` | `order_number` | string | `"2025-10-001"` | Номер заказа |
| `statusId` | `status` | string | `"AP"` → `"ACCEPTED"` | Статус заказа (маппинг: N→NEW, AP→ACCEPTED, AS→IN_PRODUCTION, ID→IN_DELIVERY, D→DELIVERED, C→CANCELLED) |
| `status_key` | `status` | string | `"accepted"` | Статус заказа (lowercase) |
| `paymentAmount` | `total_price` | string → float | `"12 990 ₸"` → `12990.0` | Сумма заказа |
| `paySystem` | `payment_method` | string | `"Kaspi Pay"` | Способ оплаты |
| `isPayed` | `is_paid` | boolean | `true` | Оплачен или нет |
| `senderName` | `sender_name`, `customer_name` | string | `"Иван Петров"` | Имя отправителя |
| `senderPhone` | `sender_phone`, `customer_phone` | string | `"+77771234567"` | Телефон отправителя |
| `senderEmail` | `sender_email` | string | `"ivan@mail.kz"` | Email отправителя |
| `recipientName` | `recipient_name` | string | `"Мария Иванова"` | Имя получателя |
| `recipientPhone` | `recipient_phone` | string | `"+77779876543"` | Телефон получателя |
| `deliveryAddress` | `delivery_address` | string | `"ул. Абая 150, кв. 25"` | Адрес доставки |
| `deliveryDate` | `delivery_date` | string | `"26.10.2025"` или `"2025-10-26"` | Дата доставки |
| `deliveryType` | `delivery_time` | string | `"14:00-16:00"` | Время доставки |
| `deliveryPrice` | `delivery_price` | integer | `1500` | Стоимость доставки в тенге |
| `city` | `delivery_city` | string | `"Алматы"` | Город доставки |
| `postcardText` | `postcard_text` | string | `"С днем рождения!"` | Текст открытки |
| `comment` | `comment` | string | `"Позвонить за час"` | Комментарий к заказу |
| `notes` | `notes` | string | `"Флорист: нет роз"` | Заметки флориста |
| `responsibleId` | `responsible_id` | integer | `42` | ID ответственного |
| `askAddress` | `ask_address` | boolean | `true` | Узнать адрес у получателя |
| `pickup` | `is_pickup` | boolean | `false` | Самовывоз |
| `basket` | `items[]` | array | `[{...}]` | Товары в заказе |
| `basket[].productName` | `items[].name` | string | `"Розы красные 15 шт"` | Название товара |
| `basket[].amount` | `items[].quantity` | integer | `1` | Количество |
| `basket[].price` | `items[].price` | float | `12990.0` | Цена товара в тенге |
| `basket[].productImage` | `items[].image` | string | `"https://cvety.kz/upload/.../rose.jpg"` | URL фото товара |
| `executors[]` | `executors[]` | array | `[{id:42, name:"Анна"}]` | Исполнители (флорист, курьер) |
| `history[]` | `history[]` | array | `[{status:"Новый", ...}]` | История изменений |
| `assembledImage` | `assembled_photo` | string | `"https://cvety.kz/upload/.../assembled.jpg"` | Фото собранного букета |
| `recipientPhoto` | `recipient_photo` | string | `"https://cvety.kz/upload/.../delivered.jpg"` | Фото доставки |
| `urls.status` | `tracking_url` | string | `"https://cvety.kz/track/abc123"` | Ссылка для отслеживания |
| `dateCreated` | `created_at` | string | `"24.10.2025"` → `"2025-10-24T00:00:00Z"` | Дата создания |

### Товары: Bitrix → API

| Bitrix Property Code | API Field | Тип | Пример значения | Описание |
|---------------------|-----------|-----|-----------------|----------|
| `ID` | `id` | integer | `697695` | ID товара |
| `NAME` | `name`, `title` | string | `"Эустомы в пачке"` | Название товара |
| `PRICE` | `price` | string или kopecks | `"7 500 ₸"` или `750000` | Цена (в API может быть строка с форматированием или kopecks) |
| `ACTIVE` | `enabled`, `isAvailable` | boolean | `true` | Активен ли товар |
| `PREVIEW_PICTURE` | `image` | string | `"https://cvety.kz/upload/.../IMG_0255.jpeg"` | Главное фото |
| `DETAIL_PICTURE` | `image` | string | `"https://cvety.kz/upload/.../IMG_0255.jpeg"` | Детальное фото |
| `IMAGES` | `images[]` | array | `["https://...", "https://..."]` | Все фото товара |
| `DETAIL_TEXT` | `description`, `composition` | string | `"Нежные эустомы"` | Описание |
| `IS_READY` | `type` | string | `true` → `"vitrina"`, `false` → `"catalog"` | Готовый товар или на заказ |
| `WIDTH` | `width`, `catalogWidth` | string | `"30"` | Ширина в см |
| `HEIGHT` | `height`, `catalogHeight` | string | `"40"` | Высота в см |
| `DURATION` | `duration`, `productionTime` | string | `"30"` → `"short"` | Время сборки (≤30 = short, ≤60 = medium, >60 = long) |
| `DISCOUNT` | `discount` | string | `"10"` | Скидка в процентах |
| `VIDEO` | `video` | string | `"https://..."` | Ссылка на видео |
| `COMPOSITION` | `composition[]` | array | `[{id:123, name:"Розы", amount:7}]` | Состав (рецепт) |
| `COLORS` | `colors` | array/boolean | `false` или `[...]` | Доступные цвета |
| `TIMESTAMP_X` | `created_at`, `createdAt` | string | `"2025-09-26T14:59:39+0500"` | Дата создания |

### Маппинг времени доставки (deliveryType → delivery_time)

Bitrix хранит время доставки в поле `deliveryType` с кодами. Вот таблица маппинга:

| Bitrix Property Code | Значение в базе | API Field `delivery_time` | Отображение для клиента |
|---------------------|-----------------|---------------------------|-------------------------|
| `when` (deliveryType) | `"0"` | `"Как можно скорее"` | "Как можно скорее" |
| `when` (deliveryType) | `"1"` | `"08:00-12:00"` | "8:00 - 12:00" |
| `when` (deliveryType) | `"2"` | `"12:00-16:00"` | "12:00 - 16:00" |
| `when` (deliveryType) | `"3"` | `"16:00-20:00"` | "16:00 - 20:00" |
| `when` (deliveryType) | `"4"` | `"20:00-00:00"` | "20:00 - 00:00" |
| `when` (deliveryType) | `"5"` | `"10:00"` | "К 10:00" |
| `when` (deliveryType) | `"custom"` | Точное время | "14:30" (пользователь указал) |

**Пример:**

```javascript
// В ответе API:
"deliveryType": "2"

// Отображается на фронтенде как:
"delivery_time": "12:00-16:00"
```

---

## ⚠️ Обработка ошибок

### HTTP статус-коды

| Код | Название | Когда возвращается |
|-----|----------|-------------------|
| `200` | OK | Успешный запрос (GET, POST, PATCH) |
| `204` | No Content | Успешный DELETE (без тела ответа) |
| `400` | Bad Request | Неверные параметры запроса |
| `401` | Unauthorized | Неверный или отсутствующий токен |
| `404` | Not Found | Ресурс не найден (заказ/товар с таким ID не существует) |
| `500` | Internal Server Error | Ошибка на сервере |

### Примеры ошибок

**401 Unauthorized:**

```json
{
  "success": false,
  "error": {
    "code": "unauthorized",
    "message": "Invalid access token"
  }
}
```

**404 Not Found:**

```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Order not found"
  }
}
```

**500 Internal Server Error:**

```json
{
  "success": false,
  "error": {
    "code": "internal_error",
    "message": "Internal error"
  }
}
```

**400 Bad Request (неверный статус):**

```json
{
  "success": false,
  "error": {
    "code": "invalid_status",
    "message": "Status must be one of: NEW, PAID, ACCEPTED, IN_PRODUCTION, IN_DELIVERY, DELIVERED, CANCELLED"
  }
}
```

---

## 🐛 Debug Mode

### Будет реализован: Query Parameter `?debug=1`

В будущей версии API добавим параметр `debug=1`, который вернет расширенную информацию о запросе:

```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/orders/detail/?id=12345&debug=1"
```

**Пример ответа с debug=1:**

```json
{
  "success": true,
  "data": { /* обычные данные */ },
  "debug": {
    "sql_queries": [
      "SELECT * FROM orders WHERE id = 12345",
      "SELECT * FROM order_items WHERE order_id = 12345"
    ],
    "execution_time_ms": 125,
    "raw_bitrix_properties": {
      "PROPERTY_WHEN": "2",
      "PROPERTY_NAME_RECIPIENT": "Мария Иванова",
      "PROPERTY_ADDRESS_RECIPIENT": "ул. Абая 150"
    },
    "transformations": [
      "deliveryType: '2' → '12:00-16:00'",
      "statusId: 'AP' → 'ACCEPTED'"
    ]
  }
}
```

**Цель debug mode:**
- Увидеть исходные property codes из Bitrix
- Понять какие SQL запросы выполняются
- Проверить правильность трансформаций данных

---

## 🔧 Частые проблемы

### 1. Почему некоторые поля `null`?

**Проблема:**

```json
{
  "width": null,
  "height": null,
  "composition": null
}
```

**Причины:**

1. **Поля не заполнены в Bitrix CMS**: Администратор не указал размеры или состав товара при создании
2. **Тип товара не требует поля**: Например, для товаров типа `catalog` (на заказ) размеры хранятся в `catalogWidth` и `catalogHeight`, а не в `width`/`height`
3. **Property code не привязан к инфоблоку**: В Bitrix может отсутствовать связь между инфоблоком и property

**Решение:**

- Проверить заполнение полей в Bitrix админке
- Использовать правильные поля для типа товара:
  ```javascript
  const width = product.type === 'vitrina'
    ? product.width
    : product.catalogWidth;
  ```

---

### 2. Почему время доставки отображается как "null" или "0"?

**Проблема:**

```json
{
  "deliveryType": "0",
  "delivery_time": null
}
```

**Причина:**

Bitrix хранит время доставки в виде кодов (`"0"`, `"1"`, `"2"` и т.д.), которые нужно преобразовать в человекочитаемый формат.

**Решение:**

Используйте маппинг из раздела [Маппинг времени доставки](#маппинг-времени-доставки-deliverytype--delivery_time).

**Пример на JavaScript:**

```javascript
const deliveryTimeMap = {
  '0': 'Как можно скорее',
  '1': '08:00-12:00',
  '2': '12:00-16:00',
  '3': '16:00-20:00',
  '4': '20:00-00:00',
  '5': 'К 10:00'
};

const deliveryTime = deliveryTimeMap[order.deliveryType] || order.deliveryType;
```

---

### 3. Почему изображения не загружаются?

**Проблема:**

```json
{
  "image": "/upload/resize_cache/iblock/abc/IMG_0255.jpeg"
}
```

Изображение возвращается как относительный путь, а не полный URL.

**Причина:**

Bitrix API иногда возвращает относительные пути вместо абсолютных URL.

**Решение:**

Преобразовать относительный путь в полный URL:

```javascript
function formatImageUrl(imagePath) {
  if (!imagePath) return '';
  if (imagePath.startsWith('http')) return imagePath;
  return `https://cvety.kz${imagePath}`;
}

// Использование:
const imageUrl = formatImageUrl(product.image);
```

---

### 4. Почему цена приходит как строка "7 500 ₸"?

**Проблема:**

```json
{
  "price": "7 500 ₸"
}
```

Нельзя выполнить математические операции с такой ценой.

**Причина:**

Bitrix API v2 возвращает отформатированные цены для удобства отображения.

**Решение:**

Парсить строку в число (kopecks):

```javascript
function parsePrice(priceStr) {
  if (!priceStr) return 0;

  // Удалить все нецифровые символы кроме цифр
  const cleaned = priceStr.toString().replace(/[^0-9]/g, '');
  const tenge = parseInt(cleaned, 10);

  // Конвертировать тенге в копейки
  return tenge * 100;
}

// Использование:
const priceKopecks = parsePrice("7 500 ₸"); // 750000 kopecks
const priceTenge = priceKopecks / 100; // 7500 tenge
```

---

### 5. Почему статус заказа не совпадает с ожидаемым?

**Проблема:**

Вы меняете статус на `ACCEPTED`, но в списке заказов он показывается как `accepted` (lowercase).

**Причина:**

Существует два формата статусов:
- **Legacy Bitrix**: Uppercase коды (`N`, `AP`, `AS`, `ID`, `D`, `C`)
- **Modern API**: Lowercase слова (`new`, `accepted`, `assembled`, `in_delivery`, `delivered`, `cancelled`)

**Решение:**

Используйте адаптер для конвертации статусов:

```javascript
function adaptOrderStatus(statusKey) {
  const statusMap = {
    // Modern API (lowercase)
    'new': 'NEW',
    'accepted': 'ACCEPTED',
    'assembled': 'IN_PRODUCTION',
    'in_delivery': 'IN_DELIVERY',
    'delivered': 'DELIVERED',
    'cancelled': 'CANCELLED',
    // Legacy Bitrix (uppercase)
    'N': 'NEW',
    'AP': 'ACCEPTED',
    'AS': 'IN_PRODUCTION',
    'ID': 'IN_DELIVERY',
    'D': 'DELIVERED',
    'C': 'CANCELLED'
  };

  return statusMap[statusKey] || statusKey?.toUpperCase() || 'NEW';
}
```

---

### 6. CORS ошибки при запросе из браузера

**Проблема:**

```
Access to fetch at 'https://cvety.kz/api/v2/orders/' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Причина:**

Bitrix API настроен для работы с определенными доменами. Локальный dev сервер не в белом списке.

**Решение:**

Используйте прокси:

**Vite (vite.config.js):**

```javascript
export default {
  server: {
    proxy: {
      '/api/v2': {
        target: 'https://cvety.kz',
        changeOrigin: true
      }
    }
  }
};
```

**Next.js (next.config.js):**

```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/v2/:path*',
        destination: 'https://cvety.kz/api/v2/:path*'
      }
    ];
  }
};
```

---

## 📚 Дополнительные ресурсы

- **Production URL**: https://cvety.kz
- **Admin Panel (Bitrix)**: https://cvety.kz/bitrix/admin/
- **Bearer Token**: `ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144`
- **Default City**: Astana (ID: 2), Almaty (ID: 1)

---

## 📝 Changelog

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2025-10-25 | v2.0 | Полная документация создана |
| 2025-10-24 | v1.9 | Добавлены endpoints для товаров (composition) |
| 2025-09-26 | v1.5 | Добавлен фильтр по типу товара (`type=vitrina`) |

---

**Составитель документации**: Claude Code (Anthropic)
**Дата создания**: 2025-10-25
**Формат**: Markdown
**Целевая аудитория**: Русскоязычные разработчики

---

> 💡 **Совет**: Сохраните этот файл в репозиторий проекта как `/docs/API_README_RU.md` для удобства работы команды.
