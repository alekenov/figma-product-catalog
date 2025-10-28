# API Overview

Comprehensive guide to the Flower Shop Platform REST API.

**Base URL**:
- Development: `http://localhost:8014/api/v1`
- Production: `https://figma-product-catalog-production.up.railway.app/api/v1`

**Last Updated**: 2025-10-28

---

## Quick Links

- **Interactive Docs** (Swagger UI): http://localhost:8014/docs
- **Alternative Docs** (ReDoc): http://localhost:8014/redoc
- **Documentation Standard**: [backend/API_DOCUMENTATION_STANDARD.md](../backend/API_DOCUMENTATION_STANDARD.md)
- **Testing Guide**: [backend/API_TESTING_GUIDE.md](../backend/API_TESTING_GUIDE.md)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Multi-Tenancy](#multi-tenancy)
3. [API Modules](#api-modules)
4. [Common Patterns](#common-patterns)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

---

## Authentication

### JWT Token-Based Authentication

Most endpoints require JWT authentication via the `Authorization` header.

**Get Token:**
```bash
curl -X POST http://localhost:8014/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "77015211545", "password": "1234"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 13,
    "phone": "77015211545",
    "role": "DIRECTOR",
    "shop_id": 8
  }
}
```

**Use Token:**
```bash
curl http://localhost:8014/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Token Claims

JWT tokens include:
- `sub`: User ID
- `phone`: User phone number (77012345678 format)
- `role`: User role (DIRECTOR, MANAGER, WORKER)
- `shop_id`: Shop identifier (for multi-tenancy)
- `exp`: Expiration timestamp (7 days from issue)

### Public Endpoints

Some endpoints don't require authentication but need `shop_id` parameter:
- `GET /products/?shop_id=8` - List products
- `POST /orders/public/create?shop_id=8` - Create order
- `GET /orders/track/{tracking_id}` - Track order
- `GET /shop/settings?shop_id=8` - Shop settings

---

## Multi-Tenancy

The platform supports multiple shops with complete data isolation via `shop_id`.

### How It Works

1. **JWT Token Contains shop_id**:
   ```json
   {
     "sub": "13",
     "shop_id": 8  // User belongs to shop 8
   }
   ```

2. **All Queries Filter by shop_id**:
   ```python
   # Automatic filtering
   products = db.query(Product).filter(Product.shop_id == current_user.shop_id).all()
   ```

3. **Cross-Shop Access Forbidden**:
   - User A (shop_id=8) cannot access User B's data (shop_id=17008)
   - Attempts return 403 Forbidden

### Environments

| Environment | shop_id | Database | Purpose |
|-------------|---------|----------|---------|
| Development | 8 | Railway PostgreSQL | Local development & testing |
| Production | 17008 | Bitrix MySQL | Live production shop |

---

## API Modules

The API is organized into 12 modules with 147 endpoints:

### 1. Authentication (`/auth`)
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### 2. Products (`/products`)
- `GET /products/` - List products (public)
- `GET /products/{id}` - Get product by ID
- `POST /products/` - Create product (admin)
- `PUT /products/{id}` - Update product (admin)
- `DELETE /products/{id}` - Delete product (admin)
- `POST /products/{id}/images` - Add product images
- `GET /products/bestsellers` - Get bestselling products
- `GET /products/featured` - Get featured products
- `POST /products/search-smart` - Smart search with filters

### 3. Orders (`/orders`)
- `GET /orders/` - List orders (admin)
- `GET /orders/{id}` - Get order details (admin)
- `POST /orders/public/create` - Create order (public)
- `PATCH /orders/{id}/status` - Update order status (admin)
- `GET /orders/track/{tracking_id}` - Track order (public)
- `POST /orders/track-by-phone` - Track by phone (public)
- `POST /orders/preview-cost` - Calculate order cost (public)
- `POST /orders/{id}/cancel` - Cancel order (public)

### 4. Warehouse (`/warehouse`)
- `GET /warehouse/items` - List inventory items (admin)
- `POST /warehouse/items/{id}/add-stock` - Add stock (admin)
- `POST /warehouse/operations` - Record operation (admin)
- `GET /warehouse/items/{id}/history` - Operation history (admin)
- `POST /warehouse/inventory-check` - Create inventory check (admin)
- `GET /warehouse/inventory-checks` - List checks (admin)

### 5. Client Profiles (`/client-profile`)
- `GET /client-profile/telegram` - Get client by Telegram ID
- `POST /client-profile/telegram` - Register Telegram client
- `GET /client-profile/{telegram_user_id}` - Get profile with history
- `POST /client-profile/save-address` - Save delivery address

### 6. Shop Settings (`/shop`)
- `GET /shop/settings` - Get shop settings (public)
- `GET /shop/working-hours` - Get working hours (public)
- `PUT /shop/settings` - Update settings (admin)

### 7. Reviews & FAQ (`/content`)
- `GET /faq` - Get FAQ list (public)
- `GET /reviews` - Get reviews with ratings (public)

### 8. Delivery (`/delivery`)
- `GET /delivery/slots` - Get available delivery slots (public)
- `POST /delivery/validate-time` - Validate delivery time (public)
- `POST /delivery/check-feasibility` - Check if delivery possible (public)

### 9. Payments (`/payments`)
- `POST /payments/kaspi/create` - Create Kaspi Pay payment
- `GET /payments/kaspi/{external_id}/status` - Check payment status
- `GET /payments/kaspi/{external_id}` - Get payment details
- `POST /payments/kaspi/{external_id}/refund` - Refund payment

### 10. Visual Search (`/visual-search`)
- `POST /visual-search/similar` - Find similar bouquets by image

### 11. Production Integration (`/production`)
- `POST /production/sync-order` - Sync order to Bitrix (internal)

### 12. Superadmin (`/superadmin`)
- `POST /superadmin/shops` - Create new shop
- `GET /superadmin/shops` - List all shops

---

## Common Patterns

### Pagination

List endpoints support pagination:

```bash
GET /products/?shop_id=8&limit=20&offset=0
```

**Parameters**:
- `limit` (int): Items per page (default: 20, max: 100)
- `offset` (int): Number of items to skip (default: 0)

**Response**:
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

### Filtering

Many endpoints support filters:

```bash
GET /products/?shop_id=8&type=BOUQUET&min_price=100000&max_price=200000
```

**Common Filters**:
- `search` (str): Search term
- `type` (enum): Product type filter
- `min_price`, `max_price` (int): Price range in kopecks
- `enabled_only` (bool): Show enabled items only

### Sorting

Some endpoints support sorting:

```bash
GET /products/?shop_id=8&sort_by=price&order=desc
```

**Sort Options**:
- `sort_by`: Field to sort by (e.g., price, created_at, name)
- `order`: Sort direction (asc, desc)

### Data Formats

#### Prices (Kopecks)
All prices stored in kopecks:
- Database: `150000` (kopecks)
- Display: `1,500 ₸` (tenge)
- Calculation: `price / 100`

#### Phone Numbers
Phones stored without +7 prefix:
- Input: `+77012345678` or `77012345678`
- Stored: `77012345678`
- Display: `+7 (701) 234-56-78`

#### Dates & Times
ISO 8601 format:
- `2025-10-28T14:30:00Z` (UTC)
- `2025-10-28` (date only)

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message here",
  "error_code": "RESOURCE_NOT_FOUND",
  "status_code": 404
}
```

### HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input parameters |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User doesn't have permission |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Common Error Messages

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```
**Solution**: Include valid JWT token in `Authorization: Bearer <token>` header

**403 Forbidden**:
```json
{
  "detail": "Access denied to shop_id 17008"
}
```
**Solution**: User's JWT token shop_id doesn't match requested resource

**404 Not Found**:
```json
{
  "detail": "Product with id 999 not found"
}
```
**Solution**: Check resource exists and you have access

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "Price must be positive integer",
      "type": "value_error"
    }
  ]
}
```
**Solution**: Fix input according to validation message

---

## Rate Limiting

**Current Status**: No rate limiting implemented

**Future Implementation**:
- 100 requests/minute per IP (public endpoints)
- 1000 requests/minute per user (authenticated endpoints)
- Burst allowance: 20 requests/second

**Headers** (when implemented):
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698765432
```

---

## Examples

### Complete Order Flow

**1. Get Products**:
```bash
curl "http://localhost:8014/api/v1/products/?shop_id=8&limit=10"
```

**2. Preview Order Cost**:
```bash
curl -X POST http://localhost:8014/api/v1/orders/preview-cost \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "items": [
      {"product_id": 3, "quantity": 1},
      {"product_id": 5, "quantity": 2}
    ]
  }'
```

**3. Check Delivery Slots**:
```bash
curl "http://localhost:8014/api/v1/delivery/slots?shop_id=8&date=2025-10-29"
```

**4. Create Order**:
```bash
curl -X POST "http://localhost:8014/api/v1/orders/public/create?shop_id=8" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "+77015211545",
    "phone": "+77015211545",
    "recipient_name": "Мария Петрова",
    "recipient_phone": "+77778889900",
    "delivery_address": "ул. Кабанбай батыра 87, ЖК Royal Palace",
    "delivery_date": "2025-10-29",
    "delivery_time": "14:00-16:00",
    "delivery_type": "delivery",
    "items": [
      {"product_id": 3, "quantity": 1},
      {"product_id": 5, "quantity": 2}
    ],
    "total_price": 450000
  }'
```

**5. Track Order**:
```bash
curl "http://localhost:8014/api/v1/orders/track/ABC123XYZ"
```

### Admin Workflow

**1. Login**:
```bash
TOKEN=$(curl -s -X POST http://localhost:8014/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "77015211545", "password": "1234"}' \
  | jq -r '.access_token')
```

**2. List Orders**:
```bash
curl "http://localhost:8014/api/v1/orders/?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**3. Update Order Status**:
```bash
curl -X PATCH "http://localhost:8014/api/v1/orders/42/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "IN_PRODUCTION",
    "notes": "Started making bouquet"
  }'
```

**4. Add Product**:
```bash
curl -X POST http://localhost:8014/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Red Roses Bouquet",
    "price": 150000,
    "type": "BOUQUET",
    "description": "Beautiful red roses",
    "enabled": true
  }'
```

---

## Testing

### Using Swagger UI

1. Open: http://localhost:8014/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN`
4. Try endpoints interactively

### Using curl

See examples above. Tips:
- Use `-v` for verbose output
- Use `jq` for JSON formatting
- Store token in variable: `TOKEN=...`
- Use `.env` for secrets

### Using Postman

Import OpenAPI spec:
1. Download: http://localhost:8014/openapi.json
2. Import in Postman
3. Configure environment variables
4. Set Authorization header

---

## Additional Resources

- **Documentation Standard**: [backend/API_DOCUMENTATION_STANDARD.md](../backend/API_DOCUMENTATION_STANDARD.md)
- **Testing Guide**: [backend/API_TESTING_GUIDE.md](../backend/API_TESTING_GUIDE.md)
- **Developer Onboarding**: [docs/DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Support

**Found an issue?**
- Check Swagger UI for latest endpoint definitions
- Review [API_DOCUMENTATION_STANDARD.md](../backend/API_DOCUMENTATION_STANDARD.md)
- Open GitHub issue: https://github.com/alekenov/figma-product-catalog/issues

**Last Updated**: 2025-10-28
**API Version**: v1
**Maintained by**: Development Team
