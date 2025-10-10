# Test Environment Setup - Complete ✅

## Date: 2025-10-06

## Summary

Successfully created shop_id=8 test environment with user account and test order to enable proper testing of the `07_modify_order.yaml` scenario.

## Test Credentials

### Admin User (shop_id=8)
- **Phone**: 77088888888
- **Password**: test123
- **Name**: Test Admin
- **Role**: ADMIN
- **Shop ID**: 8

## Test Data

### Test Order for Modification Scenario
- **Tracking ID**: 608537258
- **Order Number**: #TEST-60853
- **Customer Name**: Айгуль Тестовая
- **Customer Phone**: +77012345678
- **Delivery Address**: ул. Абая, дом 10, кв. 5
- **Delivery Date**: Tomorrow at 14:00
- **Status**: ACCEPTED
- **Product**: Букет 'Романтика' из роз и лилий (18,000 тenge)

## Files Modified

### 1. backend/seeds/test_data.py
**Changes**:
- Added `get_password_hash` import
- Fixed test user password generation to use proper bcrypt hash
- Added auto-fix for invalid password hashes on seed run
- Added `seed_test_order()` function to create test order

**Key Lines**:
- Line 9: Import get_password_hash
- Lines 35-39: Auto-fix password hash when shop exists
- Lines 212-288: New seed_test_order function

### 2. backend/seeds/__init__.py
**Changes**:
- Import `seed_test_order` from test_data
- Call `seed_test_order(session)` after `seed_test_shop`

**Key Lines**:
- Line 7: Import seed_test_order
- Lines 20-21: Call seed_test_order

### 3. mcp-server/server.py (from earlier fixes)
**Changes**:
- Fixed `scheduled_time` to send parsed time instead of natural language
- Added `update_order` to http_server.py exports

**Key Lines**:
- Line 460: Use parsed_time instead of delivery_time

## How Seeds Work

Seeds run automatically on backend startup in local development (when DATABASE_URL env var is not set).

**Behavior**:
- If shop_id=8 exists → Skip shop creation, but still fix user password if invalid
- If test order exists for +77012345678 → Skip order creation
- Completely safe to run multiple times

## Backend Status

- ✅ Running on http://localhost:8014
- ✅ Seeds completed successfully
- ✅ Test user password hash fixed
- ✅ Test order exists in database

## Expected Scenario Behavior

### 07_modify_order.yaml Flow:

1. **Customer**: "I ordered yesterday, phone 77012345678. Can I change delivery address?"

2. **AI**: Should ask for tracking ID (security requirement)

3. **Customer**: Provides tracking_id: 608537258

4. **AI**: Should call `track_order` or `update_order` to:
   - Verify order exists
   - Check permissions
   - Modify delivery address

5. **Expected Outcome**:
   - `update_order` MCP tool is called
   - Delivery address updated successfully
   - Scenario passes with `manager_should_update_order_details: true`

## Next Steps

1. **Run Scenario**: `python3 run_scenario.py scenarios/07_modify_order.yaml`

2. **Verify update_order is called**: Check dialog logs for tool calls

3. **Check Updated Address**: Verify order was modified in database

## Troubleshooting

### If Login Fails
Run backend restart to re-run seeds and fix password:
```bash
cd /Users/alekenov/figma-product-catalog/backend
pkill -f "main.py" && python3 main.py
```

### If Order Not Found
Check if order exists:
```bash
python3 -c "
import asyncio, httpx
async def test():
    async with httpx.AsyncClient() as c:
        r = await c.post('http://localhost:8014/api/v1/auth/login',
            json={'phone':'77088888888','password':'test123'})
        token = r.json()['access_token']
        r = await c.get('http://localhost:8014/api/v1/orders',
            headers={'Authorization': f'Bearer {token}'}, params={'phone':'+77012345678'})
        print(r.json())
asyncio.run(test())
"
```

### Re-create Test Data
Delete database and restart backend:
```bash
rm /Users/alekenov/figma-product-catalog/backend/*.db*
```

## Success Criteria Met

✅ Test user (77088888888) can login
✅ Password hash is valid bcrypt format
✅ Test order exists for phone +77012345678
✅ Order has valid tracking_id (608537258)
✅ Order status is ACCEPTED (modifiable)
✅ MCP update_order tool is available
✅ Backend enforces multi-tenancy correctly

## Conclusion

The test environment is fully set up and ready for end-to-end testing of the order modification scenario. The `update_order` MCP tool should now be called when the AI assists customers with changing order details.
