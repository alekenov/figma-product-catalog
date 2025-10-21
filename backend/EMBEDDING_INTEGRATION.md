# Embedding Integration Guide

## Phase 3 Complete! ✅

This document describes how embeddings are automatically generated and stored when products are created or updated via webhooks from Production Bitrix.

---

## Architecture Flow

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ Production      │      │   Backend API    │      │ Embedding       │
│ Bitrix          │─────▶│   (Railway)      │─────▶│ Service         │
│ (cvety.kz)      │      │                  │      │ (Railway)       │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                        │                         │
         │                        ▼                         ▼
         │               ┌──────────────────┐      ┌─────────────────┐
         │               │   PostgreSQL     │      │  Vertex AI      │
         │               │   + pgvector     │      │  (Google Cloud) │
         │               └──────────────────┘      └─────────────────┘
         │                        │
         └────────────────────────┘
              product.created/updated
              webhook event
```

---

## How It Works

### 1. Webhook Receives Product Event

When a product is created or updated in Production Bitrix, a webhook sends data to:

```http
POST /api/webhooks/product-sync
Content-Type: application/json
X-Webhook-Secret: your-secret-key

{
  "event_type": "product.created",  // or "product.updated"
  "product_data": {
    "id": 668826,
    "title": "Эустомы в пачках ФИОЛЕТОВЫЕ",
    "price": "4 950 ₸",
    "isAvailable": true,
    "image": "https://cvety.kz/upload/.../IMG_0254.jpeg",
    "images": ["url1", "url2", "url3"],
    "catalogHeight": "70 см"
  }
}
```

### 2. Backend Processes Event

**`backend/api/webhooks.py:product_sync_webhook()`**:

1. **Validates webhook secret** (security)
2. **Creates/updates product** in PostgreSQL
3. **Triggers background tasks**:
   - Generate embedding (async)
   - Reindex visual search (async)

### 3. Embedding Generation (Background Task)

**`backend/api/webhooks.py:generate_and_save_embedding()`**:

1. **Calls Embedding Service** via `EmbeddingClient`
   ```python
   embedding = await embedding_client.generate_image_embedding(
       image_url="https://cvety.kz/upload/.../IMG_0254.jpeg",
       product_id=668826
   )
   # Returns: [0.123, -0.456, ..., 0.789]  # 512D vector
   ```

2. **Saves to PostgreSQL** (pgvector)
   ```python
   product_embedding = ProductEmbedding(
       product_id=668826,
       embedding=embedding,  # 512D vector
       embedding_type="image",
       model_version="vertex-multimodal-001",
       source_url="https://cvety.kz/upload/.../IMG_0254.jpeg"
   )
   session.add(product_embedding)
   await session.commit()
   ```

3. **Enables vector search** for this product

---

## Components

### 1. Embedding Client (`backend/services/embedding_client.py`)

**EmbeddingClient** - HTTP client for Embedding Service:

```python
from services.embedding_client import EmbeddingClient

client = EmbeddingClient(
    service_url="https://embedding-service-production-xxxx.up.railway.app"
)

# Generate single embedding
embedding = await client.generate_image_embedding(
    image_url="https://example.com/image.png",
    product_id=123
)

# Batch generate embeddings
results = await client.generate_batch_embeddings(
    image_urls=["url1", "url2", "url3"]
)

# Health check
is_healthy = await client.health_check()

# Get stats
stats = await client.get_stats()
```

### 2. Webhook Handler (`backend/api/webhooks.py`)

**product_sync_webhook()** - Handles product sync events:

- **Events**: `product.created`, `product.updated`, `product.deleted`
- **Security**: Validates `X-Webhook-Secret` header
- **Background tasks**: Embedding generation + visual search reindex
- **Idempotency**: Handles duplicate events gracefully

**generate_and_save_embedding()** - Background task:

- Calls Embedding Service
- Saves ProductEmbedding to database
- Updates existing embeddings if found
- Logs errors but doesn't fail webhook

### 3. Database Model (`backend/models/embeddings.py`)

**ProductEmbedding** - SQLAlchemy model:

```python
from models import ProductEmbedding

# Query embeddings
from sqlmodel import select
stmt = select(ProductEmbedding).where(
    ProductEmbedding.product_id == 123,
    ProductEmbedding.embedding_type == "image"
)
result = await session.execute(stmt)
embedding = result.scalar_one_or_none()

# Access embedding vector
if embedding:
    vector = embedding.embedding  # List[float] with 512 dimensions
```

---

## Environment Variables

### Backend Configuration

Add to `backend/.env`:

```bash
# Embedding Service URL
EMBEDDING_SERVICE_URL=https://embedding-service-production-xxxx.up.railway.app

# Webhook secret (must match Production Bitrix configuration)
WEBHOOK_SECRET=your-generated-secret-key
```

### Generate Webhook Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: wR9xK7nP8mQvT2yU5hJwL4aZ6bN3cM1sX8fG0dK9iR
```

---

## Testing

### 1. Test Embedding Client

```python
# backend/test_embedding_client.py
import asyncio
from services.embedding_client import EmbeddingClient

async def test_client():
    client = EmbeddingClient(
        service_url="http://localhost:8001"  # Local development
    )

    # Health check
    is_healthy = await client.health_check()
    print(f"Service healthy: {is_healthy}")

    # Generate embedding
    embedding = await client.generate_image_embedding(
        image_url="https://cvety.kz/upload/.../IMG_0254.jpeg",
        product_id=123
    )
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

if __name__ == "__main__":
    asyncio.run(test_client())
```

Run:
```bash
cd backend
python test_embedding_client.py

# Expected output:
# Service healthy: True
# Embedding dimensions: 512
# First 5 values: [0.123, -0.456, 0.789, ...]
```

### 2. Test Webhook Endpoint

```bash
# Send test webhook
curl -X POST http://localhost:8014/api/webhooks/product-sync \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: change-me-in-production" \
  -d '{
    "event_type": "product.created",
    "product_data": {
      "id": 999999,
      "title": "Test Product",
      "price": "5 000 ₸",
      "isAvailable": true,
      "image": "https://cvety.kz/upload/test.jpeg",
      "images": ["https://cvety.kz/upload/test.jpeg"],
      "catalogHeight": "60 см"
    }
  }'

# Expected response:
# {
#   "status": "success",
#   "action": "created",
#   "product_id": 999999,
#   "reindex_triggered": true,
#   "embedding_generated": true
# }
```

### 3. Verify Embedding in Database

```sql
-- Connect to PostgreSQL
psql $DATABASE_URL

-- Check if embedding was created
SELECT
    id,
    product_id,
    embedding_type,
    model_version,
    created_at,
    LENGTH(embedding::text) as embedding_length
FROM product_embeddings
WHERE product_id = 999999;

-- Expected output:
--  id | product_id | embedding_type |    model_version      |       created_at        | embedding_length
-- ----+------------+----------------+-----------------------+-------------------------+------------------
--   1 |     999999 | image          | vertex-multimodal-001 | 2025-01-21 12:30:00.000 |            ~8000
```

---

## Monitoring

### 1. Backend Logs

```bash
# Watch backend logs for embedding generation
railway logs --service figma-product-catalog

# Look for:
# 🔄 Generating embedding for product 668826
# ✅ Generated embedding for product 668826: 512 dims, 1234ms
# ✅ Created embedding for product 668826
```

### 2. Embedding Service Logs

```bash
# Watch embedding service logs
railway logs --service embedding-service

# Look for:
# Generating embedding for: https://cvety.kz/upload/.../IMG_0254.jpeg...
# Downloaded 145678 bytes
# Generated embedding for product 668826: 512 dims, 823ms
```

### 3. Embedding Service Stats

```bash
# Get service statistics
curl https://embedding-service-production-xxxx.up.railway.app/stats

# Response:
# {
#   "service": "embedding-service",
#   "status": "healthy",
#   "uptime_seconds": 3600.5,
#   "total_requests": 150,
#   "successful_requests": 148,
#   "failed_requests": 2,
#   "average_duration_ms": 1234.5
# }
```

---

## Error Handling

### Graceful Degradation

Embedding generation is **non-blocking**:
- Webhook succeeds even if embedding generation fails
- Errors are logged but don't affect product creation/update
- Can retry embedding generation later via batch indexing

### Common Errors

**1. Embedding Service Unreachable**
```
❌ Failed to generate embedding for product 668826: Connection refused
```
**Solution**: Check `EMBEDDING_SERVICE_URL` and service health

**2. Invalid Image URL**
```
❌ HTTP error while generating embedding: 404 Not Found
```
**Solution**: Verify image URL is accessible

**3. Vertex AI Quota Exceeded**
```
❌ HTTP error: 429 Too Many Requests
```
**Solution**: Reduce concurrent requests or upgrade quota

---

## Data Flow Example

### Complete Flow for New Product

**1. Production Bitrix**: Create product ID 668826

**2. Webhook sent**:
```json
{
  "event_type": "product.created",
  "product_data": {"id": 668826, "image": "https://..."}
}
```

**3. Backend API** (`product_sync_webhook`):
- ✅ Validate secret
- ✅ Create Product in PostgreSQL
- ✅ Create ProductImages
- 🔄 Queue background task: `generate_and_save_embedding(668826, "https://...")`
- ✅ Return success response

**4. Background Task** (`generate_and_save_embedding`):
- 🔄 Call Embedding Service: `POST /embed/image`
- ⏳ Wait for Vertex AI (500-1500ms)
- ✅ Receive 512D vector
- ✅ Save ProductEmbedding to PostgreSQL
- ✅ Log success

**5. Result**:
- Product 668826 is now searchable via vector similarity
- Can find similar products using pgvector cosine search

---

## Next Steps

### Phase 4: Search API with pgvector

Create REST API endpoints for vector similarity search:

```http
POST /api/v1/search/similar
{
  "product_id": 668826,
  "limit": 10
}

Response:
{
  "products": [
    {
      "id": 668830,
      "name": "Эустомы белые",
      "similarity": 0.92,
      "image": "https://..."
    },
    ...
  ]
}
```

### Phase 5: Batch Indexing Script

Create script to index all existing products:

```bash
python scripts/batch_index_products.py

# Expected output:
# 📦 Found 150 products without embeddings
# 🔄 Generating embeddings in batches of 10...
# ✅ Batch 1/15 completed: 10 success, 0 failed (12.5s)
# ✅ Batch 2/15 completed: 10 success, 0 failed (11.8s)
# ...
# ✅ Completed! 148 success, 2 failed in 187.3s
```

---

## Resources

- [Phase 1: PostgreSQL + pgvector Setup](PGVECTOR_SETUP.md)
- [Phase 2: Embedding Service](../embedding-service/README.md)
- [Vertex AI Multimodal Embeddings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

**Last Updated**: 2025-01-21
**Version**: 1.0.0
**Status**: ✅ Phase 3 Complete
