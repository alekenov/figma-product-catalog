# Troubleshooting Guide

## Error: "This account is not allowed to access this model"

### Problem
When trying to index a bouquet, you get:
```json
{
  "success": false,
  "error": "Failed to generate embedding: 5018: This account is not allowed to access this model."
}
```

### Root Cause
Your Cloudflare account doesn't have access to Workers AI CLIP model (`@cf/openai/clip-vit-base-patch32`).

### Solution

#### Option 1: Enable Workers AI (Recommended)

1. **Go to Cloudflare Dashboard**:
   - Visit https://dash.cloudflare.com/
   - Select your account

2. **Enable Workers AI**:
   - Navigate to **Workers & Pages** → **AI**
   - Click **"Enable Workers AI"**
   - Accept terms and conditions

3. **Verify Access**:
   ```bash
   # Test the worker again
   curl -X POST https://visual-search.alekenov.workers.dev/index \
     -H "Content-Type: application/json" \
     -d '{
       "product_id": 3,
       "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
       "name": "Test Bouquet",
       "price": 100000,
       "shop_id": 8
     }'
   ```

4. **Check Pricing**:
   - Workers AI has a **generous free tier**:
     - 10,000 Neurons free per day
     - CLIP model uses ~1 Neuron per request
   - Paid tier: $0.01 per 1,000 requests
   - See: https://developers.cloudflare.com/workers-ai/platform/pricing/

#### Option 2: Use Alternative Architecture

If Workers AI is not available or too expensive, consider:

**A. Use External CLIP API**:
- Deploy CLIP model on Replicate, HuggingFace, or Modal
- Modify `src/services/embeddings.ts` to call external API
- Example with Replicate:
  ```typescript
  const response = await fetch('https://api.replicate.com/v1/predictions', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${REPLICATE_API_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      version: 'clip-vit-base-patch32',
      input: { image: base64Image }
    })
  });
  ```

**B. Use Cloudflare Images Variants** (simpler but less accurate):
- Use perceptual hashing instead of CLIP
- Good for exact duplicates, poor for similarity
- Much cheaper, no AI required

**C. Deploy CLIP on Railway/Fly.io**:
- Create separate microservice with CLIP
- Worker calls your service via HTTP
- More control, but higher latency

#### Option 3: Test Locally First

Test with wrangler dev to debug without deploying:
```bash
cd visual-search-worker
npx wrangler dev

# In another terminal
curl -X POST http://localhost:8787/index \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, ...}'
```

## Current Deployment Status

✅ **Successfully deployed**:
- Worker: https://visual-search.alekenov.workers.dev
- Vectorize index: `bouquet-embeddings` (512 dims, cosine)
- D1 database: `figma-catalog-db` (with `bouquets` table)
- R2 bucket: `flower-shop-images` (shared)

❌ **Blocked by**:
- Workers AI access for CLIP model

## Next Steps

1. Enable Workers AI in Cloudflare Dashboard
2. Test indexing: `POST /index`
3. Index all products: `POST /batch-index`
4. Test search: `POST /search`
5. Integrate with MCP server

## Alternative: Manual Testing Script

If Workers AI is unavailable, test the infrastructure without AI:

```bash
# Test health
curl https://visual-search.alekenov.workers.dev/

# Check stats
curl https://visual-search.alekenov.workers.dev/stats

# Verify D1 connection (manual SQL via wrangler)
npx wrangler d1 execute figma-catalog-db --command "SELECT COUNT(*) FROM bouquets"
```

## Contact Support

If you continue to have issues:
- Cloudflare Workers AI: https://discord.gg/cloudflaredev
- Check account limits: https://dash.cloudflare.com → Account → Limits
- Review billing: Workers AI is included in Workers Paid plan ($5/month + usage)

## Estimated Costs (with Workers AI enabled)

For 1,000 searches/day:
- Workers AI CLIP: $0.01 per 1,000 requests = $0.30/month
- Vectorize queries: Free tier (30M vectors/month)
- D1 storage: Free tier (5GB)
- R2 storage: $0.015/GB/month
- **Total**: < $1/month

Free tier covers ~10,000 searches/month.
