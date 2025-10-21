# MCP Testing Fixes & Current Status

**Date:** 2025-10-20 18:14
**Backend:** http://localhost:8014
**Status:** 🟡 Partial Progress

---

## ✅ Fixes Applied

### 1. Order Preview Payload Format (FIXED)

**Issue:** Preview endpoint was receiving wrong payload format
**Error:** `422 Validation Error - Input should be a valid list`

**Root Cause:**
```python
# Wrong (before):
json_data={"items": items}

# Correct (after):
json_data=items  # Send list directly
```

**Fix Location:** `mcp-server/domains/orders/tools.py:272`

**Result:** ✅ Order preview now working (test #8 passes)

```
8️⃣ Previewing order cost...
   ✅ Subtotal: 900000₸
   🚚 Delivery: 0₸
   💰 Total: 900000₸
```

---

## ❌ Outstanding Issues

### Critical: Order Creation 500 Error

**Status:** BLOCKING - Cannot test Production sync until fixed

**Symptoms:**
- Backend returns `500 Internal Server Error` for both delivery and pickup orders
- Error occurs at `POST /api/v1/orders/public/create`
- Payload appears correct (all required fields present)
- Backend health check passes, database connected

**Test Payload (Delivery):**
```json
{
  "customerName": "MCP Test",
  "phone": "+77015211545",
  "delivery_address": "ул. Достык 5/2, кв 10",
  "delivery_date": "2025-10-21T14:00:00",
  "scheduled_time": "14:00",
  "items": [{"product_id": 1, "quantity": 1}],
  "notes": "Тестовый заказ из MCP",
  "check_availability": false,
  "recipient_name": "Тест МСП",
  "recipient_phone": "+77777777777",
  "sender_phone": "+77015211545",
  "delivery_type": "delivery"
}
```

**Test Payload (Pickup):**
```json
{
  "customerName": "MCP Pickup Test",
  "phone": "+77015211545",
  "delivery_address": "ул. Тестовая 1, Алматы",
  "delivery_date": "2025-10-20T18:00:00",
  "scheduled_time": "18:00",
  "items": [{"product_id": 1, "quantity": 1}],
  "notes": "Тестовый самовывоз из MCP",
  "check_availability": false,
  "sender_phone": "+77015211545",
  "delivery_type": "pickup",
  "pickup_address": "ул. Тестовая 1, Алматы"
}
```

**Potential Causes:**
1. Missing database columns or schema mismatch
2. Validation error in OrderService.create_order_with_items
3. Missing product_id=1 in database
4. Issue with client_service.get_or_create_client
5. Analytics or notification service errors

**Debug Steps Needed:**
1. Check backend application logs for detailed stack trace
2. Verify product_id=1 exists in database:
   ```sql
   SELECT * FROM product WHERE id = 1 AND shop_id = 8;
   ```
3. Test order creation with minimal payload (no optional fields)
4. Review OrderService code for validation logic
5. Check if database schema has all required columns

---

### Medium Priority Issues

#### 2. Bestsellers Endpoint (500 Error)

```
7️⃣ Getting bestsellers...
   ❌ Error: [500] Internal Server Error
```

**Endpoint:** `GET /api/v1/products/public/bestsellers?shop_id=8&limit=3`

**Likely Causes:**
- Database query error (possibly missing order_items or stats)
- Statistics not calculated for products
- Missing join or aggregation issue

#### 3. Smart Search Not Implemented (404)

```
6️⃣ Searching roses under 20000₸...
   ❌ Error: [404] Resource not found: {"detail":"Not Found"}
```

**Endpoint:** `GET /api/v1/products/public/smart-search`

**Status:** Endpoint doesn't exist in backend
**Options:**
- A) Remove from MCP tools (quick fix)
- B) Implement smart search in backend (requires dev work)

---

## 📊 Test Results Summary

### Improved: 8/12 Tests Passing (67%)

**Before Fixes:** 7/12 (58%)
**After Fixes:** 8/12 (67%)
**Improvement:** +1 test (+8%)

### ✅ Passing Tests (8)

| # | Test | Status |
|---|------|--------|
| 1 | List products | ✅ PASS |
| 2 | Get product details | ✅ PASS |
| 3 | Check availability | ✅ PASS |
| 4 | Get shop settings | ✅ PASS |
| 5 | Get working hours | ✅ PASS |
| 6 | Parse delivery date/time | ✅ PASS |
| 7 | Check delivery feasibility | ✅ PASS |
| 8 | **Preview order cost** | ✅ **FIXED** |

### ❌ Failing Tests (4)

| # | Test | Error | Priority |
|---|------|-------|----------|
| 9 | Create delivery order | 500 Error | 🔴 CRITICAL |
| 10 | Create pickup order | 500 Error | 🔴 CRITICAL |
| 11 | Smart search | 404 Not Found | 🟢 LOW |
| 12 | Get bestsellers | 500 Error | 🟡 MEDIUM |

---

## 🎯 Next Steps

### Immediate Priority

1. **Debug Order Creation** - CRITICAL 🔴
   - Access backend logs to get stack trace
   - Verify database schema matches code expectations
   - Test with minimal payload to isolate issue
   - Check if all foreign keys/relations exist

2. **Backend Logs Access**
   ```bash
   # Option 1: Direct log file
   tail -f /path/to/backend.log

   # Option 2: Stderr/stdout capture
   python3 main.py 2>&1 | tee backend-debug.log

   # Option 3: Check Railway logs (if deployed)
   railway logs
   ```

3. **Database Verification**
   ```sql
   -- Check if test product exists
   SELECT * FROM product WHERE id = 1 AND shop_id = 8;

   -- Check shop exists
   SELECT * FROM shop WHERE id = 8;

   -- Check order table structure
   DESCRIBE "order";
   ```

### After Order Creation Fix

4. **Re-run Full Test Suite**
   ```bash
   cd mcp-server
   python3 test_mcp_tools.py
   ```

5. **Test Production Sync End-to-End**
   - Create order in Railway backend
   - Call `sync_order_to_production` MCP tool
   - Verify order appears in Production Bitrix (shop_id=17008)
   - Check sequential order numbering

6. **Fix Bestsellers (Medium Priority)**
   - Debug 500 error
   - Implement product statistics if missing

7. **Remove or Implement Smart Search (Low Priority)**
   - Option A: Remove from server.py
   - Option B: Implement `/products/public/smart-search` endpoint

---

## 💡 Recommendations

### For User

**Before deploying Telegram bot:**
1. ✅ Order preview - Working
2. ❌ Order creation - **MUST FIX** (critical blocker)
3. ❌ Production sync - Cannot test until #2 fixed

**Workaround for Testing:**
- Create orders manually in database
- Test Production sync with existing order IDs
- Use MCP Inspector for manual tool testing

### For Development

**Clean up duplicate backend processes:**
```bash
# Kill old backends
pkill -9 -f "python main.py"

# Start fresh with logging
cd backend
python3 main.py 2>&1 | tee logs/backend-$(date +%Y%m%d-%H%M%S).log
```

**Enable verbose logging:**
```python
# In backend/main.py or config
logging.basicConfig(level=logging.DEBUG)
```

---

## 📈 Progress Tracking

- [x] Create sync_order_to_production MCP tool
- [x] Register tool in server.py
- [x] Create MCP Inspector testing guide
- [x] Run automated test suite
- [x] Fix order preview payload (422 error)
- [ ] **Fix order creation (500 error)** - IN PROGRESS 🔴
- [ ] Re-test after fixes
- [ ] Test Production sync end-to-end
- [ ] Deploy Telegram bot

---

**Report Generated:** 2025-10-20 18:14:30
**MCP Server:** `mcp-server/server.py`
**Test Script:** `mcp-server/test_mcp_tools.py`
