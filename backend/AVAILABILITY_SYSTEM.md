# Availability Checking System

## Overview

This system implements real-time inventory availability checking for order creation in the product catalog backend. It ensures that orders can only be placed when sufficient stock is available, considering both warehouse quantities and product recipes.

## Key Features

### 1. Recipe-Based Availability Calculation
- Products have recipes that define required warehouse ingredients
- System calculates total required quantities based on order items and quantities
- Considers both required and optional ingredients

### 2. Real-Time Stock Tracking
- Tracks available warehouse quantities
- Considers currently reserved items for pending orders
- Provides detailed availability reports with ingredient-level breakdowns

### 3. Order Reservation System
- Reserves warehouse items when orders are created
- Prevents overselling by blocking reserved quantities from other orders
- Automatically releases reservations when orders are cancelled
- Converts reservations to actual deductions when orders are assembled

## API Endpoints

### Order Availability Endpoints

#### `POST /api/v1/orders/check-availability`
Check availability for multiple items before creating an order.
```json
{
  "order_items": [
    {
      "product_id": 1,
      "quantity": 2,
      "special_requests": "Optional notes"
    }
  ]
}
```

Response:
```json
{
  "available": true,
  "items": [
    {
      "product_id": 1,
      "product_name": "Rose Bouquet",
      "quantity_requested": 2,
      "available": true,
      "max_quantity": 10,
      "ingredients": [
        {
          "warehouse_item_id": 1,
          "name": "Red Rose",
          "required": 10,
          "available": 135,
          "reserved": 0,
          "sufficient": true
        }
      ]
    }
  ],
  "warnings": []
}
```

#### `POST /api/v1/orders/with-items`
Create an order with items and automatic availability validation.
```json
{
  "customerName": "John Doe",
  "phone": "77012345678",
  "delivery_address": "123 Main St",
  "delivery_cost": 1000,
  "check_availability": true,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

#### `GET /api/v1/orders/{order_id}/availability`
Check availability for existing order items.

#### `POST /api/v1/orders/{order_id}/reserve`
Reserve warehouse items for an order.

#### `DELETE /api/v1/orders/{order_id}/reservations`
Release all reservations for an order.

### Product Availability Endpoint

#### `GET /api/v1/products/{product_id}/availability?quantity=1`
Get detailed availability information for a specific product.

## Database Schema

### New Tables

#### `OrderReservation`
Tracks reserved warehouse items for orders.
```sql
- id: Primary key
- order_id: Foreign key to Order
- warehouse_item_id: Foreign key to WarehouseItem
- reserved_quantity: Quantity reserved
- created_at: Timestamp
```

### Enhanced Models

#### `AvailabilityResponse`
```python
{
  "available": bool,
  "items": List[ProductAvailability],
  "warnings": List[str]
}
```

#### `ProductAvailability`
```python
{
  "product_id": int,
  "product_name": str,
  "quantity_requested": int,
  "available": bool,
  "max_quantity": int,
  "ingredients": List[IngredientAvailability]
}
```

#### `IngredientAvailability`
```python
{
  "warehouse_item_id": int,
  "name": str,
  "required": int,
  "available": int,
  "reserved": int,
  "sufficient": bool
}
```

## Service Layer

### `AvailabilityService`

#### Key Methods:

- `check_product_availability(session, product_id, quantity)`: Check single product
- `check_order_availability(session, order_items)`: Check multiple items
- `reserve_ingredients_for_order(session, order_id, order_items)`: Reserve stock
- `release_order_reservations(session, order_id)`: Release reservations
- `get_reserved_quantities(session, warehouse_item_ids)`: Get current reservations

## Order Status Flow Integration

### Status Transitions:
1. **NEW**: Order created, items reserved (if availability checking enabled)
2. **PAID**: Payment confirmed, reservations maintained
3. **ACCEPTED**: Order accepted for processing, reservations maintained
4. **ASSEMBLED**: Reservations converted to actual warehouse deductions
5. **DELIVERED**: Order complete
6. **CANCELLED**: Reservations automatically released

## Error Handling

### Common Error Cases:
- Insufficient stock: Returns detailed breakdown of what's missing
- Product not found: Clear error message with product ID
- Disabled products: Prevents ordering inactive products
- Database errors: Proper rollback and error reporting

## Usage Examples

### Frontend Integration
```javascript
// Check availability before showing order confirmation
const availability = await fetch('/api/v1/orders/check-availability', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ order_items: cartItems })
});

if (!availability.available) {
  showStockWarning(availability.warnings);
  return;
}

// Create order with automatic availability checking
const order = await fetch('/api/v1/orders/with-items', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ...customerData,
    items: cartItems,
    check_availability: true
  })
});
```

### Admin Dashboard
```javascript
// Check product availability for inventory management
const availability = await fetch(`/api/v1/products/${productId}/availability?quantity=${quantity}`);

if (availability.max_quantity < 10) {
  showLowStockAlert(product);
}
```

## Testing

Run the test suite:
```bash
cd backend
python3 test_availability.py
```

This tests:
- Database schema integrity
- Service layer functionality
- Product availability calculations
- Order availability checks
- Reservation system

## Configuration

The system uses the existing database configuration from `config_sqlite.py`. No additional configuration is required.

## Future Enhancements

1. **Real-time notifications**: WebSocket updates for stock changes
2. **Batch reservations**: Reserve multiple orders atomically
3. **Stock forecasting**: Predict stock needs based on order patterns
4. **Supplier integration**: Automatic reordering when stock is low
5. **Advanced scheduling**: Time-based reservations for delivery dates