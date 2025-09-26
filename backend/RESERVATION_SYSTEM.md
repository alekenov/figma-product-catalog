# Order Reservation System

This document explains the order reservation system implemented for the product catalog backend.

## Overview

The order reservation system ensures that warehouse items are properly reserved when orders are created and converted to actual deductions when orders are assembled. This prevents overselling and provides accurate inventory management.

## Database Schema

### order_reservation Table

```sql
CREATE TABLE order_reservation (
    id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES order(id),
    warehouse_item_id INTEGER REFERENCES warehouseitem(id),
    reserved_quantity INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_order_reservation_order_id` for efficient order lookups
- `idx_order_reservation_warehouse_item_id` for efficient warehouse item lookups

## Models

### OrderReservation

Located in `models.py`:

```python
class OrderReservation(OrderReservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))

    # Relationships
    order: Optional[Order] = Relationship(back_populates="reservations")
    warehouse_item: Optional[WarehouseItem] = Relationship(back_populates="reservations")
```

## Core Functionality

### 1. Availability Checking

The `AvailabilityService` class provides comprehensive availability checking:

- **`check_order_availability()`**: Validates if all items in an order are available
- **`check_product_availability()`**: Checks availability for a single product
- **`get_reserved_quantities()`**: Gets currently reserved quantities for warehouse items

### 2. Reservation Management

**Creating Reservations:**
```python
await AvailabilityService.reserve_ingredients_for_order(session, order_id, order_items)
```

**Releasing Reservations:**
```python
await AvailabilityService.release_order_reservations(session, order_id)
```

### 3. Order Status Integration

The system integrates with order status changes:

- **Order Status → ASSEMBLED**: Converts reservations to actual deductions
- **Order Status → CANCELLED**: Releases all reservations
- **Order Deletion**: Automatically releases reservations

## API Endpoints

### Availability Checking
- `POST /orders/check-availability` - Check availability for order items
- `GET /orders/{order_id}/availability` - Check existing order availability

### Reservation Management
- `POST /orders/{order_id}/reserve` - Reserve warehouse items for order
- `DELETE /orders/{order_id}/reservations` - Release order reservations

### Order Creation with Reservations
- `POST /orders/with-items` - Create order with items and automatic reservations

## Workflow

### Standard Order Flow

1. **Order Creation**:
   - Use `POST /orders/with-items` with `check_availability: true`
   - System checks availability and creates reservations automatically

2. **Order Processing**:
   - Items remain reserved during order preparation
   - Availability calculations consider reserved quantities

3. **Order Assembly** (`status: "assembled"`):
   - Reservations are converted to actual warehouse deductions
   - Warehouse operations are logged
   - Reservations are deleted

4. **Order Cancellation** (`status: "cancelled"`):
   - All reservations are released
   - Items become available for other orders

### Manual Reservation Management

For advanced scenarios, you can manually manage reservations:

```python
# Check availability
availability = await AvailabilityService.check_order_availability(session, order_items)

# Create reservations
if availability.available:
    success = await AvailabilityService.reserve_ingredients_for_order(session, order_id, order_items)

# Release reservations
await AvailabilityService.release_order_reservations(session, order_id)
```

## Key Features

### Prevents Overselling
- Items are reserved when orders are created
- Availability calculations account for reservations
- Multiple orders cannot reserve the same inventory

### Atomic Operations
- Reservations are created as part of database transactions
- Failed operations roll back cleanly
- No partial reservation states

### Audit Trail
- All reservations are logged with timestamps
- Warehouse operations track reservation conversions
- Full traceability from order to inventory deduction

### Backward Compatibility
- Systems without reservations fall back to direct deduction logic
- Existing orders continue to work without modification

## Migration

The system includes a migration script to add the reservation table:

```bash
python3 migrations/add_order_reservation_table.py
```

**Rollback:**
```bash
python3 migrations/add_order_reservation_table.py rollback
```

## Testing

Test the reservation system:

```bash
python3 test_reservations.py
```

This tests:
- Database schema validation
- Reservation creation and management
- Availability checking with reservations
- Integration with existing data

## Error Handling

### Common Error Scenarios

1. **Insufficient Stock**: Throws ValueError with detailed message
2. **Missing Products**: Returns 404 error
3. **Database Errors**: Automatic rollback with error logging
4. **Concurrent Access**: Database locks prevent race conditions

### Error Messages

The system provides detailed error messages:
- Which warehouse item is insufficient
- How much is required vs available
- Which products are affected

## Performance Considerations

### Indexes
- Efficient lookups by order_id and warehouse_item_id
- Optimized for common reservation queries

### Query Optimization
- Batch operations where possible
- Minimal database round trips
- Efficient joins with warehouse items

### Memory Usage
- Reservations are processed in batches
- No large object caching
- Minimal memory footprint

## Security

### Access Control
- Reservations are tied to specific orders
- No cross-order reservation access
- Proper foreign key constraints

### Data Integrity
- Foreign key constraints prevent orphaned reservations
- Transaction boundaries ensure consistency
- Automatic cleanup on order deletion

## Monitoring

### Key Metrics to Monitor

1. **Reservation Count**: Track active reservations
2. **Conversion Rate**: Reservations → actual deductions
3. **Release Rate**: Cancelled orders releasing reservations
4. **Error Rate**: Failed reservation operations

### Queries for Monitoring

```sql
-- Active reservations count
SELECT COUNT(*) FROM order_reservation;

-- Reservations by order status
SELECT o.status, COUNT(r.id) as reservation_count
FROM order_reservation r
JOIN "order" o ON r.order_id = o.id
GROUP BY o.status;

-- Most reserved items
SELECT wi.name, SUM(r.reserved_quantity) as total_reserved
FROM order_reservation r
JOIN warehouseitem wi ON r.warehouse_item_id = wi.id
GROUP BY wi.id, wi.name
ORDER BY total_reserved DESC;
```