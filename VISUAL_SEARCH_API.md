# 🔍 Visual Search API - Documentation

## Overview

Visual Search API позволяет находить визуально похожие продукты по изображению, используя:
- **Vertex AI** - генерация 512D embeddings для изображений
- **pgvector** - PostgreSQL расширение для vector similarity search
- **Cosine Distance** - метрика для измерения похожести векторов

---

## 📍 Endpoints

### 1. POST `/api/v1/products/search/similar`

Найти визуально похожие продукты по изображению.

**Request:**
```json
{
  "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
  "shop_id": 8,
  "limit": 5,
  "min_similarity": 0.5
}
```

**Parameters:**
- `image_url` (string, required) - URL изображения для поиска
- `shop_id` (int, required) - ID магазина
- `limit` (int, optional) - Количество результатов (1-50, default: 5)
- `min_similarity` (float, optional) - Минимальный порог похожести (0-1, default: 0.0)

**Response:**
```json
{
  "success": true,
  "query_image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
  "total_results": 3,
  "results": [
    {
      "id": 999888,
      "name": "Test Product - Integration Test",
      "price": 1500000,
      "image": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
      "type": "flowers",
      "enabled": true,
      "similarity": 1.0
    },
    {
      "id": 123,
      "name": "Розы красные 7шт",
      "price": 450000,
      "image": "https://...",
      "type": "flowers",
      "enabled": true,
      "similarity": 0.87
    }
  ],
  "search_duration_ms": 1523
}
```

**Similarity Score:**
- `1.0` - идентичные изображения
- `0.8-0.99` - очень похожие
- `0.6-0.79` - похожие
- `0.4-0.59` - умеренная схожесть
- `< 0.4` - слабая схожесть

---

### 2. GET `/api/v1/products/search/stats`

Получить статистику по visual search для магазина.

**Request:**
```
GET /api/v1/products/search/stats?shop_id=8
```

**Response:**
```json
{
  "success": true,
  "shop_id": 8,
  "total_products": 150,
  "products_with_embeddings": 1,
  "coverage_percentage": 0.67,
  "search_ready": true
}
```

---

## 🧪 Testing

### Quick Test
```bash
chmod +x test_visual_search.sh
./test_visual_search.sh
```

### Manual cURL Test
```bash
curl -X POST "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
    "shop_id": 8,
    "limit": 5,
    "min_similarity": 0.0
  }' | jq .
```

---

## 🔧 How It Works

### Architecture Flow

```
1. User uploads/provides image URL
   ↓
2. Backend calls Embedding Service
   POST /embed/image
   ↓
3. Embedding Service:
   - Downloads image
   - Sends to Vertex AI
   - Returns 512D vector
   ↓
4. Backend executes pgvector query:
   SELECT * FROM products
   WHERE embedding <=> query_vector
   ORDER BY distance ASC
   ↓
5. Returns top N similar products
   with similarity scores
```

### SQL Query (pgvector)

```sql
SELECT
  p.id,
  p.name,
  p.price,
  p.image,
  p.type,
  p.enabled,
  1 - (pe.embedding <=> :query_vector::vector) AS similarity
FROM product p
JOIN product_embeddings pe ON p.id = pe.product_id
WHERE p.shop_id = :shop_id
  AND p.enabled = true
  AND pe.embedding_type = 'image'
  AND (1 - (pe.embedding <=> :query_vector::vector)) >= :min_similarity
ORDER BY pe.embedding <=> :query_vector::vector ASC
LIMIT :limit
```

**Key Points:**
- `<=>` - cosine distance operator from pgvector
- `1 - distance` - converts distance to similarity (0-1)
- `ORDER BY distance ASC` - closest vectors first
- `::vector` - explicit type cast for query vector

---

## 📊 Performance

**Typical Response Times:**
- Embedding generation: ~1200-1800ms (Vertex AI)
- Vector similarity search: ~50-200ms (pgvector)
- **Total**: ~1500-2000ms

**Optimization Tips:**
1. **Create index on embeddings** (для больших датасетов):
   ```sql
   CREATE INDEX ON product_embeddings
   USING ivfflat (embedding vector_cosine_ops)
   WITH (lists = 100);
   ```

2. **Cache embeddings** - для часто используемых query изображений

3. **Batch processing** - обрабатывать несколько изображений параллельно

---

## 🚀 Production URLs

- **Backend**: `https://figma-product-catalog-production.up.railway.app`
- **Embedding Service**: `https://embedding-service-production-4aaa.up.railway.app`
- **Swagger UI**: `https://figma-product-catalog-production.up.railway.app/docs`

---

## 🔐 Requirements

### For Products to Appear in Search:

1. ✅ Product must have `enabled = true`
2. ✅ Product must have an embedding in `product_embeddings` table
3. ✅ Embedding must be of type `'image'`
4. ✅ Product must belong to specified `shop_id`

### To Generate Embeddings:

**Option 1: Via Webhook** (automatic)
```bash
POST /api/v1/webhooks/product-sync
X-Webhook-Secret: cvety-webhook-2025-secure-key
{
  "event_type": "product.created",
  "product_data": {...}
}
```

**Option 2: Via Embedding Service** (manual)
```bash
POST https://embedding-service-production-4aaa.up.railway.app/embed/image
{
  "image_url": "https://...",
  "product_id": 123
}
```

---

## 📝 Error Handling

**Common Errors:**

1. **400 Bad Request** - Invalid image URL or failed to download
   ```json
   {"detail": "Failed to download image: ..."}
   ```

2. **404 Not Found** - No products with embeddings found
   ```json
   {"total_results": 0, "results": []}
   ```

3. **500 Internal Server Error** - Database or embedding service error
   ```json
   {"detail": "Visual search failed: ..."}
   ```

---

## 🎯 Use Cases

1. **"Find Similar Products"** - пользователь загружает фото букета, находим похожие
2. **Duplicate Detection** - автоматическое нахождение дубликатов в каталоге
3. **Visual Recommendations** - "Похожие товары" на странице продукта
4. **Smart Search** - поиск по изображению вместо текста

---

## 🔮 Future Enhancements

- [ ] Support multimodal search (image + text)
- [ ] Add HNSW index for faster search (pgvector 0.5.0+)
- [ ] Batch similarity search endpoint
- [ ] Real-time reranking using metadata (price, category)
- [ ] A/B testing framework for similarity thresholds
