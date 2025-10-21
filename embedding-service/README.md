# Embedding Service

Standalone microservice for generating ML embeddings using Google Vertex AI.

## Overview

This service provides a REST API for generating 512-dimensional vector embeddings from images and text using Google's multimodal-embedding@001 model. It's designed to be deployed separately on Railway for scalability and independent scaling from the main backend.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Backend API   │─────▶│ Embedding Service│─────▶│  Vertex AI API  │
│   (Railway)     │      │    (Railway)     │      │  (Google Cloud) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│   PostgreSQL    │      │  Image Storage   │
│  (pgvector DB)  │      │ (Cloudflare R2)  │
└─────────────────┘      └──────────────────┘
```

## Features

- ✅ **Image Embeddings**: Generate 512D embeddings from image URLs
- ✅ **Text Embeddings**: Generate 512D embeddings from text (for future search)
- ✅ **Batch Processing**: Process multiple images/texts in parallel
- ✅ **Concurrency Control**: Configurable rate limiting to avoid API overload
- ✅ **Retry Logic**: Automatic retries with exponential backoff
- ✅ **Error Handling**: Graceful degradation with detailed error messages
- ✅ **Health Monitoring**: Health check and statistics endpoints
- ✅ **Vector Normalization**: L2-normalized vectors for cosine similarity

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "embedding-service",
  "vertex_ai_configured": true
}
```

### Generate Image Embedding
```http
POST /embed/image
Content-Type: application/json

{
  "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
  "product_id": 123
}
```

Response:
```json
{
  "success": true,
  "embedding": [0.123, -0.456, ..., 0.789],
  "dimensions": 512,
  "model": "vertex-multimodal-001",
  "duration_ms": 1234
}
```

### Batch Generate Embeddings
```http
POST /embed/batch
Content-Type: application/json

{
  "image_urls": [
    "https://example.com/image1.png",
    "https://example.com/image2.png"
  ]
}
```

Response:
```json
{
  "success": true,
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "image_url": "https://example.com/image1.png",
      "success": true,
      "embedding": [0.1, 0.2, ...],
      "error": null
    },
    {
      "image_url": "https://example.com/image2.png",
      "success": true,
      "embedding": [0.3, 0.4, ...],
      "error": null
    }
  ],
  "duration_ms": 2456
}
```

### Service Statistics
```http
GET /stats
```

Response:
```json
{
  "service": "embedding-service",
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "total_requests": 150,
  "successful_requests": 148,
  "failed_requests": 2,
  "average_duration_ms": 1234.5
}
```

## Local Development

### Prerequisites

- Python 3.10+
- GCP account with Vertex AI API enabled
- Service account key with Vertex AI permissions

### Setup

1. **Install dependencies:**
   ```bash
   cd embedding-service
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   VERTEX_PROJECT_ID=your-gcp-project-id
   VERTEX_LOCATION=us-central1
   VERTEX_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
   PORT=8001
   LOG_LEVEL=INFO
   ENV=development
   ```

3. **Run service:**
   ```bash
   python main.py
   ```

   Service will start on http://localhost:8001

4. **Test endpoints:**
   ```bash
   # Health check
   curl http://localhost:8001/health

   # Generate embedding
   curl -X POST http://localhost:8001/embed/image \
     -H "Content-Type: application/json" \
     -d '{
       "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
       "product_id": 123
     }'
   ```

## Railway Deployment

### Environment Variables

Configure these in Railway dashboard:

```bash
# Required
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1
VERTEX_SERVICE_ACCOUNT_KEY='{"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}'

# Optional
PORT=8001                    # Auto-assigned by Railway
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
ENV=production              # development or production
```

### Deployment Steps

1. **Create new Railway service:**
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `figma-product-catalog` repository
   - Choose `embedding-service/` as root directory

2. **Configure service:**
   - Set root directory to `embedding-service`
   - Railway will auto-detect Python and use Nixpacks
   - Add environment variables (see above)

3. **Deploy:**
   - Push to `main` branch
   - Railway will automatically build and deploy
   - Check logs for successful startup

4. **Get service URL:**
   - Railway assigns public URL: `https://embedding-service-production-xxxx.up.railway.app`
   - Update backend to use this URL

## GCP Service Account Setup

### Create Service Account

1. **Go to GCP Console** → IAM & Admin → Service Accounts
2. **Create Service Account:**
   - Name: `vertex-ai-embedding-service`
   - Description: "Service account for generating embeddings via Vertex AI"
3. **Grant Roles:**
   - `Vertex AI User` (roles/aiplatform.user)
4. **Create Key:**
   - Click on service account → Keys → Add Key → Create new key
   - Choose JSON format
   - Download key file

### Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### Convert Key to Environment Variable

```bash
# Minify JSON (remove whitespace)
cat service-account-key.json | jq -c . > key-minified.json

# Copy content to clipboard
cat key-minified.json | pbcopy

# Paste into Railway environment variable: VERTEX_SERVICE_ACCOUNT_KEY
```

## Architecture Details

### Services

**`VertexAIClient`** (`services/vertex_ai.py`):
- Handles OAuth2 authentication with GCP
- Calls Vertex AI multimodal-embedding API
- Normalizes vectors (L2 norm)
- Supports both image and text embeddings

**`EmbeddingService`** (`services/embedding.py`):
- High-level business logic
- Batch processing with concurrency control (default: 5 concurrent)
- Retry logic with exponential backoff (default: 2 retries)
- Downloads images from URLs
- Error handling and logging

### Concurrency & Rate Limiting

```python
# Default settings (configurable)
max_concurrent = 5      # Max parallel requests to Vertex AI
max_retries = 2        # Retry attempts per request
timeout = 30.0         # HTTP timeout in seconds
```

Vertex AI quotas (us-central1):
- **Online prediction requests**: 60 per minute
- **Recommendation**: Keep max_concurrent ≤ 5 to stay under limits

### Vector Normalization

All embeddings are L2-normalized before returning:

```python
def normalize_vector(v):
    norm = sqrt(sum(x^2 for x in v))
    return [x / norm for x in v]
```

This enables:
- ✅ Cosine similarity = dot product (faster)
- ✅ Consistent distance metrics
- ✅ Optimal for pgvector cosine search

## Error Handling

### Common Errors

**1. Authentication Failed**
```
Error: Failed to get access token: invalid_grant
```
**Solution**: Check `VERTEX_SERVICE_ACCOUNT_KEY` is valid JSON and service account has Vertex AI permissions.

**2. API Quota Exceeded**
```
Error: 429 Too Many Requests
```
**Solution**: Reduce `max_concurrent` in `EmbeddingService` initialization.

**3. Image Download Failed**
```
Error: Failed to download image: 404 Not Found
```
**Solution**: Verify image URL is accessible and not expired (Cloudflare signed URLs).

**4. Invalid Response Format**
```
Error: Unexpected API response format
```
**Solution**: Check Vertex AI model version matches (`multimodalembedding@001`).

### Retry Behavior

```python
# Exponential backoff for retries
attempt 1: wait 2^0 = 1s
attempt 2: wait 2^1 = 2s
attempt 3: fail (max retries = 2)
```

## Performance

### Benchmarks (us-central1)

| Operation | Single Image | Batch (10 images) | Batch (50 images) |
|-----------|-------------|-------------------|-------------------|
| **Download** | ~100ms | ~150ms | ~200ms |
| **Vertex AI** | ~800ms | ~1200ms | ~2500ms |
| **Total** | ~1000ms | ~1500ms | ~3000ms |
| **Per image** | 1000ms | 150ms | 60ms |

**Recommendation**: Use batch endpoints for bulk operations (5-10x faster per image).

### Optimization Tips

1. **Batch processing**: Always use `/embed/batch` for multiple images
2. **Concurrency**: Increase `max_concurrent` if you have higher quotas
3. **Caching**: Cache embeddings in database to avoid regeneration
4. **Image size**: Resize images to max 1024x1024 before uploading (faster transfer)

## Monitoring

### Health Check

```bash
# Check if service is running
curl https://your-service.up.railway.app/health

# Expected response
{"status":"healthy","service":"embedding-service","vertex_ai_configured":true}
```

### Statistics

```bash
# Get service statistics
curl https://your-service.up.railway.app/stats

# Monitor metrics
{
  "uptime_seconds": 3600,
  "total_requests": 150,
  "successful_requests": 148,
  "failed_requests": 2,
  "average_duration_ms": 1234.5
}
```

### Railway Logs

```bash
# View logs in Railway dashboard
railway logs --service embedding-service

# Look for:
# - "✅ Embedding Service initialized"
# - "Generated embedding: 512 dims, XXXms"
# - Error messages with stack traces
```

## Integration with Backend

### 1. Store Embedding Service URL

```bash
# In backend/.env
EMBEDDING_SERVICE_URL=https://embedding-service-production-xxxx.up.railway.app
```

### 2. Call from Backend

```python
# backend/api/embeddings/router.py
import httpx

async def generate_product_embedding(image_url: str, product_id: int):
    """Generate embedding for product image."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.EMBEDDING_SERVICE_URL}/embed/image",
            json={
                "image_url": image_url,
                "product_id": product_id
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]
```

### 3. Store in PostgreSQL

```python
# Save to database
from models import ProductEmbedding

embedding = await generate_product_embedding(image_url, product.id)

product_embedding = ProductEmbedding(
    product_id=product.id,
    embedding=embedding,
    embedding_type="image",
    model_version="vertex-multimodal-001",
    source_url=image_url
)
session.add(product_embedding)
await session.commit()
```

## Cost Estimation

### Vertex AI Pricing (us-central1)

**Multimodal Embeddings**:
- **$0.00025 per 1000 predictions**
- **512D vector** = 1 prediction

**Example costs**:
- 1,000 products = $0.25
- 10,000 products = $2.50
- 100,000 products = $25.00

**Railway costs**:
- Embedding Service: ~$5/month (512MB RAM, minimal CPU)

**Total monthly cost** (10k products, reindex monthly): **~$7.50/month**

## Future Enhancements

- [ ] Support for custom embedding dimensions (128D, 256D, 1024D)
- [ ] Text embedding endpoint for product descriptions
- [ ] Redis caching for frequently requested embeddings
- [ ] Webhook callbacks for async processing
- [ ] Prometheus metrics export
- [ ] OpenTelemetry tracing
- [ ] Multi-model support (CLIP, custom models)

## Troubleshooting

### Service won't start on Railway

1. Check environment variables are set correctly
2. View Railway logs for error messages
3. Verify service account key is valid JSON (use `jq -c .` to minify)
4. Ensure Vertex AI API is enabled in GCP project

### Embeddings differ from Cloudflare Worker

This is expected! Different reasons:
- Different model versions
- Different normalization methods
- Different random seeds in model

**Solution**: Reindex all products with new service for consistency.

### Slow performance

1. Check Railway region matches Vertex AI region (us-central1)
2. Use batch endpoints for multiple images
3. Monitor Railway CPU/RAM usage
4. Consider upgrading Railway plan for more resources

## Support

For issues or questions:
1. Check Railway logs: `railway logs --service embedding-service`
2. Test locally with same environment variables
3. Verify GCP quotas: https://console.cloud.google.com/iam-admin/quotas
4. Review Vertex AI documentation: https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings

---

**Last Updated**: 2025-01-21
**Version**: 1.0.0
**Author**: Cvety.kz Team
