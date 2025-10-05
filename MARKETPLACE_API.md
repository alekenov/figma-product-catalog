# Marketplace Public API Documentation

This document describes the public API endpoints for the marketplace frontend (customer-facing shop).

## Base URL
- **Development**: `http://localhost:8014/api/v1`
- **Production**: `https://figma-product-catalog-production.up.railway.app/api/v1`

## Authentication
All endpoints listed below are **public** and do **not** require authentication. They are designed for anonymous customers browsing the marketplace.

---

## Phase 1: Shops Discovery

### List All Shops
Get list of active shops with delivery settings and current status.

```http
GET /shops
```

**Query Parameters:**
- `city` (optional) - Filter by city (e.g., `Almaty`, `Astana`)
- `skip` (optional, default: 0) - Number of shops to skip for pagination
- `limit` (optional, default: 20, max: 100) - Number of shops to return

**Response:**
```json
[
  {
    "id": 1,
    "name": "Мой магазин",
    "city": "Almaty",
    "phone": "+77771234567",
    "address": "ул. Абая 150",
    "delivery_cost_tenge": 1500,
    "delivery_available": true,
    "pickup_available": true,
    "rating": 4.8,
    "review_count": 25,
    "is_open": true
  }
]
```

### Get Shop Details
Get detailed information about a specific shop including working hours.

```http
GET /shops/{shop_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Мой магазин",
  "phone": "+77771234567",
  "address": "ул. Абая 150",
  "city": "Almaty",
  "weekday_start": "09:00",
  "weekday_end": "18:00",
  "weekday_closed": false,
  "weekend_start": "10:00",
  "weekend_end": "17:00",
  "weekend_closed": false,
  "delivery_cost_tenge": 1500,
  "free_delivery_amount_tenge": 10000,
  "pickup_available": true,
  "delivery_available": true,
  "rating": 4.8,
  "review_count": 25,
  "is_open": true
}
```

### Get Shop Products
Get products for a specific shop.

```http
GET /shops/{shop_id}/products
```

**Query Parameters:**
- `enabled` (optional, default: true) - Filter by enabled status
- `skip` (optional, default: 0) - Number of products to skip
- `limit` (optional, default: 50, max: 200) - Number of products to return

**Response:**
```json
[
  {
    "id": 13,
    "name": "Яркий контраст",
    "price": 1400000,
    "type": "flowers",
    "description": "Эффектная композиция...",
    "manufacturingTime": 30,
    "shelfLife": 7,
    "enabled": true,
    "is_featured": false,
    "colors": ["pink", "purple", "green"],
    "occasions": ["birthday", "celebration"],
    "cities": ["almaty", "astana"],
    "tags": ["roses", "bright"],
    "image": "https://...",
    "created_at": "2025-10-02T07:14:58",
    "updated_at": "2025-10-02T07:14:58"
  }
]
```

---

## Phase 2: Cart & Checkout

### Preview Cart
Preview cart items before checkout - validates availability and calculates totals.

```http
POST /orders/public/preview?shop_id={shop_id}
```

**Request Body:**
```json
[
  {"product_id": 13, "quantity": 1},
  {"product_id": 12, "quantity": 2}
]
```

**Response:**
```json
{
  "available": true,
  "items": [
    {
      "product_id": 13,
      "product_name": "Яркий контраст",
      "quantity_requested": 1,
      "available": true,
      "max_quantity": 9999,
      "ingredients": []
    }
  ],
  "warnings": [],
  "subtotal": 3800000,
  "delivery_cost": 0,
  "free_delivery_threshold": 10000,
  "free_delivery_applied": true,
  "total": 3800000,
  "shop": {
    "id": 1,
    "name": "Мой магазин",
    "delivery_available": true,
    "pickup_available": true
  }
}
```

### Create Order
Create order for anonymous customer.

```http
POST /orders/public/create?shop_id={shop_id}
```

**Request Body:**
```json
{
  "customerName": "Анна Иванова",
  "phone": "77771234567",
  "customer_email": "anna@example.com",
  "delivery_address": "ул. Абая 100, кв. 25",
  "delivery_type": "delivery",
  "delivery_cost": 0,
  "payment_method": "kaspi",
  "order_comment": "Пожалуйста, доставить до 18:00",
  "items": [
    {"product_id": 13, "quantity": 1},
    {"product_id": 12, "quantity": 2}
  ],
  "check_availability": true
}
```

**Response:**
```json
{
  "tracking_id": "160551019",
  "orderNumber": "#12353",
  "customerName": "Анна Иванова",
  "phone": "+77771234567",
  "customer_email": "anna@example.com",
  "delivery_address": "ул. Абая 100, кв. 25",
  "delivery_type": "delivery",
  "payment_method": "kaspi",
  "order_comment": "Пожалуйста, доставить до 18:00",
  "subtotal": 3800000,
  "delivery_cost": 0,
  "total": 3800000,
  "status": "new",
  "id": 8,
  "created_at": "2025-10-03T13:02:52",
  "items": [
    {
      "product_id": 13,
      "product_name": "Яркий контраст",
      "product_price": 1400000,
      "quantity": 1,
      "item_total": 1400000
    }
  ]
}
```

### Track Order
Track order status using public tracking ID (already existed, included for completeness).

```http
GET /orders/by-tracking/{tracking_id}/status
```

**Response:**
```json
{
  "tracking_id": "160551019",
  "order_number": "#12353",
  "status": "confirmed",
  "recipient": {
    "name": "Анна Иванова",
    "phone": "+77771234567"
  },
  "delivery_address": "ул. Абая 100, кв. 25",
  "date_time": "Friday 03 October, 13:02",
  "items": [
    {
      "name": "Яркий контраст",
      "price": 1400000
    }
  ],
  "total": 3800000
}
```

---

## Phase 3: Enhanced Features

### Get Featured Products
Get featured products across all shops for marketplace homepage.

```http
GET /products/public/featured
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of products to skip
- `limit` (optional, default: 20, max: 100) - Number of products to return

**Response:**
```json
[
  {
    "id": 10,
    "name": "Синяя мечта",
    "price": 1800000,
    "type": "flowers",
    "is_featured": true,
    "enabled": true,
    "image": "https://...",
    "colors": ["blue", "pink", "white"],
    "occasions": ["exclusive", "celebration"],
    ...
  }
]
```

### Get Bestsellers
Get bestselling products sorted by order count.

```http
GET /products/public/bestsellers
```

**Query Parameters:**
- `limit` (optional, default: 20, max: 100) - Number of products to return

**Response:**
```json
[
  {
    "id": 1,
    "name": "Романтический букет роз",
    "price": 1500000,
    "is_featured": true,
    ...
  }
]
```

### Get Platform Reviews
Get aggregated reviews from all shops for marketplace homepage.

```http
GET /reviews/platform
```

**Query Parameters:**
- `limit` (optional, default: 10, max: 100) - Number of reviews to return
- `offset` (optional, default: 0) - Number of reviews to skip

**Response:**
```json
{
  "reviews": [
    {
      "id": 1,
      "author_name": "Мария К.",
      "rating": 5,
      "text": "Отличный сервис!",
      "likes": 10,
      "dislikes": 0,
      "shop_name": "Мой магазин",
      "created_at": "2025-10-01T10:00:00"
    }
  ],
  "stats": {
    "total_count": 150,
    "average_rating": 4.8,
    "rating_breakdown": {
      "5": 120,
      "4": 20,
      "3": 5,
      "2": 3,
      "1": 2
    }
  },
  "pagination": {
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input (e.g., product doesn't belong to shop)
- `404 Not Found` - Resource not found (e.g., shop doesn't exist)
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Product 13 does not belong to shop 7"
}
```

---

## Data Types & Enums

### OrderStatus
- `new` - Order created
- `paid` - Payment received
- `accepted` - Shop accepted order
- `assembled` - Bouquet assembled
- `in_delivery` - Out for delivery
- `delivered` - Delivered to customer
- `cancelled` - Order cancelled

### ProductType
- `flowers` - Flower bouquets
- `plants` - Indoor/outdoor plants
- `gifts` - Gift items
- `accessories` - Vases, decorations

### City
- `Almaty`
- `Astana`

### PaymentMethod
- `kaspi` - Kaspi Pay
- `card` - Credit/debit card
- `cash` - Cash on delivery

### DeliveryType
- `delivery` - Courier delivery
- `pickup` - Customer pickup
- `express` - Express delivery
- `scheduled` - Scheduled delivery

---

## Notes

### Multi-Shop Architecture
- All public endpoints support multi-shop marketplace
- Products are validated to belong to the specified shop
- Only active shops (`is_active=true`) appear in listings
- Each order is scoped to a single shop

### Price Format
- All prices are in **kopecks** (тенге * 100)
- Example: `1400000` kopecks = 14,000 тенге
- Frontend should divide by 100 and format with thousands separator

### Phone Number Format
- Input: Can be with or without `+` or `7` prefix
- Storage: Normalized to `+7XXXXXXXXXX` format
- Example: `77771234567` → `+77771234567`

### Availability Checking
- Preview endpoint checks inventory availability
- Create order validates products belong to shop
- Inventory reservations managed automatically

### Free Delivery
- Each shop has `free_delivery_amount_tenge` threshold
- Automatically applied when subtotal exceeds threshold
- Preview endpoint calculates and returns this info
