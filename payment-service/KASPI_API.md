# Kaspi Pay API Integration

Complete documentation for Kaspi Pay integration with multi-БИН support.

## Overview

Payment-service integrates with Kaspi Pay Remote Payment API through a PHP proxy on production server (185.125.90.141). This architecture is required because:

1. **IP Whitelist**: Kaspi API only accepts requests from whitelisted IPs
2. **mTLS Certificates**: Requires client certificates for authentication
3. **Production Environment**: Certificates only work in production Kaspi environment

## Architecture

```
Payment Service (Railway)
  ↓ HTTPS
PHP Proxy (cvety.kz - 185.125.90.141)
  ↓ HTTPS + mTLS
Kaspi Pay API (qrapi-cert-ip.kaspi.kz)
```

## Kaspi API Endpoints

### 1. Create Remote Payment

**Kaspi Endpoint**: `POST /r3/v01/remote/create/`

Creates a payment request that customer pays via Kaspi app.

**PHP Proxy**: `https://cvety.kz/api/v2/paymentkaspi/create/`

**Parameters**:
- `phone` - Customer phone (e.g., "77015211545")
- `amount` - Amount in tenge (e.g., 100.00)
- `message` - Payment description
- `organizationBin` - Organization БИН (12 digits)
- `deviceToken` - Kaspi TradePointId (UUID, required for multi-БИН)
- `access_token` - Authentication token

**Response**:
```json
{
  "status": true,
  "data": {
    "externalId": "12800627774",
    "status": "Wait"
  },
  "http_code": 200
}
```

**Example**:
```bash
curl "https://cvety.kz/api/v2/paymentkaspi/create/?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&phone=77015211545&amount=100&message=Test&organizationBin=210440028324&deviceToken=66cbf4e5-0193-45f3-8d97-362c98374466"
```

### 2. Create Payment Link

**Kaspi Endpoint**: `POST /r3/v01/qr/create-link`

Creates a payment link without requiring customer phone number. Link can be shared via WhatsApp, Telegram, Email, or QR code.

**PHP Proxy**: `https://cvety.kz/api/v2/paymentkaspi/create-link/`

**Parameters**:
- `amount` - Amount in tenge (e.g., 100.00)
- `message` - Payment description
- `organizationBin` - Organization БИН (12 digits)
- `deviceToken` - Kaspi TradePointId (UUID, **required**)
- `access_token` - Authentication token

**Response**:
```json
{
  "status": true,
  "data": {
    "paymentLink": "https://pay.kaspi.kz/pay/57320274812835631931198067238079705415594",
    "paymentId": "12800944903",
    "expireDate": "2025-10-22T17:10:50.717+05:00"
  },
  "http_code": 200
}
```

**Payment Lifecycle**:
1. **QrTokenCreated**: Link generated, not yet activated
2. **RemotePaymentCreated**: Customer opened link in Kaspi app
3. **Processed**: Payment completed successfully

**Important**: Payment link expires 3 minutes after customer activates it (opens in Kaspi app).

**Example**:
```bash
curl "https://cvety.kz/api/v2/paymentkaspi/create-link/?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&amount=100&message=Test%20Payment&organizationBin=210440028324&deviceToken=66cbf4e5-0193-45f3-8d97-362c98374466"
```

### 3. Check Payment Status

**Kaspi Endpoint**: `GET /r3/v02/payment/status/{QrPaymentId}`

**PHP Proxy**: `https://cvety.kz/api/v2/paymentkaspi/status/`

**Parameters**:
- `externalId` - QrPaymentId from create payment
- `access_token` - Authentication token

**Response**:
```json
{
  "status": true,
  "data": {
    "externalId": "12800627774",
    "status": "Processed"
  },
  "http_code": 200
}
```

**Status Values**:
- `RemotePaymentCreated` - Payment link created, waiting for customer
- `Processed` - Payment completed successfully
- `Error` - Payment failed

**Example**:
```bash
curl "https://cvety.kz/api/v2/paymentkaspi/status/?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&externalId=12800627774"
```

### 4. Refund Payment

**Kaspi Endpoint**: `POST /r3/v01/payment/return`

**PHP Proxy**: `https://cvety.kz/api/v2/paymentkaspi/refund/`

**Parameters**:
- `externalId` - QrPaymentId from create payment
- `amount` - Amount to refund in tenge
- `organizationBin` - Organization БИН (must match payment)
- `deviceToken` - Kaspi TradePointId (required)
- `access_token` - Authentication token

**Response**:
```json
{
  "status": true,
  "data": {
    "externalId": "12800627774",
    "returnOperationId": 12800582793,
    "refundedAmount": 50
  },
  "http_code": 200
}
```

**Example**:
```bash
curl "https://cvety.kz/api/v2/paymentkaspi/refund/?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144&externalId=12800627774&amount=50&organizationBin=210440028324&deviceToken=66cbf4e5-0193-45f3-8d97-362c98374466"
```

## Multi-БИН Support

### Device Token Registration

Each organization БИН can have multiple trade points (devices). To use a specific trade point for payments:

1. **Register Device** (one-time setup):
```bash
curl -X POST https://qrapi-cert-ip.kaspi.kz/r3/v01/device/register \
  --cert cvety.cer --key cvety-new.key --pass "password" \
  -H "Content-Type: application/json" \
  -d '{
    "DeviceId": "unique-device-id",
    "OrganizationBin": "210440028324",
    "TradePointId": 1454711
  }'

Response:
{
  "Data": {
    "DeviceToken": "66cbf4e5-0193-45f3-8d97-362c98374466"
  },
  "StatusCode": 0
}
```

2. **Store DeviceToken** in database:
```sql
UPDATE payment_config
SET device_token = '66cbf4e5-0193-45f3-8d97-362c98374466'
WHERE shop_id = 8;
```

3. **Use DeviceToken** in all payment operations (create, refund)

### Configured Organizations

| shop_id | Organization | БИН | Device Token | Trade Point |
|---------|--------------|-----|--------------|-------------|
| 8 | Cvety.kz (Main) | 891027350515 | f369a115-2c0c-4b25-8b1e-d049dfb54f98 | 385716 (Сайт Cvety.kz) |
| 16 | VLVT FLOWERS | 210440028324 | 66cbf4e5-0193-45f3-8d97-362c98374466 | 1454711 |

## Payment Flow

### Customer Payment

1. **Create Payment**:
```python
POST /payments/kaspi/create
{
  "shop_id": 8,
  "amount": 100,
  "phone": "77015211545",
  "message": "Order #12345"
}
```

2. **Customer receives SMS** with Kaspi payment link

3. **Customer pays** in Kaspi app

4. **Check Status** (poll every 5-10 seconds):
```python
GET /payments/kaspi/status/12800627774
```

5. **Status changes** to "Processed" when paid

### Payment Link Flow

1. **Create Payment Link**:
```python
POST /payments/kaspi/create-link
{
  "shop_id": 8,
  "amount": 100,
  "message": "Order #12345"
}
```

2. **Share payment link** via WhatsApp, Telegram, Email, or QR code

3. **Customer opens link** → Status changes to "RemotePaymentCreated"

4. **Customer pays** → Status changes to "Processed"

5. **Check Status** using PaymentId:
```python
GET /payments/kaspi/status/12800944903
```

**Advantages over SMS payments**:
- No phone number required
- Can be shared in multiple channels
- Customer can pay from any device with Kaspi app
- Better for social media and website integration

### Refund Flow

1. **Check Available Refund Amount**:
```bash
curl -G "https://qrapi-cert-ip.kaspi.kz/r3/v01/payment/details" \
  --cert cvety.cer --key cvety-new.key \
  --data-urlencode "QrPaymentId=12800627774" \
  --data-urlencode "DeviceToken=66cbf4e5-0193-45f3-8d97-362c98374466"

Response:
{
  "Data": {
    "QrPaymentId": 12800627774,
    "TotalAmount": 100.00,
    "AvailableReturnAmount": 100.00
  }
}
```

2. **Process Refund** (full or partial):
```python
POST /payments/kaspi/refund
{
  "shop_id": 8,
  "external_id": "12800627774",
  "amount": 50
}
```

3. **Customer receives refund** in Kaspi app instantly

## Database Schema

### payment_config

Stores БИН routing configuration for each shop:

```sql
CREATE TABLE payment_config (
  id SERIAL PRIMARY KEY,
  shop_id INT UNIQUE NOT NULL,
  organization_bin VARCHAR(12) NOT NULL,
  device_token VARCHAR(50),  -- Kaspi TradePointId (UUID)
  is_active BOOLEAN DEFAULT TRUE,
  provider VARCHAR(20) DEFAULT 'kaspi',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**device_token field**: Required for multi-БИН setups. Must be VARCHAR(50) to accommodate UUID format (36 characters).

### payment_log

Audit trail for all payment operations:

```sql
CREATE TABLE payment_log (
  id SERIAL PRIMARY KEY,
  shop_id INT NOT NULL,
  organization_bin VARCHAR(12) NOT NULL,
  operation_type VARCHAR(20) NOT NULL,  -- create, status, refund
  external_id VARCHAR(50),               -- QrPaymentId
  amount INT,                            -- in kopecks
  status VARCHAR(50),
  error_message VARCHAR(500),
  provider VARCHAR(20) DEFAULT 'kaspi',
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### End-to-End Test

```bash
# 1. Create payment
curl -X POST https://payment-service-production-a685.up.railway.app/payments/kaspi/create \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "amount": 100,
    "phone": "77015211545",
    "message": "Test Payment"
  }'

# Response: {"external_id": "12800627774", "organization_bin": "210440028324"}

# 2. Pay in Kaspi app (manual)

# 3. Check status
curl https://payment-service-production-a685.up.railway.app/payments/kaspi/status/12800627774

# Response: {"status": "Processed"}

# 4. Refund
curl -X POST https://payment-service-production-a685.up.railway.app/payments/kaspi/refund \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "external_id": "12800627774",
    "amount": 50
  }'

# Response: {"refunded_amount": 50.0}
```

### Payment Link Test

```bash
# 1. Create payment link (no phone required)
curl -X POST https://payment-service-production-a685.up.railway.app/payments/kaspi/create-link \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "amount": 100,
    "message": "Test Payment Link"
  }'

# Response: {
#   "payment_link": "https://pay.kaspi.kz/pay/573202...",
#   "payment_id": "12800944903",
#   "expire_date": "2025-10-22T17:10:50.717+05:00"
# }

# 2. Share link via WhatsApp/Telegram/Email or open in browser

# 3. Customer opens link and pays in Kaspi app

# 4. Check status using payment_id
curl https://payment-service-production-a685.up.railway.app/payments/kaspi/status/12800944903

# Response: {"status": "Processed"}
```

### Test Results (2025-10-22)

✅ **All endpoints tested and working:**

- **SMS Payment**: Created payment 12800627774 from БИН 210440028324 (VLVT FLOWERS)
- **Status Check**: Returned "Processed" after payment
- **Refund**: Refunded 100 tenge in 2 operations (50 + 50)
- **Payment Link**: Created link with PaymentId 12800944903, no phone required
- **Device Token**: Automatically passed from database config for all operations

## Troubleshooting

### Payment Creation Issues

**Device not found error:**
- Check device_token is registered with Kaspi
- Verify device_token matches organization_bin
- Re-register device if needed

**Wrong БИН used:**
```sql
-- Check current config
SELECT * FROM payment_config WHERE shop_id = 8;

-- Update БИН and device_token
UPDATE payment_config
SET organization_bin = '210440028324',
    device_token = '66cbf4e5-0193-45f3-8d97-362c98374466'
WHERE shop_id = 8;
```

### Refund Issues

**404 error on refund:**
- Ensure payment is in "Processed" status
- Verify device_token is provided
- Check AvailableReturnAmount > 0

**Insufficient funds error:**
- Check total refunded amount doesn't exceed original payment
- Use `/r3/v01/payment/details` to verify AvailableReturnAmount

### Database Migration Issues

**device_token field too short:**
```bash
# Run migration endpoint
curl -X POST https://payment-service-production-a685.up.railway.app/admin/migrate

# Or run SQL manually
ALTER TABLE payment_config
ALTER COLUMN device_token TYPE VARCHAR(50);
```

## Production Setup

### 1. Configure БИН Mapping

```sql
-- Main БИН (Cvety.kz)
INSERT INTO paymentconfig (shop_id, organization_bin, device_token)
VALUES (8, '891027350515', 'f369a115-2c0c-4b25-8b1e-d049dfb54f98');

-- VLVT FLOWERS (backup)
INSERT INTO paymentconfig (shop_id, organization_bin, device_token)
VALUES (16, '210440028324', '66cbf4e5-0193-45f3-8d97-362c98374466');
```

### 2. Set Environment Variables

```bash
DATABASE_URL=postgresql://...
PRODUCTION_API_URL=https://cvety.kz/api/v2/paymentkaspi
KASPI_ACCESS_TOKEN=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144
CORS_ORIGINS=https://backend.yourdomain.com
```

### 3. Deploy to Railway

Railway auto-deploys on push to main branch. Monitor logs:

```bash
railway logs --service payment-service
```

## Security Notes

- **Access Token**: Never commit `KASPI_ACCESS_TOKEN` to git
- **mTLS Certificates**: Stored on production server only (185.125.90.141)
- **Device Token**: Sensitive, store securely in database
- **IP Whitelist**: Only production server IP allowed by Kaspi API

## References

- Kaspi Pay API Documentation (internal)
- Trade Point Management: `/r3/v01/partner/tradepoints/{bin}`
- Device Registration: `/r3/v01/device/register`
