# 🚀 Phase 3 Deployment Guide: ApiClient Integration

**Status**: Ready for deployment
**Files**: PaymentServiceClient.php, ApiClientUpdated.php
**Date**: 2025-11-03

---

## Summary

Phase 3 integrates the production payment-service (Railway) with the Bitrix ApiClient, enabling multi-BIN payment routing for all 7 sellers.

**Result**: When customers place orders, payments are automatically routed to the correct seller's Kaspi account based on shop_id.

---

## Files to Deploy

### 1. PaymentServiceClient.php
**Destination**: `/home/bitrix/www/local/classes/Integration/PaymentService/Client.php`

**Purpose**:
- HTTP client for payment-service API calls
- Handles БIN lookup by shop_id
- Logs payments for auditing
- Includes fallback for when payment-service is unavailable

**Key Methods**:
- `getPaymentConfig($shopId)` - Get БIN and device_token for a shop
- `createPaymentLog($logData)` - Log payment operations
- `healthCheck()` - Check if payment-service is accessible

### 2. ApiClientUpdated.php
**Destination**: `/home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php`

**Purpose**:
- Replaces existing hardcoded ApiClient
- Integrates with PaymentServiceClient for dynamic БINs
- Maintains backwards compatibility with fallback values

**Key Changes**:
- Added `getPaymentConfig($shopId)` - Gets БIN from payment-service
- Added `getShopIdFromContext()` - Extracts shop_id from order/product
- Updated all public methods to use dynamic БINs instead of hardcoded values
- Added payment logging to payment-service
- Added config caching for performance (1-hour TTL)

---

## Deployment Steps

### Step 1: Pre-Deployment Checks

```bash
# 1. Verify payment-service is deployed on Railway
curl -s https://payment-service.up.railway.app/api/health
# Expected: 200 OK

# 2. Verify paymentconfig table is populated
# SSH to Railway PostgreSQL or use Railway CLI:
railway connect postgres -c "SELECT COUNT(*) FROM paymentconfig;"
# Expected: 7 rows (for the 7 sellers)

# 3. Test payment-service API
curl -s "https://payment-service.up.railway.app/api/payment/config?shop_id=121038"
# Expected: Returns config with organization_bin, device_token, etc.
```

### Step 2: Backup Existing ApiClient

```bash
# On production server (185.125.90.141):
ssh root@185.125.90.141

# Backup existing ApiClient
cp /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php \
   /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php.backup.$(date +%Y%m%d_%H%M%S)

# Verify backup created
ls -la /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php*
```

### Step 3: Create Payment Service Directory

```bash
# Create directory for PaymentService client
mkdir -p /home/bitrix/www/local/classes/Integration/PaymentService
chmod 755 /home/bitrix/www/local/classes/Integration/PaymentService
```

### Step 4: Deploy Files

#### Option A: SCP Deploy (Recommended)

```bash
# From your local machine:

# Deploy PaymentServiceClient.php
scp PaymentServiceClient.php \
    root@185.125.90.141:/home/bitrix/www/local/classes/Integration/PaymentService/Client.php

# Deploy Updated ApiClient
scp ApiClientUpdated.php \
    root@185.125.90.141:/home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php

# Verify files
ssh root@185.125.90.141 "ls -la /home/bitrix/www/local/classes/Integration/{PaymentService,Kaspi}/"
```

#### Option B: Git-based Deploy

```bash
# If using git hooks on production:
cd /home/bitrix/www
git pull origin main

# Or manually copy from figma-product-catalog repo
cp ~/figma-product-catalog/payment-service/PaymentServiceClient.php \
   /home/bitrix/www/local/classes/Integration/PaymentService/Client.php

cp ~/figma-product-catalog/payment-service/ApiClientUpdated.php \
   /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php
```

### Step 5: Set File Permissions

```bash
# On production server:
chown www-data:www-data /home/bitrix/www/local/classes/Integration/PaymentService/Client.php
chown www-data:www-data /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php

chmod 644 /home/bitrix/www/local/classes/Integration/PaymentService/Client.php
chmod 644 /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php
```

### Step 6: Configure Payment Service URL (Optional)

If payment-service URL is different from default:

```bash
# In Bitrix admin panel (or via API):
# Store URL in Bitrix options:

mysql -u usercvety -p dbcvety -e "
INSERT INTO b_option (MODULE_ID, OPTION_NAME, OPTION_VALUE)
VALUES ('onelab.kaspipay', 'payment_service_url', 'https://payment-service.up.railway.app/api')
ON DUPLICATE KEY UPDATE OPTION_VALUE='https://payment-service.up.railway.app/api';
"

# Verify:
mysql -u usercvety -p dbcvety -e "
SELECT OPTION_NAME, OPTION_VALUE FROM b_option
WHERE MODULE_ID='onelab.kaspipay' AND OPTION_NAME='payment_service_url';
"
```

### Step 7: Test Deployment

```bash
# On production server, test the integration:

php -r "
require_once '/home/bitrix/www/bitrix/modules/main/include/prolog_before.php';

// Test PaymentServiceClient
\$client = new \\Integration\\PaymentService\\Client();
\$config = \$client->getPaymentConfig(121038);

if (\$config['organization_bin'] === '920317450731') {
    echo '✅ PaymentServiceClient works!\n';
    echo 'БИN for shop_id 121038: ' . \$config['organization_bin'] . '\n';
} else {
    echo '❌ PaymentServiceClient test failed\n';
    exit(1);
}

// Test ApiClient integration
\$apiClient = new \\Integration\\Kaspi\\ApiClient();
echo '✅ ApiClient initialized\n';

exit(0);
"
```

### Step 8: Verify Logs

```bash
# Check for any errors in Bitrix logs:
tail -50 /home/bitrix/www/bitrix/log/kaspi_payment_service.log

# Check Apache/PHP errors:
tail -50 /var/log/apache2/error.log
```

### Step 9: Monitor Initial Payments

Test with actual orders:

1. **Create test order** for each seller:
   - Shop_id = 121038 (Eileen)
   - Shop_id = 576631 (VLVT)
   - Shop_id = 75509 (Santini)
   - Etc.

2. **Monitor Kaspi API responses** - verify money routes to correct accounts

3. **Check payment-service logs** on Railway:
   ```bash
   railway logs --service=payment-service
   ```

4. **Verify БINs in paymentconfig**:
   ```bash
   railway connect postgres -c "SELECT shop_id, organization_bin FROM paymentconfig ORDER BY shop_id;"
   ```

---

## Rollback Plan

If something goes wrong:

### Quick Rollback (< 1 minute)

```bash
# On production server:
ssh root@185.125.90.141

# Restore backup
cp /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php.backup.* \
   /home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php

# Verify
php -r "
require_once '/home/bitrix/www/bitrix/modules/main/include/prolog_before.php';
echo (class_exists('\\Integration\\Kaspi\\ApiClient') ? '✅ Restored\n' : '❌ Failed\n');
"
```

### Fallback Behavior

Even after deployment, if payment-service is unavailable:
1. ApiClient catches the exception
2. Falls back to hardcoded БINs from `getPaymentConfig()`
3. Payments continue (using default БIN)
4. Error is logged to `kaspi_payment_service.log`
5. You can fix payment-service and re-try

---

## Configuration

### Payment-Service URL

Default: `https://payment-service.up.railway.app/api`

To override, set in Bitrix:
```php
Option::set('onelab.kaspipay', 'payment_service_url', 'https://custom-url.com/api');
```

Or edit the ApiClient constructor:
```php
$client = new ApiClient([
    'payment_service_url' => 'https://custom-url.com/api'
]);
```

### Debug Logging

Enable detailed logging:
```php
// In ApiClient constructor
define('DEBUG_PAYMENT_SERVICE', true);
```

### Cache TTL

Default: 1 hour (3600 seconds)

To change, modify in `getPaymentConfig()`:
```php
if (time() - $cacheEntry['cached_at'] < 7200) {  // 2 hours
```

---

## Troubleshooting

### Error: "Shop ID not found"

**Cause**: shop_id=121038 doesn't exist in paymentconfig on Railway

**Fix**:
```bash
# Verify data on Railway:
railway connect postgres -c "SELECT * FROM paymentconfig WHERE shop_id=121038;"

# If empty, run Phase 2 migration again:
python migrate_production_shop_ids.py
```

### Error: "Connection refused" for payment-service

**Cause**: Payment-service is not deployed or wrong URL

**Fix**:
```bash
# Check Railway deployment:
railway status

# Check payment-service service is running:
railway logs --service=payment-service

# Test connectivity:
curl -v https://payment-service.up.railway.app/api/health
```

### Error: "Invalid JSON response"

**Cause**: Payment-service returned invalid response

**Fix**:
1. Check payment-service logs: `railway logs --service=payment-service`
2. Verify database connection on Railway
3. Restart payment-service: `railway redeploy --service=payment-service`

### Missing Namespace Error

**Cause**: PaymentService directory not created or wrong path

**Fix**:
```bash
# Verify structure:
ls -R /home/bitrix/www/local/classes/Integration/

# Should have:
# Integration/
# ├── Kaspi/
# │   └── ApiClient.php (updated)
# └── PaymentService/
#     └── Client.php (new)
```

### Fallback Being Used

**Symptom**: Getting default БIN (891027350515) instead of seller's БIN

**Cause**: getPaymentConfig() is catching exception and returning fallback

**Fix**:
1. Check logs: `tail kaspi_payment_service.log`
2. Verify payment-service is accessible
3. Check if shop_id exists in paymentconfig
4. Test: `curl "https://payment-service.up.railway.app/api/payment/config?shop_id=121038"`

---

## Post-Deployment

### 1. Monitor for 24 hours
- Check error logs
- Verify orders are processing
- Confirm money goes to correct accounts

### 2. Test Each Seller
Create test orders for all 7 sellers and verify payment routing:
- ✅ Eileen (121038) → 920317450731
- ✅ VLVT (576631) → 210440028324
- ✅ Santini (75509) → 860214400107
- ✅ Gerim (69292) → 960514451575
- ✅ Rosalie (49237) → 930201350766
- ✅ Royal Flowers (56195) → 590915402028
- ✅ Flowers.Almaty (71691) → 991011000048

### 3. Document Configuration
Store in wiki/documentation:
- Payment-service URL
- Payment config table structure
- Fallback handling logic
- Monitoring procedures

### 4. Alert Configuration
Set up alerts for:
- payment-service API errors (HTTP 5xx)
- Database connectivity issues
- Missing shop_ids in requests

---

## Performance Notes

- **Cache TTL**: 1 hour (configurable)
- **Network latency**: +50-100ms per payment (payment-service call)
- **Fallback timeout**: 10 seconds (curl timeout)

For high-volume deployments, consider:
1. Increasing cache TTL
2. Pre-warming cache on startup
3. Load-balancing payment-service across multiple instances

---

## Next Steps

After Phase 3 is verified:

✅ Phase 1: Research production shop_ids
✅ Phase 2: Update Railway paymentconfig
✅ Phase 3: Deploy ApiClient integration (THIS PHASE)
⏳ Phase 4: Add payment status polling
⏳ Phase 5: Setup CRM webhooks
⏳ Phase 6: Test all 7 sellers end-to-end

---

Last Updated: 2025-11-03
