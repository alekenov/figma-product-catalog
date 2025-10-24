# Cvety.kz Products API Reference (Production)

## Base Configuration

**Base URL**: `https://cvety.kz/api/v2`
**Authentication**: Bearer token in `Authorization` header
**Token**: `ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144`
**Default City ID**: `2` (Almaty)

## Endpoints

### 1. GET /products/

Get paginated list of products with filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `type` | string | No | - | Filter by product type: `vitrina` (ready products) or `catalog` (made-to-order) |
| `isAvailable` | boolean | No | - | Filter by ACTIVE status (true/false) |
| `limit` | integer | No | 20 | Number of items per page (1-100) |
| `offset` | integer | No | 0 | Pagination offset |
| `cityId` | integer | No | 2 | City ID for filtering |
| `search` | string | No | - | Search by product name |

**Example Request:**
```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/?type=catalog&limit=10&offset=0"
```

**Response:**
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

### 2. GET /products/detail

Get detailed information about a single product.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Product ID |

**Example Request:**
```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/detail?id=698977"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 698977,
    "image": "https://cvety.kz/upload/.../image.jpg",
    "images": ["https://cvety.kz/upload/.../image.jpg"],
    "title": "Собранный букет",
    "price": "20 000 ₸",
    "isAvailable": true,
    "createdAt": "2025-10-24T15:42:55+0500",
    "type": "vitrina",
    "width": "",
    "height": "",
    "video": null,
    "duration": null,
    "discount": null,
    "composition": null,
    "colors": false,
    "catalogWidth": null,
    "catalogHeight": null,
    "productionTime": null
  }
}
```

### 3. DELETE /products/delete

Deactivate a product (soft delete by setting ACTIVE='N').

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Product ID to deactivate |

**Example Request:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/delete?id=698977"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 698977,
    "deleted": true
  }
}
```

### 4. GET /products/composition

Get product composition (recipe) and available quantity.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Product ID |

**Example Request:**
```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/composition?id=698977"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 698977,
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

### 5. POST /products/composition

Set product composition (recipe).

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144`

**Body:**
```json
{
  "id": 698977,
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

**Example Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  -H "Content-Type: application/json" \
  -d '{"id":698977,"composition":[{"id":123,"amount":7}]}' \
  "https://cvety.kz/api/v2/products/composition"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 698977,
    "count": 2,
    "stored_as": "json"
  }
}
```

## Product Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique product ID |
| `image` | string | Main product image URL |
| `images` | array | All product images (including main) |
| `title` | string | Product name |
| `price` | string | Formatted price with currency (e.g., "7 500 ₸") |
| `isAvailable` | boolean | Product availability (ACTIVE status) |
| `createdAt` | string | Creation date in ISO8601 format |
| `type` | string | Product type: `vitrina` (ready) or `catalog` (made-to-order) |
| `width` | string | Product width (for vitrina products) |
| `height` | string | Product height (for vitrina products) |
| `video` | string | Video URL (currently unused) |
| `duration` | string | Assembly time in minutes (for catalog products) |
| `discount` | string | Discount percentage |
| `composition` | array | Product recipe (inventory items with quantities) |
| `colors` | array/boolean | Available color options |
| `catalogWidth` | string | Width for catalog products |
| `catalogHeight` | string | Height for catalog products |
| `productionTime` | string | Production time category: `short` (≤30 min), `medium` (≤60 min), `long` (>60 min) |

## Product Type Logic

- **`type=vitrina`**: Ready-made products (IS_READY property set)
  - Displayed on the "vitrina" (showcase)
  - Have width/height in `width`, `height` fields
  - No duration or productionTime

- **`type=catalog`**: Made-to-order products (IS_READY property not set)
  - Standard catalog items
  - Have width/height in `catalogWidth`, `catalogHeight` fields
  - May have `duration` (assembly time) and `productionTime` category

## Error Responses

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
    "message": "Product not found"
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

## Implementation Notes

1. **Authorization**: All endpoints require the Bearer token in the `Authorization` header
2. **CORS**: All endpoints support CORS with `Access-Control-Allow-Origin: *`
3. **Pagination**: Use `offset` and `limit` for paginating through large result sets
4. **Soft Delete**: The DELETE endpoint sets `ACTIVE='N'` (soft delete), not a hard delete
5. **Composition**: Stored as JSON in a text property, requires warehouse inventory IDs
6. **City Context**: Use `cityId` parameter or `X-City` header for city-specific filtering
7. **Image URLs**: All images are served from `https://cvety.kz/upload/` directory
8. **Price Format**: Prices are pre-formatted strings with currency symbol

## Testing Examples

**Get all vitrina products:**
```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/?type=vitrina&limit=100"
```

**Search for roses:**
```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/?search=роза"
```

**Get only available products:**
```bash
curl -H "Authorization: Bearer ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  "https://cvety.kz/api/v2/products/?isAvailable=true"
```
