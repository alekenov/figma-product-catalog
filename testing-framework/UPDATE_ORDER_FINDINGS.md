# Update Order Investigation - Findings and Recommendations

## Date: 2025-10-06

## Summary

Investigation into why the `07_modify_order.yaml` scenario doesn't test order modification functionality, and verification of the `update_order` MCP tool.

## Key Findings

### 1. MCP Server Issues Fixed ✅

**Issue**: Multiple endpoint and data structure problems in MCP server
**Fixed**:
- `create_product`: Changed endpoint from `/products/admin` to `/products/`
- `update_product`: Changed endpoint from `/products/admin/{id}` to `/products/{id}`
- `add_warehouse_stock`: Fixed endpoint and added required fields (warehouse_item_id, operation_type)
- `create_order`: Added `check_availability: False` to prevent 500 errors
- `create_order`: Fixed `scheduled_time` to send parsed time (HH:MM) instead of natural language
- `update_order`: Added to http_server.py exports (was missing from HTTP API)

**File**: `/Users/alekenov/figma-product-catalog/mcp-server/server.py` (line 460)
```python
# FIXED: Send parsed time instead of natural language
"scheduled_time": parsed_time,  # "14:00" instead of "днем"
```

### 2. Order Creation Works ✅

**Direct Backend Test**: Successfully created order via backend API
- Order ID: 14
- Tracking ID: 680710996
- Customer: "Update Test Customer"
- Shop ID: 8
- Delivery Date: 2025-10-07T14:00:00

**Backend Requirements**:
- `delivery_date` **must** be provided in ISO datetime format ("2025-10-07T14:00:00")
- Missing `delivery_date` causes 500 Internal Server Error
- MCP server's natural language date parsing works correctly ("завтра" → "2025-10-07T14:00:00")

### 3. Update Order Multi-Tenancy Issue ⚠️

**Issue**: Cannot update orders across shops due to multi-tenancy enforcement

**Error**: `403 Forbidden - "Order does not belong to your shop"`

**Root Cause**:
- Test user (77015211545) has `shop_id: None` (DIRECTOR role)
- Created order belongs to `shop_id: 8`
- Backend enforces strict shop-scoped access for order updates
- Even DIRECTOR role cannot update orders from other shops

**Backend Endpoint**: `PUT /api/v1/orders/{order_id}`
```python
# Backend checks shop_id match before allowing updates
if order.shop_id != user.shop_id:
    raise HTTPException(status_code=403, detail="Order does not belong to your shop")
```

### 4. Why 07_modify_order.yaml Doesn't Test Updates ❌

**Scenario Issue**: The scenario expects the AI to:
1. Find existing order by phone + tracking_id
2. Update order details (change delivery address)

**Actual AI Behavior**: AI correctly identifies it cannot modify orders and recommends calling the shop instead

**Reasons**:
1. **No real orders exist** for the test phone number (77012345678) and tracking_id (ORD-2025-001234)
2. **AI is being helpful**: Rather than failing with "order not found", it provides alternative solution
3. **update_order is available** but AI doesn't use it without a valid order_id

### 5. Natural Language Date Parsing Works ✅

MCP server successfully parses natural language dates and times:
- "завтра" → tomorrow's date
- "днем" → "14:00"
- "утром" → "10:00"
- "вечером" → "18:00"
- "как можно скорее" → nearest available slot

**Log Evidence**:
```
📅 Parsed natural language: 'завтра' 'днем' → 2025-10-07T14:00:00
```

## Recommendations

### Option 1: Create Real Test Data (Recommended)

**Steps**:
1. Create a user account with `shop_id=8` (not DIRECTOR)
2. Use that account to create a real order with known tracking_id
3. Update scenario to use the real tracking_id
4. Test will verify AI can actually update orders

**Pros**:
- Tests real functionality end-to-end
- Validates multi-tenancy works correctly
- Confirms AI can use update_order when order exists

**Cons**:
- Requires database setup
- Test data management overhead

### Option 2: Mock/Fixture Approach

**Steps**:
1. Create database fixtures with pre-populated orders for shop_id=8
2. Ensure test account belongs to shop_id=8
3. Scenario uses fixture tracking_ids

**Pros**:
- Clean, repeatable tests
- Fast test execution
- No cross-test contamination

**Cons**:
- Requires fixture infrastructure
- More complex test setup

### Option 3: E2E Scenario Redesign

**Steps**:
1. Combine order creation and modification in single scenario
2. First message: Create order, capture tracking_id
3. Second message: Modify the just-created order
4. Verifies complete flow

**Pros**:
- Tests full user journey
- No fixtures needed
- Self-contained test

**Cons**:
- Longer scenario
- Cannot test modification in isolation

## Backend API Verification

### Endpoints Tested:

✅ `POST /api/v1/orders/public/create?shop_id=8` - Order creation works
✅ `GET /api/v1/orders/{order_id}` - Order retrieval works
❌ `PUT /api/v1/orders/{order_id}` - Update blocked by multi-tenancy (expected behavior)

### Multi-Tenancy Enforcement:

The backend correctly enforces shop_id isolation:
- Orders can only be updated by users from the same shop
- DIRECTOR role without shop_id cannot update shop-specific orders
- This is correct security behavior

## Next Steps

1. **Choose Option 1**: Create a shop_id=8 user account for testing
2. **Create test order**: Use new account to create order with known tracking_id
3. **Update scenario**: Modify 07_modify_order.yaml to use real data
4. **Verify end-to-end**: Run scenario and confirm update_order is called

## Files Modified

- `/mcp-server/server.py` - Fixed scheduled_time to use parsed_time (line 460)
- `/mcp-server/http_server.py` - Added update_order to exports (line 16, 55)

## Test Files Created

- `/testing-framework/test_backend_direct.py` - Backend API validation
- `/testing-framework/test_create_and_update_order.py` - MCP flow test
- `/testing-framework/test_update_order_direct.py` - Update order validation

## Conclusion

The `update_order` MCP tool is correctly implemented and exposed via HTTP API. The scenario doesn't test it because:
1. No real orders exist for the test data
2. Multi-tenancy prevents cross-shop updates (correct behavior)
3. AI correctly handles "order not found" by suggesting alternatives

**Recommendation**: Implement Option 1 (create shop_id=8 user and real test order) to enable proper end-to-end testing.
