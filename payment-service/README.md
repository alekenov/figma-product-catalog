# Payment Service

Microservice for payment operations with automatic organization БИН routing.

## Features

- **Automatic БИН Routing**: Maps `shop_id` → `organization_bin` automatically
- **Multi-БИН Support**: Device token routing for multiple organizations
- **Kaspi Pay Integration**: Create payments, check status, process refunds
- **Audit Logging**: Full payment operation history
- **Multi-Provider Ready**: Architecture supports multiple payment providers
- **Production Proxy**: Uses cvety.kz (185.125.90.141) for Kaspi API access

📖 **[Complete Kaspi API Documentation →](./KASPI_API.md)**

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
  "external_id": "12800627774",
  "status": "Wait",
  "organization_bin": "210440028324"
}
```

**Check Status**
```http
GET /payments/kaspi/status/{external_id}

Response:
{
  "success": true,
  "external_id": "12800627774",
  "status": "Processed"
}
```

**Refund** (Automatic БИН matching)
```http
POST /payments/kaspi/refund
{
  "shop_id": 8,
  "external_id": "12800627774",
  "amount": 50
}

Response:
{
  "success": true,
  "external_id": "12800627774",
  "refunded_amount": 50,
  "organization_bin": "210440028324"
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
    "organization_bin": "210440028324",
    "device_token": "66cbf4e5-0193-45f3-8d97-362c98374466",
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
  "device_token": "your-device-token-uuid",
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
device_token    VARCHAR(50)  -- Kaspi TradePointId for multi-БИН support
is_active       BOOLEAN DEFAULT TRUE
provider        VARCHAR(20) DEFAULT 'kaspi'
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

**Note**: `device_token` is required for multi-БИН setups. See [KASPI_API.md](./KASPI_API.md) for details.

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
# Create payment with shop_id=8 (uses БИН 891027350515 automatically)
curl -X POST http://localhost:8015/payments/kaspi/create \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "amount": 100,
    "phone": "77015211545",
    "message": "Test payment"
  }'

# Check status
curl http://localhost:8015/payments/kaspi/status/12800627774

# Refund payment
curl -X POST http://localhost:8015/payments/kaspi/refund \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "external_id": "12800627774",
    "amount": 50
  }'

# List configs
curl http://localhost:8015/admin/configs
```

**Full test results** documented in [KASPI_API.md](./KASPI_API.md#testing).

## Frontend Administration

Payment configuration management is available via admin UI at:
```
https://frontend-production-6869.up.railway.app/superadmin/payment-configs
```

### Features

**Configuration Management**
- View all БИН configurations with masked device tokens
- Create new shop payment configs
- Edit device tokens and descriptions
- Test payments directly from UI

**Device Token Support** (Added 2025-10-22)
- Device token field with UUID validation
- Masked display in table (first 8 chars) for security
- Optional field - supports both single and multi-БИН setups

**Test Payment Interface**
- Create test payments for any shop_id
- Real-time status checking
- Full audit log integration

### Code Changes

Frontend updates in `frontend/src/`:
- **`PaymentConfigs.jsx`**: Added device_token field to form and table
- **`services/paymentAPI.js`**:
  - Fixed `updateConfig()` to use shop_id parameter (was: id)
  - Fixed `checkPaymentStatus()` URL to path param (was: query param)

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
