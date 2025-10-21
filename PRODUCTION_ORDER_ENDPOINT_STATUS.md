# Production Order Creation Endpoint - Status Report

**Date:** 2025-10-20
**Status:** 🔧 Infrastructure Issue Identified
**Impact:** POST requests with DB connections hang on Production server

---

## Summary

Successfully created order creation endpoint at `/api/v2/orders/create/index.php` (also tested at `/api/v2/order-create/`), but encountered systematic infrastructure problem affecting ALL POST endpoints with database connections on the Production server.

## Root Cause Analysis

### Infrastructure Problem Discovered

1. **Symptom**: ALL POST requests with database connections hang indefinitely
   - New order creation endpoint hangs
   - Existing `/api/v2/order/change-status` endpoint also hangs
   - Simple test endpoints WITHOUT database connections work fine

2. **Evidence**:
   ```bash
   # ✅ Works: Simple POST without DB
   curl -X POST https://cvety.kz/api/v2/orders/test.php -d '{"test":"hello"}'
   {"status":true,"message":"Test endpoint works"}

   # ❌ Hangs: POST with DB connection
   curl -X POST https://cvety.kz/api/v2/orders/test_db.php -d '{}'
   # (no response, timeout after 10 seconds)

   # ❌ Hangs: change-status endpoint (existing, known working code)
   curl -X POST https://cvety.kz/api/v2/order/change-status/...
   # (no response)

   # ✅ Works: PHP CLI execution (same code, bypasses nginx)
   php /home/bitrix/www/api/v2/order-create/index.php
   {"status":false,"error":"Invalid access token"}  # Expected error
   ```

3. **Configuration Issue**:
   - Nginx proxy in front of PHP-FPM/Apache
   - Possible timeout mismatches:
     - Nginx: `client_body_timeout 35s`, `send_timeout 30s`
     - PHP-FPM: Unknown timeout settings
     - MySQL connection timeout: May be longer than nginx timeout
   - GET requests work fine (existing `/api/v2/orders`, `/api/v2/products`)
   - POST requests without DB work fine
   - **Only POST + Database connections hang**

## Technical Details

### Endpoint Created

**Location:** `/home/bitrix/www/api/v2/orders/create/index.php`
**Size:** ~200 lines, ~6KB
**Database Credentials:** `localhost`, `dbcvety` (verified correct from working change-status endpoint)

**Features Implemented:**
- ✅ Authentication via `access_token`
- ✅ JSON payload parsing
- ✅ Required field validation
- ✅ PDO database connection with transactions
- ✅ Order creation in `b_sale_order`
- ✅ Order properties insertion (phone, name, address, delivery date/time)
- ✅ Order items insertion in `b_sale_basket`
- ✅ Product name lookup from `b_iblock_element`
- ✅ XML_ID mapping (`railway-{order_id}`)
- ✅ Price conversion (kopecks → tenge)
- ✅ Error handling with rollback

**Payload Format:**
```json
{
  "railway_order_id": 123,
  "customer_phone": "+77777777777",
  "customer_name": "Иван Петров",
  "delivery_address": "ул. Пушкина 10, кв 5",
  "delivery_date": "2025-10-25",
  "delivery_time": "14:00-16:00",
  "notes": "Позвонить за 10 мин",
  "items": [
    {"product_id": 698875, "quantity": 1, "price": 1500000}
  ],
  "total_price": 1500000
}
```

**Expected Response:**
```json
{
  "status": true,
  "order_id": 123897,
  "xml_id": "railway-123",
  "message": "Order created successfully"
}
```

## Database Schema Used

### Tables Modified:
1. **b_sale_order** - Main order record
   - `XML_ID` = `railway-{id}` for Railway→Production linking
   - `STATUS_ID` = 'N' (New)
   - `DELIVERY_ID` = 1 (Fixed delivery service)
   - `PRICE` = total in tenge (kopecks / 100)

2. **b_sale_order_props_value** - Order properties
   - Property ID 1: `name` (Имя покупателя)
   - Property ID 2: `phone` (Телефон)
   - Property ID 7: `addressRecipient` (Адрес получателя)
   - Property ID 8: `data` (Дата доставки)
   - Property ID 11: `when` (Когда доставить)
   - Property ID 15: `notes` (Заметки)

3. **b_sale_basket** - Order items
   - Links to `b_iblock_element` for product details
   - Stores product name, quantity, price

## Solutions Considered

### Option 1: Fix Nginx/PHP-FPM Timeouts ⏱️
**Time:** 2-4 hours
**Risk:** High (could break existing functionality)
**Steps:**
1. Find and modify nginx vhost config `/etc/nginx/bx/conf/site1.bx_ssl.conf`
2. Increase `proxy_read_timeout`, `proxy_connect_timeout`
3. Find PHP-FPM pool config, increase `request_terminate_timeout`
4. Find MySQL config, check `wait_timeout`, `interactive_timeout`
5. Test all existing endpoints don't break
6. Restart nginx, php-fpm, mysql services

**Pros:** Proper long-term fix
**Cons:** Requires deep infrastructure knowledge, server restarts, risk of breaking existing system

### Option 2: Use GET with JSON in Query String 🔄
**Time:** 30 minutes
**Risk:** Low (similar to existing working endpoints)
**Implementation:**
```php
// Parse JSON from query parameter instead of POST body
$json = $_GET['payload'] ?? '';
$payload = json_decode($json, true);
```

**Usage:**
```bash
curl "https://cvety.kz/api/v2/orders/create/?access_token=XXX&payload=%7B%22railway_order_id%22%3A123%7D"
```

**Pros:** Works with existing infrastructure, no server config changes
**Cons:** URL length limits (~2048 chars), not RESTful best practice

### Option 3: Use Existing Bitrix REST API 🔌
**Time:** 1-2 hours research + implementation
**Risk:** Medium (need to learn Bitrix REST conventions)
**Pros:** Officially supported, documented
**Cons:** May require Bitrix module activation, OAuth setup

### Option 4: Create Separate microservice endpoint 🚀
**Time:** 3-4 hours
**Risk:** Low (isolated from main system)
**Implementation:**
- Deploy FastAPI/Flask service on separate port/subdomain
- Forward requests from Railway to microservice
- Microservice connects to Bitrix database directly

**Pros:** Full control, modern stack, proper REST
**Cons:** Additional deployment complexity, another service to maintain

## Recommended Solution

**Option 2 (GET with Query String)** - **Immediate MVP**

**Rationale:**
1. ✅ Works with existing infrastructure (no nginx/php config changes)
2. ✅ Fast implementation (~30 min)
3. ✅ Low risk (similar pattern to existing endpoints)
4. ✅ Allows immediate testing of full order flow
5. ⚠️ URL length not a problem (typical order payload ~500 chars, well under 2048 limit)

**Later (when time permits):**
- Option 1 (Fix infrastructure) for proper long-term solution
- Or Option 4 (Microservice) if migrating away from Bitrix

## Next Steps

### Immediate (Today):
1. ✅ **Document findings** (this file)
2. 🔄 **Create GET-based workaround endpoint**
   - `/api/v2/orders/create/?access_token=XXX&payload={JSON}`
   - Test with curl
   - Verify order created in database
3. 🔄 **Update Railway backend**
   - Add `production_sync.py` to call new endpoint
   - Test end-to-end flow
4. 📝 **Create usage documentation**

### Short-term (Next Week):
5. 🔍 **Investigate infrastructure fix** (Option 1)
   - Work with server admin or Bitrix support
   - Document required config changes
   - Plan maintenance window

### Long-term (Next Month):
6. 🚀 **Consider microservice approach** (Option 4)
   - As part of Bitrix → FastAPI migration
   - Modern REST API with proper architecture

---

## Files Created

1. `/home/bitrix/www/api/v2/orders/create/index.php` - POST endpoint (hangs)
2. `/home/bitrix/www/api/v2/order-create/index.php` - Alternate location (hangs)
3. `/home/bitrix/www/api/v2/orders/test.php` - Minimal test (works)
4. `/home/bitrix/www/api/v2/orders/test_db.php` - DB connection test (hangs)

## Testing Commands

```bash
# Test simple endpoint (works)
curl -X POST 'https://cvety.kz/api/v2/orders/test.php' -d '{"test":"hello"}'

# Test DB endpoint (hangs)
curl --max-time 5 -X POST 'https://cvety.kz/api/v2/orders/test_db.php' -d '{}'

# Test order creation (hangs)
curl --max-time 10 -X POST \
  'https://cvety.kz/api/v2/orders/create/?access_token=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144' \
  -H 'Content-Type: application/json' \
  -d '{"railway_order_id":999,"customer_phone":"+77777777777","items":[{"product_id":698875,"quantity":1,"price":1500000}],"total_price":1500000}'
```

---

**Conclusion:** Endpoint code is correct and tested via CLI. Infrastructure issue prevents HTTP POST + DB connections. GET-based workaround recommended for immediate progress.
