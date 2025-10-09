# Order Creation and Update Fix Summary

**Date**: 2025-10-09
**Status**: ✅ Completed

## Overview

Fixed critical issues preventing order creation and updates in AI Agent Service V2. The service now correctly handles natural language dates/times and communicates with backend API.

## Problems Identified

### Problem 1: Natural Language Date Parsing
**Symptom**: Orders failed with "техническая проблема" (technical problem)
**Root Cause**: AI sent natural language dates like "сегодня вечером" (today evening), but backend expected ISO datetime format "2025-10-08T18:00:00"

**Error**:
```
422 Unprocessable Entity
Field required: delivery_date must be ISO datetime
```

### Problem 2: Field Name Mismatch
**Symptom**: Orders still failed even after date parsing fix
**Root Cause**: Backend API expected different field names than AI was sending

**Expected by Backend**:
- `customerName` (camelCase)
- `phone` (not `customer_phone`)
- `shop_id` in query parameters (not body)

**Sent by AI**:
- `customer_name` (snake_case)
- `customer_phone`
- `shop_id` in body

### Problem 3: Wrong Update Endpoint
**Symptom**: All order updates returned 404 Not Found
**Root Cause**: MCP client called wrong endpoint path

**Wrong Path**: `/api/v1/by-tracking/{tracking_id}`
**Correct Path**: `/api/v1/orders/by-tracking/{tracking_id}`

## Solutions Implemented

### Solution 1: Natural Language Date/Time Parser

Added parsing methods in `services/mcp_client.py`:

```python
def _parse_natural_date(self, date_str: str) -> str:
    """
    Convert natural language dates to ISO format.

    Examples:
        "сегодня" → "2025-10-08"
        "завтра" → "2025-10-09"
        "послезавтра" → "2025-10-10"
        "через 3 дня" → "2025-10-11"
    """
```

```python
def _parse_natural_time(self, time_str: str) -> str:
    """
    Convert natural language times to HH:MM format.

    Examples:
        "утром" (morning) → "09:00"
        "днем" (afternoon) → "14:00"
        "вечером" (evening) → "18:00"
        "как можно скорее" (ASAP) → "09:00"
        "уточнит менеджер" (manager will clarify) → "12:00"
    """
```

Combined result: `"завтра вечером"` → `"2025-10-09T18:00:00"`

### Solution 2: Field Name Transformation

Added transformation logic in `_create_order()`:

```python
# Transform field names from AI format to backend format
if "customer_name" in args:
    args["customerName"] = args.pop("customer_name")
if "customer_phone" in args:
    args["phone"] = args.pop("customer_phone")

# Move shop_id to query parameters
shop_id = args.pop("shop_id")
response = await self.client.post(
    f"{self.backend_url}/orders/public/create",
    params={"shop_id": shop_id},  # Query parameter
    json=args  # Body
)
```

### Solution 3: Corrected Update Endpoint

Fixed endpoint path in `_update_order()`:

```python
# Before (wrong):
response = await self.client.put(
    f"{self.backend_url}/by-tracking/{tracking_id}",
    ...
)

# After (correct):
response = await self.client.put(
    f"{self.backend_url}/orders/by-tracking/{tracking_id}",
    params={"changed_by": "customer"},
    json=args
)
```

## Test Results

### Test 1: Create Order with Natural Language
**Input**: "Хочу 25 роз на завтра утром, Иван 77011111111, адрес Сатпаева 10, получатель Анна 77022222222"
**Result**: ✅ Order #12379 created successfully (tracking ID: 928049769)
**Parsed**: "завтра утром" → "2025-10-10T09:00:00"

### Test 2: Update Card Text (Notes)
**Input**: "Хочу изменить текст открытки для заказа 928049769. Новый текст: С любовью и наилучшими пожеланиями!"
**Result**: ✅ Notes updated successfully
**HTTP**: `PUT /api/v1/orders/by-tracking/928049769?changed_by=customer` → 200 OK

### Test 3: Update Delivery Date
**Input**: "Перенесите заказ 928049769 на послезавтра вечером"
**Result**: ✅ Date updated from "10 October, 09:00" to "11 October, 18:00"
**Parsed**: "послезавтра вечером" → "2025-10-11T18:00:00"
**HTTP**: `PUT /api/v1/orders/by-tracking/928049769?changed_by=customer` → 200 OK

### Test 4: Update Recipient Name
**Input**: "Измените имя получателя для заказа 928049769 на Мария Петровна"
**Result**: ✅ Recipient changed from "Анна" to "Мария Петровна"
**HTTP**: `PUT /api/v1/orders/by-tracking/928049769?changed_by=customer` → 200 OK

## Final Order State

```json
{
  "tracking_id": "928049769",
  "order_number": "#12379",
  "status": "confirmed",
  "recipient": {
    "name": "Мария Петровна",  // Updated in Test 4
    "phone": "+77022222222"
  },
  "delivery_address": "Сатпаева 10",
  "date_time": "Saturday 11 October, 18:00",  // Updated in Test 3
  "items": [
    {
      "name": "Букет '25 роз' VIP",
      "price": 3000000
    }
  ],
  "total": 3000000
}
```

## Files Modified

### `/Users/alekenov/figma-product-catalog/ai-agent-service-v2/services/mcp_client.py`

**Added imports**:
```python
from datetime import datetime, timedelta
import re
```

**New methods**:
- `_parse_natural_date()` - Converts natural language dates to ISO format
- `_parse_natural_time()` - Converts natural language times to HH:MM format

**Modified methods**:
- `_create_order()` - Added date parsing and field name transformation
- `_update_order()` - Added date parsing and corrected endpoint path

## Cache Performance

Prompt caching is working excellently:
- **Cache hit rate**: 100% after initial request
- **Tokens saved**: 5,781 per cached request
- **Cost savings**: Significant reduction in API costs

## Next Steps

1. ✅ Order creation with natural language - **Working**
2. ✅ Order updates (notes, date, recipient) - **Working**
3. ⏳ Test with more complex scenarios (multiple items, pickup orders, etc.)
4. ⏳ Add support for more natural language patterns
5. ⏳ Implement order cancellation flow

## Technical Decisions

### Why parse dates in MCP client instead of AI?
- **User-friendly**: Customers speak naturally in chat
- **Backend-compatible**: Backend receives valid ISO datetimes
- **Centralized logic**: All date parsing in one place
- **AI focuses on conversation**: Claude handles dialogue, MCP adapts data formats

### Why transform field names in MCP client?
- **Separation of concerns**: AI uses consistent tool schema
- **Backend compatibility**: Backend has existing camelCase conventions
- **Single source of truth**: Transformation logic in one place

## Lessons Learned

1. **Always check endpoint paths carefully**: Missing `/orders/` prefix caused all updates to fail
2. **Backend validation is strict**: Pydantic schemas require exact field names and types
3. **Natural language parsing adds huge UX value**: Users can say "завтра вечером" instead of ISO datetime
4. **Prompt caching is incredibly effective**: 100% hit rate, 5,781 tokens saved per request

## References

- Backend Orders Router: `/backend/api/orders/router.py`
- Order Models: `/backend/models/orders.py`
- MCP Client: `/ai-agent-service-v2/services/mcp_client.py`
- Test Logs: `/tmp/ai_agent.log`
