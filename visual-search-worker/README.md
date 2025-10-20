# Visual Search Worker

Cloudflare Worker for visual bouquet search using CLIP embeddings and Vectorize.

## Features

- **Visual Search**: Find similar bouquets by uploading an image
- **CLIP Embeddings**: Uses OpenAI's CLIP ViT-B/32 model via Workers AI
- **Vector Database**: Powered by Cloudflare Vectorize for fast similarity search
- **Edge Metadata**: D1 SQLite for low-latency metadata lookups
- **Batch Indexing**: Efficiently index large product catalogs
- **Production Ready**: CORS support, error handling, validation

## Architecture

```
┌─────────────┐
│   Client    │
│  (Upload    │
│   Image)    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│          Visual Search Worker                │
│                                              │
│  ┌────────────┐  ┌──────────────┐          │
│  │  CLIP AI   │  │  Vectorize   │          │
│  │ Embeddings │→ │ Similarity   │          │
│  └────────────┘  │    Search    │          │
│                  └──────┬───────┘          │
│                         │                   │
│  ┌─────────────────────▼────────┐          │
│  │       D1 Database             │          │
│  │  (Metadata: name, price, etc) │          │
│  └───────────────────────────────┘          │
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  R2 Bucket  │
│   (Images)  │
└─────────────┘
```

## API Endpoints

### POST /index
Index a single bouquet for visual search.

**Request**:
```json
{
  "product_id": 123,
  "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
  "name": "Букет роз",
  "price": 950000,
  "colors": ["pink", "white"],
  "occasions": ["birthday", "wedding"],
  "tags": ["premium", "bestseller"],
  "shop_id": 8
}
```

**Response**:
```json
{
  "success": true,
  "product_id": 123,
  "vector_id": "123",
  "indexed_at": "2025-10-18T12:00:00.000Z"
}
```

### POST /search
Search for similar bouquets by image.

**Request**:
```json
{
  "image_url": "https://example.com/bouquet.jpg",
  "topK": 10,
  "threshold": 0.7,
  "filters": {
    "colors": ["pink"],
    "shop_id": 8
  }
}
```

**Response**:
```json
{
  "exact": [
    {
      "product_id": 123,
      "name": "Букет роз",
      "price": 950000,
      "image_url": "https://flower-shop-images.alekenov.workers.dev/...",
      "similarity": 0.92,
      "colors": ["pink", "white"],
      "occasions": ["birthday"]
    }
  ],
  "similar": [
    {
      "product_id": 456,
      "similarity": 0.78,
      ...
    }
  ],
  "search_time_ms": 245,
  "total_indexed": 150
}
```

### POST /batch-index
Batch index bouquets from PostgreSQL or R2.

**Request**:
```json
{
  "source": "postgresql",
  "limit": 100,
  "offset": 0,
  "shop_id": 8
}
```

**Response**:
```json
{
  "success": true,
  "total": 100,
  "indexed": 98,
  "failed": 2,
  "errors": [
    {
      "product_id": 42,
      "error": "Image not found in R2"
    }
  ],
  "duration_ms": 12500
}
```

### GET /stats
Get index statistics.

**Response**:
```json
{
  "total_indexed": 150,
  "last_indexed_at": "2025-10-18T12:00:00.000Z",
  "vectorize_status": "healthy",
  "d1_rows": 150
}
```

## Setup

### Prerequisites

- Cloudflare account with Workers AI enabled
- Wrangler CLI installed: `npm install -g wrangler`
- R2 bucket `flower-shop-images` already created

### Installation

1. **Clone and navigate**:
```bash
cd visual-search-worker
npm install
```

2. **Create Vectorize index**:
```bash
npm run vectorize:create
# Creates "bouquet-embeddings" index with 512 dimensions, cosine metric
```

3. **Create D1 database**:
```bash
npm run d1:create
# Returns database_id - copy it to wrangler.toml
```

4. **Update wrangler.toml**:
```toml
[[d1_databases]]
binding = "DB"
database_name = "bouquet-metadata"
database_id = "<paste-database-id-here>"
```

5. **Run migrations**:
```bash
npm run d1:migrate
```

6. **Test locally**:
```bash
npm run dev
# Worker available at http://localhost:8787
```

### Deploy to Production

```bash
npm run deploy
# Deploys to visual-search.cvety.kz (configure domain in Cloudflare dashboard)
```

## Usage Examples

### Index a bouquet
```bash
curl -X POST https://visual-search.cvety.kz/index \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 123,
    "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
    "name": "Букет роз",
    "price": 950000,
    "colors": ["pink"],
    "shop_id": 8
  }'
```

### Search by image URL
```bash
curl -X POST https://visual-search.cvety.kz/search \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/bouquet.jpg",
    "topK": 5
  }'
```

### Search by base64 image
```bash
curl -X POST https://visual-search.cvety.kz/search \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "topK": 5
  }'
```

### Batch index from PostgreSQL
```bash
curl -X POST https://visual-search.cvety.kz/batch-index \
  -H "Content-Type: application/json" \
  -d '{
    "source": "postgresql",
    "limit": 50,
    "shop_id": 8
  }'
```

### Get statistics
```bash
curl https://visual-search.cvety.kz/stats
```

## Integration with MCP Server

Add to `mcp-server/server.py`:

```python
@mcp.tool()
async def visual_search_bouquet(
    image_url: str,
    top_k: int = 5
) -> str:
    """
    Search for similar bouquets by image.

    Args:
        image_url: URL of the bouquet image to search for
        top_k: Number of results to return (default: 5)
    """
    response = requests.post(
        "https://visual-search.cvety.kz/search",
        json={
            "image_url": image_url,
            "topK": top_k
        }
    )
    response.raise_for_status()
    return json.dumps(response.json(), ensure_ascii=False)
```

## Similarity Thresholds

Default thresholds (configured in `wrangler.toml`):
- **Exact match**: similarity >= 0.85 (very similar bouquets)
- **Similar**: 0.70 <= similarity < 0.85 (related bouquets)
- **Ignored**: similarity < 0.70 (not relevant)

Adjust thresholds in production based on testing results.

## Performance

- **Embedding generation**: ~200-500ms per image (CLIP ViT-B/32)
- **Vectorize query**: ~50-100ms (cosine similarity, 512 dims)
- **D1 metadata lookup**: ~10-20ms (edge SQLite)
- **Total search latency**: ~300-700ms (end-to-end)

Batch indexing: ~50-100 products per minute (includes image loading, embedding, upsert).

## Troubleshooting

### "Vectorize index not found"
Run `npm run vectorize:create` to create the index.

### "D1 database not found"
1. Run `npm run d1:create`
2. Copy `database_id` to `wrangler.toml`
3. Run `npm run d1:migrate`

### "Image not found in R2"
Ensure images are uploaded to `flower-shop-images` bucket with correct keys.

### Low similarity scores
- Ensure images are high quality (not thumbnails)
- Check image format (JPEG, PNG, WebP)
- Consider adjusting thresholds in `wrangler.toml`

## Monitoring

Check logs in Cloudflare dashboard or via CLI:
```bash
npm run tail
# Real-time streaming logs
```

## Cost Estimation

**Workers AI (CLIP)**:
- Free tier: 10,000 requests/day
- Paid: $0.01 per 1,000 requests

**Vectorize**:
- Free tier: 30M queried vectors/month
- Storage: 5M vectors free

**D1**:
- Free tier: 5GB storage, 5M reads/day
- Very cost-effective for metadata cache

**Estimated cost** for 1,000 searches/day: **< $1/month**

## Development

```bash
# Local development
npm run dev

# Format code
npx prettier --write src/

# Type check
npx tsc --noEmit

# Deploy
npm run deploy
```

## License

MIT
