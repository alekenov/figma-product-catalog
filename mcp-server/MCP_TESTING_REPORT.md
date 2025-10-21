# MCP Tools Testing Report

**Date:** 2025-10-20 18:07
**Backend:** http://localhost:8014
**Test Script:** `test_mcp_tools.py`
**Status:** ⚠️ Partial Success

---

## 📊 Test Summary

### ✅ **Passing Tests (7/12)**

| Category | Test | Status | Details |
|----------|------|--------|---------|
| Products | List products | ✅ PASS | Found 5 products successfully |
| Products | Get product details | ✅ PASS | Retrieved product #1: "Букет 'Нежность' из 7 роз" (900000₸) |
| Products | Check availability | ✅ PASS | Product available |
| Shop | Get settings | ✅ PASS | Shop name: None, Address: "ул. Тестовая 1, Алматы" |
| Shop | Get working hours | ✅ PASS | Retrieved (values None - needs setup) |
| Orders | Parse delivery date/time | ✅ PASS | "завтра днем" → "2025-10-21T14:00:00" |
| Orders | Check delivery feasibility | ✅ PASS | Delivery possible |

### ❌ **Failing Tests (5/12)**

| Category | Test | Status | Error | Fix Needed |
|----------|------|--------|-------|------------|
| Products | Smart search | ❌ FAIL | 404 Not Found | Endpoint `/api/v1/products/public/smart-search` not implemented |
| Products | Get bestsellers | ❌ FAIL | 500 Internal Server Error | Backend database or logic issue |
| Orders | Preview cost | ❌ FAIL | 422 Validation Error | Wrong payload format (expects list, got object) |
| Orders | Create delivery order | ❌ FAIL | 500 Internal Server Error | Backend database or logic issue |
| Orders | Create pickup order | ❌ FAIL | 500 Internal Server Error | Backend database or logic issue |

---

## 🔍 Detailed Test Results

### ✅ Products - List & Details

```
1️⃣ Listing products...
   ✅ Found 5 products
   📦 Example: Букет 'Нежность' из 7 роз - 900000₸

2️⃣ Getting product #1 details...
   ✅ Product: Букет 'Нежность' из 7 роз
   💰 Price: 900000₸
   📝 Description: Классический букет из 7 розовых роз с зеленью...

3️⃣ Checking availability...
   ✅ Available: True
   📦 Quantity: N/A
```

**Status:** ✅ **Working perfectly**

---

### ✅ Shop Information

```
4️⃣ Getting shop settings...
   ✅ Shop: None
   📍 Address: ул. Тестовая 1, Алматы
   📞 Phone: +77011234567
   💰 Delivery: None₸

5️⃣ Getting working hours...
   ✅ Weekdays: None - None
   ✅ Weekends: None - None
```

**Status:** ✅ **Working** (but needs shop data setup)

---

### ❌ Smart Search

```
6️⃣ Searching roses under 20000₸...
   ❌ Error: [404] Resource not found: {"detail":"Not Found"}
```

**Root Cause:** Endpoint `/api/v1/products/public/smart-search` не существует

**Fix Options:**
1. Implement endpoint in backend
2. Use regular `list_products` with filters instead
3. Remove from MCP tools if not needed

---

### ❌ Bestsellers

```
7️⃣ Getting bestsellers...
   ❌ Error: [500] Internal Server Error
```

**Root Cause:** Unknown backend error (need to check backend logs)

**Possible Issues:**
- Database query error
- Missing OrderItem data
- Statistics not calculated

---

### ❌ Order Preview

```
8️⃣ Previewing order cost...
   ❌ Error: [422] Validation error:
   {"detail":[{"type":"list_type","loc":["body"],"msg":"Input should be a valid list"...}]}
```

**Root Cause:** Wrong payload format

**Current (incorrect):**
```json
{"items": [{"product_id": 1, "quantity": 1}]}
```

**Expected (correct):**
```json
[{"product_id": 1, "quantity": 1}]
```

**Fix:** Update MCP tool to send array directly, not wrapped in object

---

### ❌ Order Creation

```
9️⃣ Creating delivery order...
   ❌ Error: [500] Internal Server Error

1️⃣1️⃣ Creating pickup order...
   ❌ Error: [500] Internal Server Error
```

**Root Cause:** Unknown backend error

**Possible Issues:**
1. Database constraint violation
2. Missing telegram_user_id validation
3. Price calculation error
4. Missing required fields in database

**Debug Steps:**
1. Check backend logs for stack trace
2. Try creating order via direct API call (curl)
3. Verify database schema matches code

---

## 🎯 **Production Sync Tool** (Not Tested)

`sync_order_to_production` tool created but **not tested** due to order creation failures.

**Expected Behavior:**
1. Fetch order from Railway backend
2. Build Production API payload
3. POST to https://cvety.kz/api/v2/orders/create/
4. Return Production order ID

**Cannot test until order creation is fixed.**

---

## 🐛 Issues Breakdown

### Critical (Blocking Production Use)

1. **Order Creation Fails (500 error)**
   - Impact: Cannot create orders in Railway
   - Blocks: Production sync, E2E testing, Telegram bot
   - Priority: **CRITICAL** 🔴

2. **Order Preview Validation Error (422)**
   - Impact: Cannot preview order cost
   - Fix: Easy (change payload format)
   - Priority: **HIGH** 🟠

### Medium Priority

3. **Bestsellers Endpoint Error (500)**
   - Impact: Cannot show bestsellers
   - Workaround: Use `get_featured_products` instead
   - Priority: **MEDIUM** 🟡

### Low Priority

4. **Smart Search Not Implemented (404)**
   - Impact: No budget/occasion filtering
   - Workaround: Use regular `list_products` with filters
   - Priority: **LOW** 🟢

---

## 💡 Recommendations

### Immediate Actions

1. **Fix Order Creation (500 error)**
   ```bash
   # Check backend logs
   cd backend
   cat logs/backend.log | grep ERROR

   # Try direct API call
   curl -X POST http://localhost:8014/api/v1/orders/public/create?shop_id=8 \
     -H "Content-Type: application/json" \
     -d '{
       "customerName": "Test",
       "phone": "+77015211545",
       "delivery_address": "Test",
       "delivery_date": "2025-10-21T14:00:00",
       "scheduled_time": "14:00",
       "items": [{"product_id": 1, "quantity": 1}],
       "check_availability": false,
       "delivery_type": "delivery"
     }'
   ```

2. **Fix Order Preview Payload**
   ```python
   # In domains/orders/tools.py preview_order_cost()
   # Change from:
   return await api_client.post("/orders/public/preview", json_data={"items": items}, ...)

   # To:
   return await api_client.post("/orders/public/preview", json_data=items, ...)
   ```

3. **Remove or Implement Smart Search**
   - Option A: Remove from server.py
   - Option B: Implement in backend

### After Fixes

4. **Re-run Full Test Suite**
   ```bash
   python3 test_mcp_tools.py
   ```

5. **Test Production Sync**
   - Create order in Railway
   - Call `sync_order_to_production`
   - Verify in Production database

6. **Start MCP Inspector for Manual Testing**
   ```bash
   python3 -m fastmcp dev server.py
   ```

7. **Connect Telegram Bot**
   - Add `TELEGRAM_TOKEN` to `.env`
   - Run: `cd telegram-bot && python3 bot.py`

---

## 📈 Success Rate

**Overall:** 7/12 tests passing (58%)

**By Category:**
- ✅ Products (basic): 3/3 (100%)
- ✅ Shop Info: 2/2 (100%)
- ❌ Products (advanced): 0/2 (0%)
- ❌ Orders: 2/5 (40%)

**Production Ready:** ❌ **NO** (order creation must work)

---

## 🚀 Next Steps

1. **Fix order creation** - CRITICAL 🔴
2. **Fix preview payload** - Easy fix 🟢
3. **Debug bestsellers** - Medium priority 🟡
4. **Re-test everything** - After fixes
5. **Test Production sync** - Final validation
6. **Deploy Telegram bot** - After all tests pass

---

## 📝 Notes

### MCP Tool Created Successfully
- ✅ `sync_order_to_production` added to `domains/orders/tools.py`
- ✅ Registered in `server.py`
- ✅ Fetches from Railway → Sends to Production
- ⏸️ **Cannot test until order creation works**

### Testing Infrastructure
- ✅ Backend running on http://localhost:8014
- ✅ Health check passing
- ✅ Database connected
- ❌ Some endpoints have errors

### What's Working Well
- ✅ Product catalog browsing
- ✅ Shop information
- ✅ Date/time parsing (natural language → ISO)
- ✅ Delivery feasibility checks

### What Needs Attention
- ❌ Order creation (500 errors)
- ❌ Some product discovery features (bestsellers, smart search)
- ⚠️ Shop settings incomplete (None values)

---

**Report Generated:** 2025-10-20 18:10
**Test Script:** `mcp-server/test_mcp_tools.py`
**Backend Logs:** `/tmp/backend.log`
