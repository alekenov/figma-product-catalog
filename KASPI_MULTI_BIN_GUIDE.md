# Kaspi Pay Multi-BIN Support Guide

## Overview

The Kaspi Pay system now supports dynamic BIN (Organization Identification Number) switching for payment operations. This allows creating payments and processing refunds for different merchant organizations without code changes.

**Status**: ✅ Both production BIN (891027350515) and alternative BIN (210440028324) are working

## Architecture

### BIN Authentication
- **Type**: mTLS Certificate-based (not API keys)
- **Certificates**: Located at `/home/bitrix/kaspi_certificates/prod/`
  - Public cert: `cvety.cer`
  - Private key: `cvety-new.key`
  - Password: `sy3t6G2HhuG1m4pEK8AJ2`
- **Token**: Custom API token (`ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144`) for accessing PHP-wrapper endpoints

### System Layers

1. **FastAPI Backend** (`/backend/api/kaspi_pay.py`):
   - Accepts `organization_bin` parameter in request body
   - Routes through service layer
   - Returns payment responses with tracking IDs

2. **Service Layer** (`/backend/services/kaspi_pay_service.py`):
   - Converts `organization_bin` to `organizationBin` query parameter
   - Passes to production PHP-wrapper endpoints
   - Handles retries and error responses

3. **Production PHP-Wrapper** (`https://cvety.kz/api/v2/paymentkaspi/`):
   - Receives `organizationBin` query parameter
   - Routes payment through selected BIN's certificate
   - Returns payment confirmation with externalId

## Supported BINs

| BIN | Type | Status | Use Case |
|-----|------|--------|----------|
| `891027350515` | Production | ✅ Working | Live flower shop payments |
| `210440028324` | Alternative | ✅ Working | Testing / Alternative merchant |

## API Usage

### 1. Create Payment with Specific BIN

**FastAPI Endpoint**: `POST /api/v1/kaspi/create`

**Request Body**:
```json
{
  "phone": "77015211545",
  "amount": 100,
  "message": "Order #123",
  "organization_bin": "210440028324"
}
```

**Response**:
```json
{
  "success": true,
  "external_id": "12737338514",
  "status": "Wait"
}
```

**Note**: Omit `organization_bin` to use default BIN from configuration.

### 2. Refund Payment with Specific BIN

**FastAPI Endpoint**: `POST /api/v1/kaspi/refund`

**Request Body**:
```json
{
  "external_id": "12737338514",
  "amount": 50,
  "organization_bin": "210440028324"
}
```

**Response**:
```json
{
  "success": true,
  "external_id": "12737338514",
  "refunded_amount": 50
}
```

**Important**: The `organization_bin` must match the BIN used when creating the payment.

### 3. Check Payment Status

**FastAPI Endpoint**: `GET /api/v1/kaspi/status/{external_id}`

**Note**: Status checking doesn't require BIN parameter (payment ID is globally unique).

## Production Testing Examples

### Using curl with Alternative BIN

```bash
# Create payment with alternative BIN
curl -s -X POST http://localhost:8014/api/v1/kaspi/create \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "77015211545",
    "amount": 10,
    "message": "Test Alt BIN 210440028324",
    "organization_bin": "210440028324"
  }'

# Response:
# {"success":true,"external_id":"12737338514","status":"Wait"}
```

```bash
# Refund payment from alternative BIN
curl -s -X POST http://localhost:8014/api/v1/kaspi/refund \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "12737338514",
    "amount": 5,
    "organization_bin": "210440028324"
  }'
```

### Direct Production API Testing

```bash
# Create payment via production PHP-wrapper
curl -s -G "https://cvety.kz/api/v2/paymentkaspi/create/" \
  --data-urlencode "access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  --data-urlencode "organizationBin=210440028324" \
  --data-urlencode "phone=77015211545" \
  --data-urlencode "amount=10" \
  --data-urlencode "message=Test Alt BIN 210440028324"

# Response:
# {"status":true,"data":{"externalId":12737338514}}
```

```bash
# Check payment status
curl -s -G "https://cvety.kz/api/v2/paymentkaspi/status/" \
  --data-urlencode "access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  --data-urlencode "externalId=12737338514"
```

```bash
# Refund payment
curl -s -G "https://cvety.kz/api/v2/paymentkaspi/refund/" \
  --data-urlencode "access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144" \
  --data-urlencode "organizationBin=210440028324" \
  --data-urlencode "externalId=12737338514" \
  --data-urlencode "amount=5"
```

## Implementation Details

### Code Changes Made

1. **`backend/api/kaspi_pay.py`**:
   - Added `organization_bin: Optional[str]` to `CreatePaymentRequest` model
   - Added `organization_bin: Optional[str]` to `RefundRequest` model
   - Updated `/create` endpoint to pass `organization_bin` to service
   - Updated `/refund` endpoint to pass `organization_bin` to service

2. **`backend/services/kaspi_pay_service.py`**:
   - Updated `create_payment()` signature to accept `organization_bin` parameter
   - Updated `refund()` signature to accept `organization_bin` parameter
   - Added logic to conditionally include `organizationBin` in query parameters
   - Updated logging to include `organization_bin` for debugging

### Parameter Mapping

| Layer | Parameter Name | Example |
|-------|----------------|---------|
| FastAPI Request | `organization_bin` | `210440028324` |
| Service Layer | `organization_bin` (internal) | `210440028324` |
| Production API | `organizationBin` (query param) | `organizationBin=210440028324` |

## Success Criteria - All Met ✅

| Requirement | Status | Evidence |
|------------|--------|----------|
| Main BIN works (891027350515) | ✅ | Payment ID: 12737065473 |
| Alt BIN works (210440028324) | ✅ | Payment ID: 12737338514 |
| Same token for both BINs | ✅ | Both created with ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144 |
| mTLS certificates in place | ✅ | `/home/bitrix/kaspi_certificates/prod/` |
| FastAPI supports multi-BIN | ✅ | `organization_bin` parameter added |
| PHP-wrapper supports multi-BIN | ✅ | `organizationBin` query parameter |

## Next Steps

1. **Deploy to Railway**: When ready, push changes to GitHub main branch
2. **Integration**: Update order creation flow to use appropriate BIN
3. **Monitoring**: Log all payments with their BIN for reconciliation
4. **Admin Interface**: Consider adding BIN selector in admin panel

## Troubleshooting

### Payment Creation Fails
- ✅ Check if BIN is valid (should be 12 digits)
- ✅ Verify token hasn't expired
- ✅ Check mTLS certificates are installed on production

### Refund Fails with "Bad BIN"
- ✅ Ensure refund BIN matches payment creation BIN
- ✅ Check refund amount doesn't exceed payment amount
- ✅ Verify payment status is "Processed"

### Invalid Parameter Error
- ✅ Check `organizationBin` spelling (camelCase in URL)
- ✅ Verify BIN format (12 digits)
- ✅ Ensure token is included in all requests
