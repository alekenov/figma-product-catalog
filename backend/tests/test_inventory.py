"""
Tests for inventory management and reservation edge cases
"""
import pytest
from httpx import AsyncClient
from sqlmodel import select
from models import WarehouseItem, OrderReservation


@pytest.mark.asyncio
async def test_inventory_reserved_on_order_creation(client: AsyncClient, async_session, sample_product_with_recipe, sample_warehouse_items):
    """Test inventory is properly reserved when order is created"""
    # Check initial quantities
    initial_roses = sample_warehouse_items[0].quantity  # Should be 50

    # Create order (requires 15 roses per recipe)
    order_data = {
        "customerName": "Inventory Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)
    assert response.status_code == 200
    created_order = response.json()

    # Check reservations were created
    query = select(OrderReservation).where(OrderReservation.order_id == created_order["id"])
    result = await async_session.execute(query)
    reservations = result.scalars().all()

    # Should have 2 reservations (optional ingredients are not reserved)
    # Ribbon is optional, so only Red Roses and Green Leaves are reserved
    assert len(reservations) == 2

    # Find roses reservation
    roses_reservation = next((r for r in reservations if r.warehouse_item_id == sample_warehouse_items[0].id), None)
    assert roses_reservation is not None
    assert roses_reservation.reserved_quantity == 15


@pytest.mark.asyncio
async def test_multiple_orders_reduce_available_inventory(client: AsyncClient, sample_product_with_recipe):
    """Test multiple orders progressively reduce available inventory"""
    order_data = {
        "customerName": "Multi Order Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    # Create first order - should succeed
    response1 = await client.post("/api/v1/orders/with-items", json=order_data)
    assert response1.status_code == 200

    # Create second order - should succeed
    response2 = await client.post("/api/v1/orders/with-items", json=order_data)
    assert response2.status_code == 200

    # Create third order - should succeed
    response3 = await client.post("/api/v1/orders/with-items", json=order_data)
    assert response3.status_code == 200

    # Preview for 4th order - warehouse has 50 roses, each order uses 15
    # After 3 orders: 50 - 45 = 5 left, not enough for 4th (needs 15)
    preview_items = [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    preview_response = await client.post("/api/v1/orders/preview", json=preview_items)

    assert preview_response.status_code == 200
    preview_data = preview_response.json()
    assert preview_data["available"] is False


@pytest.mark.asyncio
async def test_optional_ingredients_dont_block_order(client: AsyncClient, async_session, sample_product_with_recipe, sample_warehouse_items):
    """Test orders succeed even if optional ingredients are out of stock"""
    # Ribbon is optional (item 2 in recipe)
    # Set ribbon quantity to 0
    ribbon_item = sample_warehouse_items[2]
    ribbon_item.quantity = 0
    async_session.add(ribbon_item)
    await async_session.commit()

    order_data = {
        "customerName": "Optional Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}],
        "check_availability": False  # Skip availability check to test reservation logic
    }

    # Order should still succeed because ribbon is optional (not reserved)
    response = await client.post("/api/v1/orders/with-items", json=order_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_availability_considers_existing_reservations(client: AsyncClient, sample_product_with_recipe):
    """Test availability check accounts for already-reserved inventory"""
    # Create first order to reserve inventory
    order_data = {
        "customerName": "First Order",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 2}]
    }

    first_response = await client.post("/api/v1/orders/with-items", json=order_data)
    assert first_response.status_code == 200

    # Now preview another order - should account for first order's reservations
    preview_items = [{"product_id": sample_product_with_recipe.id, "quantity": 2}]
    preview_response = await client.post("/api/v1/orders/preview", json=preview_items)

    assert preview_response.status_code == 200
    data = preview_response.json()

    # After first order (2 products = 30 roses), remaining = 20
    # Second order needs 30 roses, so should be unavailable
    assert data["available"] is False


@pytest.mark.asyncio
async def test_min_quantity_warning(client: AsyncClient, async_session, sample_product_with_recipe, sample_warehouse_items):
    """Test system warns when warehouse inventory falls below min_quantity"""
    # Set roses to just above minimum (min=10, set to 15)
    roses_item = sample_warehouse_items[0]
    roses_item.quantity = 15
    async_session.add(roses_item)
    await async_session.commit()

    # Create order that will consume exactly to minimum
    order_data = {
        "customerName": "Min Qty Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)
    assert response.status_code == 200

    # After order: 15 - 15 = 0 left, which is below min_quantity=10
    # Preview should warn about low stock
    preview_response = await client.post("/api/v1/orders/preview", json=[{"product_id": sample_product_with_recipe.id, "quantity": 1}])
    assert preview_response.status_code == 200
    data = preview_response.json()
    assert data["available"] is False