# MCP Production Server

Production API proxy for cvety.kz (Bitrix CMS). Exposes cvety.kz REST API as MCP tools for AI agents.

## Architecture

```
AI Agent/Telegram Bot → MCP Production → cvety.kz API (Bitrix)
```

## Available Tools

### Products (4 tools)
- `list_products` - List products with filters
- `create_product` - Create new product
- `update_product_status` - Change product status
- `delete_product` - Delete product (destructive)

### Orders (3 tools)
- `list_orders` - List orders with filters
- `get_order_details` - Get order details
- `update_order_status` - Change order status

### Health (1 tool)
- `health_check` - Check API connectivity

## Local Development

### 1. Setup Environment

```bash
cd mcp-production
cp .env.example .env
# Edit .env with your credentials
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test with MCP Inspector

```bash
python -m fastmcp dev server.py
```

Opens MCP Inspector UI at http://localhost:5173

### 4. Test Tools

```python
# In MCP Inspector:

# List products
await list_products(product_type="vitrina", limit=10)

# Get orders
await list_orders(status="in-transit")

# Health check
await health_check()
```

## Railway Deployment

### Environment Variables

Set these in Railway dashboard:

```
CVETY_PRODUCTION_TOKEN=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144
CVETY_API_BASE_URL=https://cvety.kz/api/v2
CVETY_SHOP_ID=17008
CVETY_CITY_ID=2
RAILWAY_MCP_URL=https://mcp-server-production.railway.app
RAILWAY_WEBHOOK_SECRET=<random-secret>
LOG_LEVEL=INFO
LOG_JSON=true
```

### Deploy

```bash
railway up --ci
```

Or push to GitHub (auto-deploy enabled).

## Safety Features

### Circuit Breaker
- Opens after 5 consecutive failures
- Prevents cascading failures
- Auto-recovery after 5 minutes

### Retry Logic
- 3 retry attempts with exponential backoff
- Delays: 1s, 2s, 4s
- Only on HTTP errors

### Validation
- shop_id fixed at 17008 (Cvetykz)
- cityId fixed at 2 (Astana)
- Order status transitions validated

## Monitoring

### Logs

```bash
railway logs --tail
```

### Health Check

```bash
curl https://mcp-production.railway.app/health
```

## API Limits

- Production API timeout: 30 seconds
- Max products per request: 100
- Max orders per request: 20
- Rate limit: Not enforced (trust-based)

## Error Handling

All tools return structured responses:

```json
{
  "success": true,
  "data": {...},
  "timestamp": "2025-10-20T14:35:50"
}
```

On error:

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Development Roadmap

- [x] Phase 1: Shared library (mcp-shared)
- [x] Phase 2: HTTP client with retry
- [x] Phase 3: Read-only tools (list products/orders)
- [x] Phase 4: Write tools (create/update/delete)
- [ ] Phase 5: Webhook handler for sync
- [ ] Phase 6: Railway deployment
- [ ] Phase 7: Telegram Bot integration

## Support

For issues or questions, check:
- Railway logs: `railway logs`
- MCP Inspector: `python -m fastmcp dev server.py`
- Production API docs: `/api/v2/` endpoints
