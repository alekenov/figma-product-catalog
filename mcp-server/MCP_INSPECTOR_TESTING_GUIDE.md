# MCP Inspector Testing Guide

**Last Updated:** 2025-10-20
**Purpose:** Test all 33 MCP tools before deploying Telegram bot
**Status:** ✅ Ready for Testing

---

## 🚀 Quick Start

### 1. Start Backend API
```bash
cd backend
python main.py
```

Backend runs on **http://localhost:8014**

### 2. Start MCP Server with Inspector
```bash
cd mcp-server
python -m fastmcp dev server.py
```

MCP Inspector UI opens on **http://localhost:5173**

---

## 📊 Available Tools (33 total)

### 🌸 Products (9 tools)
- `list_products` - Browse catalog with filters
- `get_product` - Product details
- `check_product_availability` - Check stock
- `get_bestsellers` - Top sellers
- `get_featured_products` - Featured items
- `search_products_smart` - Smart search (budget, occasion)
- `create_product` - Admin: Create product
- `update_product` - Admin: Update product

### 📦 Orders (10 tools)
- `create_order` - Create new order
- `track_order` - Track by tracking_id
- `preview_order_cost` - Calculate cost
- `cancel_order` - Cancel order
- `sync_order_to_production` - **NEW**: Sync to Production Bitrix
- `list_orders` - Admin: List orders
- `get_order` - Admin: Order details
- `update_order_status` - Admin: Change status
- `update_order` - Update order details
- `track_order_by_phone` - Track by phone

### 🏪 Shop (9 tools)
- `get_shop_settings` - Shop info
- `get_working_hours` - Business hours
- `get_delivery_slots` - Available delivery times
- `validate_delivery_time` - Validate delivery time
- `check_delivery_feasibility` - Can we deliver?
- `get_faq` - Frequently asked questions
- `get_reviews` - Customer reviews
- `get_client_profile` - Client info
- `save_client_address` - Save address

### 🔑 Auth (2 tools)
- `login` - Get JWT token
- `get_current_user` - User info

### 📋 Other (3 tools)
- Inventory, Telegram, Kaspi Pay, Visual Search

---

## 🧪 Test Scenarios

### Scenario 1: Browse Products (Beginner)

**Goal:** Explore catalog and check availability

```json
# Step 1: Get list of products
Tool: list_products
Parameters:
{
  "shop_id": 8,
  "limit": 10,
  "enabled_only": true
}

Expected Response:
[
  {
    "id": 1,
    "name": "Букет из 25 роз",
    "price": 15000,
    "type": "flowers",
    "enabled": true
  },
  ...
]
```

```json
# Step 2: Get details of first product
Tool: get_product
Parameters:
{
  "product_id": <ID from step 1>,
  "shop_id": 8
}

Expected Response:
{
  "id": 1,
  "name": "Букет из 25 роз",
  "description": "Красивый букет...",
  "price": 15000,
  "images": [...],
  "enabled": true
}
```

```json
# Step 3: Check if product is available
Tool: check_product_availability
Parameters:
{
  "product_id": 1,
  "quantity": 1,
  "shop_id": 8
}

Expected Response:
{
  "available": true,
  "quantity_available": 50,
  "message": "Product is available"
}
```

---

### Scenario 2: Smart Product Search

**Goal:** Find products by budget and occasion

```json
# Find roses under 20000₸
Tool: search_products_smart
Parameters:
{
  "shop_id": 8,
  "query": "розы",
  "budget": 20000,
  "limit": 10
}

# Find birthday bouquets
Tool: search_products_smart
Parameters:
{
  "shop_id": 8,
  "occasion": "birthday",
  "limit": 5
}

# Get bestsellers
Tool: get_bestsellers
Parameters:
{
  "shop_id": 8,
  "limit": 5
}
```

---

### Scenario 3: Delivery Information

**Goal:** Check shop hours and delivery options

```json
# Get shop settings
Tool: get_shop_settings
Parameters:
{
  "shop_id": 8
}

Expected Response:
{
  "id": 8,
  "name": "Cvetykz",
  "address": "улица Достык, 5/2",
  "phone": "+77015211545",
  "weekday_start": "09:00",
  "weekday_end": "21:30",
  "delivery_price": 2500
}
```

```json
# Get working hours
Tool: get_working_hours
Parameters:
{
  "shop_id": 8
}

Expected Response:
{
  "weekday_start": "09:00",
  "weekday_end": "21:30",
  "weekday_closed": false,
  "weekend_start": "09:30",
  "weekend_end": "20:30",
  "weekend_closed": false
}
```

```json
# Get delivery slots for tomorrow
Tool: get_delivery_slots
Parameters:
{
  "shop_id": 8,
  "date": "2025-10-21"
}

Expected Response:
{
  "date": "2025-10-21",
  "slots": [
    {"start": "10:00", "end": "12:00", "available": true},
    {"start": "14:00", "end": "16:00", "available": true},
    ...
  ]
}
```

```json
# Check if delivery is possible tomorrow
Tool: check_delivery_feasibility
Parameters:
{
  "shop_id": 8,
  "delivery_date": "2025-10-21",
  "product_ids": "1,2,3"
}

Expected Response:
{
  "feasible": true,
  "message": "Delivery is possible",
  "earliest_time": "10:00"
}
```

---

### Scenario 4: Create Delivery Order

**Goal:** Create full delivery order in Railway + sync to Production

```json
# Step 1: Preview cost
Tool: preview_order_cost
Parameters:
{
  "shop_id": 8,
  "items": [
    {"product_id": 1, "quantity": 1}
  ]
}

Expected Response:
{
  "subtotal": 15000,
  "delivery_cost": 2500,
  "total": 17500,
  "items": [...]
}
```

```json
# Step 2: Create order in Railway
Tool: create_order
Parameters:
{
  "customer_name": "Тест МСП",
  "customer_phone": "+77015211545",
  "delivery_date": "завтра",
  "delivery_time": "днем",
  "shop_id": 8,
  "items": [
    {
      "product_id": 1,
      "quantity": 1
    }
  ],
  "total_price": 17500,
  "delivery_type": "delivery",
  "delivery_address": "ул. Достык 5/2, кв 10",
  "recipient_name": "Мария Петрова",
  "recipient_phone": "+77777777777",
  "notes": "Позвонить за 10 минут"
}

Expected Response:
{
  "id": 123,
  "tracking_id": "ABC123XYZ",
  "status": "NEW",
  "total_price": 17500,
  "customer_phone": "+77015211545",
  "delivery_type": "delivery"
}
```

```json
# Step 3: Sync to Production Bitrix
Tool: sync_order_to_production
Parameters:
{
  "order_id": 123,  // From step 2
  "shop_id": 8
}

Expected Response:
{
  "status": true,
  "order_id": 123903,
  "account_number": "123903",
  "xml_id": "railway-123",
  "pickup": "N",
  "price": 17000,
  "delivery_price": 2000
}
```

```json
# Step 4: Track order
Tool: track_order
Parameters:
{
  "tracking_id": "ABC123XYZ"  // From step 2
}

Expected Response:
{
  "tracking_id": "ABC123XYZ",
  "status": "NEW",
  "customer_phone": "+77015211545",
  "delivery_date": "2025-10-21T14:00:00",
  "items": [...]
}
```

---

### Scenario 5: Create Pickup Order

**Goal:** Create pickup order and sync to Production

```json
# Create pickup order
Tool: create_order
Parameters:
{
  "customer_name": "Тест Самовывоз",
  "customer_phone": "+77015211545",
  "delivery_date": "сегодня",
  "delivery_time": "вечером",
  "shop_id": 8,
  "items": [
    {"product_id": 1, "quantity": 1}
  ],
  "total_price": 15000,
  "delivery_type": "pickup"
}

Expected Response:
{
  "id": 124,
  "tracking_id": "DEF456ABC",
  "status": "NEW",
  "delivery_type": "pickup"
}
```

```json
# Sync to Production
Tool: sync_order_to_production
Parameters:
{
  "order_id": 124,
  "shop_id": 8
}

Expected Response:
{
  "status": true,
  "order_id": 123904,
  "xml_id": "railway-124",
  "pickup": "Y",
  "addressRecipient": "улица Достык, 5/2"
}
```

---

### Scenario 6: Get FAQs and Reviews

**Goal:** Fetch content for user information

```json
# Get FAQs
Tool: get_faq
Parameters:
{
  "shop_id": 8,
  "category": null
}

# Get reviews
Tool: get_reviews
Parameters:
{
  "shop_id": 8,
  "limit": 5
}
```

---

## 🎯 Testing Checklist

### Products
- [ ] List all products
- [ ] Get product details
- [ ] Check availability
- [ ] Search with budget filter
- [ ] Get bestsellers
- [ ] Get featured products

### Orders (Railway)
- [ ] Preview order cost
- [ ] Create delivery order
- [ ] Create pickup order
- [ ] Track order by tracking_id

### Production Sync
- [ ] Sync delivery order to Production
- [ ] Sync pickup order to Production
- [ ] Verify in Production database

### Shop Info
- [ ] Get shop settings
- [ ] Get working hours
- [ ] Get delivery slots
- [ ] Check delivery feasibility

### Content
- [ ] Get FAQs
- [ ] Get reviews

---

## 🐛 Common Issues

### Issue 1: Backend not running
**Error:** `Connection refused`
**Fix:** `cd backend && python main.py`

### Issue 2: Wrong shop_id
**Error:** `Shop not found`
**Fix:** Use `shop_id: 8` for Cvetykz

### Issue 3: Invalid date format
**Error:** `Invalid delivery date`
**Fix:** Use natural language: "завтра", "сегодня", or ISO format "2025-10-21"

### Issue 4: Product not available
**Error:** `Product not in stock`
**Fix:** Check `check_product_availability` first

### Issue 5: Production API timeout
**Error:** `production_api_failed`
**Fix:** Check Production API is accessible: `curl https://cvety.kz/api/v2/shop-info`

---

## 📝 Notes

### Price Format
- All prices in **kopecks** (100 kopecks = 1 tenge)
- Example: `1500000` kopecks = `15000₸`

### Date/Time Format
- Natural language supported: "завтра", "сегодня", "днем", "вечером"
- ISO format: "2025-10-21T14:00:00"

### Shop IDs
- **8** = Cvetykz (Астана)
- **17008** = Production shop_id

### Phone Format
- With prefix: `+77015211545`
- Without: `77015211545`

---

## 🚀 Next Steps

After successful MCP Inspector testing:

1. **Connect Telegram Bot**
   - Get token from @BotFather
   - Add to `.env`: `TELEGRAM_TOKEN=your_token`
   - Run: `cd telegram-bot && python bot.py`

2. **Test AI Agent Conversations**
   - "Какие у вас есть букеты?"
   - "Покажи розы до 15000 тенге"
   - "Хочу заказать букет на завтра"
   - "Где самовывоз?"

3. **Monitor Production**
   - Check Bitrix admin panel
   - Verify orders created correctly
   - Check sequential numbering

---

**Created by:** Claude Code
**Date:** 2025-10-20
**Status:** ✅ Ready for Testing
