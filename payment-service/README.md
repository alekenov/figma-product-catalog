# Payment Service

Microservice for payment operations with automatic organization БИН routing.

## Features

- **Automatic БИН Routing**: Maps `shop_id` → `organization_bin` automatically
- **Kaspi Pay Integration**: Create payments, check status, process refunds
- **Audit Logging**: Full payment operation history
- **Multi-Provider Ready**: Architecture supports multiple payment providers
- **Production Proxy**: Uses cvety.kz (185.125.90.141) for Kaspi API access

## Architecture

```
Client (Main Backend)
  ↓
Payment Service (Railway)
  ↓ HTTP
Production API (185.125.90.141) [whitelist IP, mTLS]
  ↓
Kaspi API
```

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run server
python main.py
```

Server runs on `http://localhost:8015`

### Deploy to Railway

1. Create new Railway service
2. Connect to GitHub repo
3. Set environment variables:
   - `DATABASE_URL` (Railway PostgreSQL)
   - `PRODUCTION_API_URL`
   - `KASPI_ACCESS_TOKEN`
   - `CORS_ORIGINS`

4. Deploy automatically on push

## API Endpoints

### Payment Operations

**Create Payment** (Automatic БИН routing)
```http
POST /payments/kaspi/create
{
  "shop_id": 8,
  "amount": 10000,
  "phone": "77015211545",
  "message": "Order #12345"
}

Response:
{
  "success": true,
  "external_id": "12737065473",
  "status": "Wait",
  "organization_bin": "891027350515"
}
```

**Check Status**
```http
GET /payments/kaspi/status/{external_id}

Response:
{
  "success": true,
  "external_id": "12737065473",
  "status": "Processed"
}
```

**Refund** (Automatic БИН matching)
```http
POST /payments/kaspi/refund
{
  "shop_id": 8,
  "external_id": "12737065473",
  "amount": 5000
}

Response:
{
  "success": true,
  "external_id": "12737065473",
  "refunded_amount": 5000,
  "organization_bin": "891027350515"
}
```

### Admin Operations

**List Configs**
```http
GET /admin/configs

Response:
[
  {
    "id": 1,
    "shop_id": 8,
    "organization_bin": "891027350515",
    "is_active": true,
    "provider": "kaspi"
  }
]
```

**Create Config**
```http
POST /admin/configs
{
  "shop_id": 9,
  "organization_bin": "991011000048",
  "is_active": true
}
```

**Payment Logs**
```http
GET /admin/logs?shop_id=8&limit=100

Response:
[
  {
    "id": 1,
    "shop_id": 8,
    "organization_bin": "891027350515",
    "operation_type": "create",
    "external_id": "12737065473",
    "amount": 1000000,
    "status": "Wait",
    "created_at": "2025-10-22T10:00:00Z"
  }
]
```

## Database Schema

### payment_config
```sql
id              SERIAL PRIMARY KEY
shop_id         INT UNIQUE NOT NULL
organization_bin VARCHAR(12) NOT NULL
is_active       BOOLEAN DEFAULT TRUE
provider        VARCHAR(20) DEFAULT 'kaspi'
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

### payment_log
```sql
id              SERIAL PRIMARY KEY
shop_id         INT NOT NULL
organization_bin VARCHAR(12) NOT NULL
operation_type  VARCHAR(20) NOT NULL -- create, status, refund
external_id     VARCHAR(50)
amount          INT -- in kopecks
status          VARCHAR(50)
error_message   VARCHAR(500)
provider        VARCHAR(20) DEFAULT 'kaspi'
created_at      TIMESTAMP DEFAULT NOW()
```

## Configuration

Environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `PRODUCTION_API_URL`: cvety.kz API base URL
- `KASPI_ACCESS_TOKEN`: Access token for production API
- `PORT`: Service port (default: 8015)
- `DEBUG`: Debug mode
- `CORS_ORIGINS`: Allowed origins (comma-separated)

## Testing

```bash
# Create payment with shop_id=8
curl -X POST http://localhost:8015/payments/kaspi/create \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "amount": 100,
    "phone": "77015211545",
    "message": "Test payment"
  }'

# Check status
curl http://localhost:8015/payments/kaspi/status/12737065473

# List configs
curl http://localhost:8015/admin/configs
```

## Future Enhancements

- [ ] Add CloudPayments provider
- [ ] Add payment webhooks/callbacks
- [ ] Add authentication for admin endpoints
- [ ] Add rate limiting
- [ ] Add Prometheus metrics

## Troubleshooting

**Payment creation fails:**
- Check `payment_config` table has entry for `shop_id`
- Verify `is_active = true`
- Check `KASPI_ACCESS_TOKEN` is valid
- Verify production server (185.125.90.141) is accessible

**Wrong БИН used:**
- Check `payment_config` for correct `organization_bin`
- Check `payment_log` to see which БИН was used

**Database connection error:**
- Verify `DATABASE_URL` is correct
- Check Railway PostgreSQL is running

## License

Internal use only - Cvety.kz payment infrastructure
