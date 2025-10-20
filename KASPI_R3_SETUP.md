# Kaspi Pay R3 Multi-BIN Setup Guide

## Overview

This guide explains how to properly configure the Kaspi Pay r3 "усиленная" (enhanced) API for supporting multiple organization BINs (Organization Identification Numbers).

**Key Concept**: Each BIN requires its own **DeviceToken**, which is bound to a specific (OrganizationBin, TradePointId) pair.

## Database Schema

### KaspiPayConfig Table
Stores the mapping of BIN → TradePoint → DeviceToken

```sql
CREATE TABLE kaspi_pay_config (
    id INT PRIMARY KEY,
    shop_id INT NOT NULL,

    -- Organization BIN (12 digits)
    organization_bin VARCHAR(12) NOT NULL UNIQUE,

    -- TradePoint ID obtained from r3/v01/partner/tradepoints/{organizationBin}
    trade_point_id VARCHAR(36) NOT NULL,

    -- DeviceToken obtained from r3/v01/device/register
    -- This token is bound to the specific (OrganizationBin, TradePointId) pair
    device_token VARCHAR(256) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,  -- Only one per shop

    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    last_verified_at DATETIME,
    description VARCHAR(255)
);
```

### KaspiPayLog Table
Audit trail for all payment operations (which BIN was used, etc.)

```sql
CREATE TABLE kaspi_pay_log (
    id INT PRIMARY KEY,
    shop_id INT NOT NULL,
    kaspi_config_id INT REFERENCES kaspi_pay_config(id),

    operation_type VARCHAR(50),  -- create, status, refund, cancel
    external_id VARCHAR(20),     -- QrPaymentId from Kaspi
    organization_bin VARCHAR(12),
    amount INT,                   -- kopecks
    status VARCHAR(50),           -- success, failed, pending
    error_message VARCHAR(500),

    created_at DATETIME DEFAULT NOW()
);
```

## Setup Process

### Step 1: Get TradePoints for BIN

For each organization BIN, fetch available trade points:

```bash
curl -s https://qrapi-cert-ip.kaspi.kz/r3/v01/partner/tradepoints/891027350515 \
  --cert /home/bitrix/kaspi_certificates/prod/cvety.cer \
  --key /home/bitrix/kaspi_certificates/prod/cvety-new.key \
  --cacert /home/bitrix/kaspi_certificates/prod/ca.crt
```

Response example:
```json
{
  "status": true,
  "data": {
    "tradepoints": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Main Office",
        "city": "Almaty"
      }
    ]
  }
}
```

**Store the TradePointId** - you'll need it for device registration.

### Step 2: Register Device for BIN

Using the TradePointId from Step 1, register a device in the context of this BIN:

```bash
curl -s -X POST https://qrapi-cert-ip.kaspi.kz/r3/v01/device/register \
  -H "Content-Type: application/json" \
  --cert /home/bitrix/kaspi_certificates/prod/cvety.cer \
  --key /home/bitrix/kaspi_certificates/prod/cvety-new.key \
  --cacert /home/bitrix/kaspi_certificates/prod/ca.crt \
  -d '{
    "organizationBin": "891027350515",
    "tradePointId": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response:
```json
{
  "status": true,
  "data": {
    "deviceToken": "577b4b39-1e7e-43d2-83c3-a0116118ef16"
  }
}
```

**Important Notes**:
- Repeated calls with the same (OrganizationBin, TradePointId) are idempotent - you get the same token
- This is the **only way** to get a DeviceToken for this BIN
- Store this token in `KaspiPayConfig.device_token`

### Step 3: Store Configuration in Database

```sql
INSERT INTO kaspi_pay_config (
    shop_id,
    organization_bin,
    trade_point_id,
    device_token,
    is_active,
    is_default,
    description
) VALUES (
    8,
    '891027350515',
    '550e8400-e29b-41d4-a716-446655440000',
    '577b4b39-1e7e-43d2-83c3-a0116118ef16',
    TRUE,
    TRUE,
    'Main BIN - Production'
);

-- And for alternative BIN
INSERT INTO kaspi_pay_config (
    shop_id,
    organization_bin,
    trade_point_id,
    device_token,
    is_active,
    is_default,
    description
) VALUES (
    8,
    '210440028324',
    '660f9511-f30c-52e5-b827-557766551111',
    '688c5d4a-2f8f-54e3-94d4-b1227229g27',
    TRUE,
    FALSE,
    'Alternative BIN - Testing'
);
```

### Step 4: Use DeviceToken When Creating Payments

When creating a payment, you **must** use the DeviceToken from the correct BIN:

```python
# Select which BIN to use
bin_config = KaspiConfigService.select_bin(
    db=db,
    shop_id=8,
    organization_bin="891027350515"  # Optional - uses default if not specified
)

if not bin_config:
    raise Exception("No active BIN configuration found")

# Create payment with BOTH OrganizationBin AND DeviceToken from same BIN
response = await kaspi_service.create_payment(
    phone="77015211545",
    amount=10000,  # kopecks
    message="Order #123",
    organization_bin=bin_config.organization_bin,
    device_token=bin_config.device_token,  # CRITICAL: Must match the BIN!
    trade_point_id=bin_config.trade_point_id
)

# Log the operation
KaspiConfigService.log_payment_operation(
    db=db,
    shop_id=8,
    kaspi_config_id=bin_config.id,
    operation_type="create",
    external_id=response["data"]["externalId"],
    organization_bin=bin_config.organization_bin,
    amount=10000,
    status="success"
)
```

## API Endpoints (R3 Enhanced)

### 1. Create Remote Payment

```
POST /r3/v01/remote/create/

Parameters:
{
    "organizationBin": "891027350515",      # REQUIRED
    "deviceToken": "577b4b39-1e7e-43d2-83c3-a0116118ef16",  # REQUIRED (from this BIN's registration)
    "tradePointId": "550e8400-e29b-41d4-a716-446655440000", # REQUIRED
    "phoneNumber": "77015211545",
    "amount": 10000,
    "comment": "Order description"
}

Response:
{
    "status": true,
    "data": {
        "QrPaymentId": "12737694350"
    }
}
```

### 2. Check Payment Status

```
GET /r3/v01/payment/status/{QrPaymentId}

Note: Status doesn't require OrganizationBin - QrPaymentId is globally unique
```

### 3. Cancel Payment

```
POST /r3/v01/remote/cancel/

Parameters:
{
    "organizationBin": "891027350515",      # REQUIRED (same BIN that created it)
    "deviceToken": "577b4b39-1e7e-43d2-83c3-a0116118ef16",  # REQUIRED
    "QrPaymentId": "12737694350"
}
```

### 4. Create Refund

```
POST /r3/v01/payment/refund/

Parameters:
{
    "organizationBin": "891027350515",      # REQUIRED (same BIN that created it)
    "deviceToken": "577b4b39-1e7e-43d2-83c3-a0116118ef16",  # REQUIRED
    "QrPaymentId": "12737694350",
    "returnAmount": 5000
}
```

### 5. Create QR Link

```
POST /r3/v01/qr/create-link/

Parameters:
{
    "organizationBin": "891027350515",      # REQUIRED
    "deviceToken": "577b4b39-1e7e-43d2-83c3-a0116118ef16",  # REQUIRED
    "tradePointId": "550e8400-e29b-41d4-a716-446655440000",
    "phoneNumber": "77015211545",
    "amount": 10000,
    "comment": "Order description",
    "merchantInvoiceId": "order-123"
}

Response:
{
    "status": true,
    "data": {
        "link": "https://kaspi.kz/pay?qrId=xyz...",
        "QrPaymentId": "12737694350"
    }
}
```

## Important Rules

1. **DeviceToken is BIN-specific**: The token is registered for a specific (OrganizationBin, TradePointId) pair
2. **Pair matching is critical**: For any operation, you must pass the DeviceToken from the **same BIN** you're operating on
3. **Status doesn't need BIN**: Checking payment status works with just the QrPaymentId
4. **Operations need full pair**: Creating, canceling, refunding all need both OrganizationBin + DeviceToken

## Troubleshooting

### Error: "Организация не зарегистрирована в Kaspi Pay"
**Cause**: The OrganizationBin is not registered with Kaspi
**Solution**: Verify the BIN is correct and has been registered with your Kaspi merchant account

### Error: "Invalid deviceToken"
**Cause**: DeviceToken doesn't match OrganizationBin, or token has expired
**Solution**:
- Verify you're using the DeviceToken from the KaspiPayConfig for this BIN
- Re-register the device if token is old

### Error: "Trade point is not active"
**Cause**: The TradePointId is not active for this BIN
**Solution**: Get fresh TradePointIds from r3/v01/partner/tradepoints

### Payment created but with wrong BIN
**Cause**: Used DeviceToken from different BIN than OrganizationBin parameter
**Solution**: Use `BinSelectionGuard.validate_bin_for_shop()` before creating payment

## Migration from Old Setup

If migrating from hardcoded single BIN:

1. Create KaspiPayConfig entries for each BIN you want to support
2. Update KaspiPayService to accept `device_token` parameter
3. Use KaspiConfigService.select_bin() to choose correct BIN
4. Update all payment creation calls to pass DeviceToken
5. Enable KaspiPayLog for audit trail

## Example: Complete Payment Flow with Multi-BIN

```python
from sqlalchemy.orm import Session
from services.kaspi_pay_service import get_kaspi_service
from services.kaspi_config_service import KaspiConfigService

async def create_order_payment(
    db: Session,
    shop_id: int,
    customer_phone: str,
    amount: int,
    organization_bin: str = None  # Optional - uses default if not specified
):
    # Step 1: Select which BIN to use
    bin_config = KaspiConfigService.select_bin(
        db=db,
        shop_id=shop_id,
        organization_bin=organization_bin
    )

    if not bin_config:
        raise ValueError("No active BIN configuration found")

    # Step 2: Validate BIN is allowed for this shop
    if not BinSelectionGuard.validate_bin_for_shop(db, shop_id, bin_config.organization_bin):
        raise ValueError("BIN not allowed for this shop")

    # Step 3: Create payment with correct DeviceToken
    kaspi_service = get_kaspi_service()
    try:
        response = await kaspi_service.create_payment(
            phone=customer_phone,
            amount=amount,
            message=f"Order for {customer_phone}",
            organization_bin=bin_config.organization_bin,
            device_token=bin_config.device_token
        )

        external_id = response["data"]["QrPaymentId"]
        status = "success"
        error_msg = None

    except Exception as e:
        external_id = None
        status = "failed"
        error_msg = str(e)
        raise

    finally:
        # Step 4: Log the operation
        KaspiConfigService.log_payment_operation(
            db=db,
            shop_id=shop_id,
            kaspi_config_id=bin_config.id,
            operation_type="create",
            external_id=external_id,
            organization_bin=bin_config.organization_bin,
            amount=amount,
            status=status,
            error_message=error_msg
        )

    return response
```

## Next Steps

1. ✅ Set up KaspiPayConfig table
2. ✅ Get TradePointIds for each BIN via r3 API
3. ✅ Register devices and store DeviceTokens in database
4. ✅ Update KaspiPayService to accept device_token parameter
5. ✅ Use KaspiConfigService.select_bin() before payments
6. ✅ Enable audit logging via KaspiPayLog
7. Deploy to production
