"""
Tests for order creation, preview, and availability checking
"""
import pytest
from httpx import AsyncClient
from sqlmodel import select
from models import Order, OrderItem, OrderReservation


@pytest.mark.asyncio
async def test_preview_order_success(client: AsyncClient, sample_product_with_recipe):
    """Test POST /orders/preview validates availability and calculates totals"""
    order_items = [
        {"product_id": sample_product_with_recipe.id, "quantity": 1}
    ]

    response = await client.post("/api/v1/orders/preview", json=order_items)

    assert response.status_code == 200
    data = response.json()

    assert data["available"] is True
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == sample_product_with_recipe.id
    assert data["estimated_total"] == 1200000  # 12000 tenge in kopecks


@pytest.mark.asyncio
async def test_preview_order_insufficient_stock(client: AsyncClient, sample_product_with_recipe):
    """Test preview fails when warehouse stock is insufficient"""
    # Request way more than warehouse has (warehouse has 50 roses, product needs 15 per unit)
    # So max ~3 products, request 10
    order_items = [
        {"product_id": sample_product_with_recipe.id, "quantity": 10}
    ]

    response = await client.post("/api/v1/orders/preview", json=order_items)

    assert response.status_code == 200
    data = response.json()

    # Should indicate unavailability
    assert data["available"] is False
    assert len(data["warnings"]) > 0


@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient, async_session, sample_product_with_recipe):
    """Test POST /orders/with-items creates order and reserves inventory"""
    order_data = {
        "customerName": "Test Customer",
        "phone": "+77777777777",
        "delivery_address": "Test Address, Almaty",
        "recipient_name": "John Doe",
        "recipient_phone": "+77771234567",
        "delivery_type": "standard",
        "payment_method": "kaspi",
        "items": [
            {
                "product_id": sample_product_with_recipe.id,
                "quantity": 1,
                "special_requests": "Handle with care"
            }
        ]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)

    assert response.status_code == 200
    data = response.json()

    # Check order was created
    assert "orderNumber" in data
    assert data["orderNumber"].startswith("#")
    assert data["customerName"] == "Test Customer"
    assert data["status"] == "new"  # Enum serializes as lowercase

    # Check order items
    assert len(data["items"]) == 1
    assert data["items"][0]["product_name"] == "Test Bouquet"

    # Verify inventory was reserved
    query = select(OrderReservation).where(OrderReservation.order_id == data["id"])
    result = await async_session.execute(query)
    reservations = result.scalars().all()

    # Should have 2 reservations (optional ingredients are not reserved)
    # Ribbon is optional, so only Red Roses and Green Leaves are reserved
    assert len(reservations) == 2


@pytest.mark.asyncio
async def test_create_order_with_phase3_fields(client: AsyncClient, sample_product_with_recipe):
    """Test order creation with Phase 3 checkout fields"""
    order_data = {
        "customerName": "Test Customer",
        "phone": "+77777777777",
        "delivery_address": "Test Address",
        # Phase 3 fields
        "recipient_name": "Jane Smith",
        "recipient_phone": "+77779999999",
        "sender_phone": "+77777777777",
        "pickup_address": "Pickup Location 1",
        "delivery_type": "express",
        "scheduled_time": "2025-10-01 14:00",
        "payment_method": "cash",
        "order_comment": "Please call before delivery",
        "bonus_points": 50,
        "items": [
            {"product_id": sample_product_with_recipe.id, "quantity": 1}
        ]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)

    assert response.status_code == 200
    data = response.json()

    # Verify Phase 3 fields are saved
    assert data["recipient_name"] == "Jane Smith"
    assert data["delivery_type"] == "express"
    assert data["payment_method"] == "cash"
    assert data["order_comment"] == "Please call before delivery"
    assert data["bonus_points"] == 50


@pytest.mark.asyncio
async def test_get_order_status_by_number(client: AsyncClient, async_session, sample_product_with_recipe):
    """Test GET /orders/by-number/{order_number}/status retrieves order"""
    # First create an order
    order_data = {
        "customerName": "Status Test",
        "phone": "+77777777777",
        "delivery_address": "Test Address",
        "recipient_name": "Recipient Name",
        "delivery_type": "standard",
        "items": [
            {"product_id": sample_product_with_recipe.id, "quantity": 1}
        ]
    }

    create_response = await client.post("/api/v1/orders/with-items", json=order_data)
    created_order = create_response.json()
    order_number = created_order["orderNumber"]

    # Now retrieve status (URL-encode the order number)
    from urllib.parse import quote
    encoded_order_number = quote(order_number, safe='')
    response = await client.get(f"/api/v1/orders/by-number/{encoded_order_number}/status")

    assert response.status_code == 200
    data = response.json()

    assert data["order_number"] == order_number
    assert "status" in data
    assert data["recipient"]["name"] == "Recipient Name"
    assert "items" in data


@pytest.mark.asyncio
async def test_get_order_status_not_found(client: AsyncClient):
    """Test order status returns 404 for non-existent order"""
    from urllib.parse import quote
    encoded_order_number = quote("#99999", safe='')
    response = await client.get(f"/api/v1/orders/by-number/{encoded_order_number}/status")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_order_number_auto_increment(client: AsyncClient, sample_product_with_recipe):
    """Test order numbers are auto-incremented"""
    order_data = {
        "customerName": "Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    # Create first order
    response1 = await client.post("/api/v1/orders/with-items", json=order_data)
    order1 = response1.json()

    # Create second order
    response2 = await client.post("/api/v1/orders/with-items", json=order_data)
    order2 = response2.json()

    # Extract numbers
    num1 = int(order1["orderNumber"].replace("#", ""))
    num2 = int(order2["orderNumber"].replace("#", ""))

    # Second order number should be greater
    assert num2 > num1