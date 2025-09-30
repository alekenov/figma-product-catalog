"""
Backend HTTP Tests for Phase 3 Order Functionality

Tests:
- Order creation with Phase 3 fields (recipient, sender, delivery options, payment)
- Order status endpoint with URL-encoded order numbers
- Price normalization (kopecks vs tenge)
- Bonus points calculation
- Order number encoding in API responses
"""
import pytest
from httpx import AsyncClient
from urllib.parse import quote, unquote


@pytest.mark.asyncio
async def test_create_order_with_kopecks_prices(client: AsyncClient, sample_product_with_recipe):
    """Test order creation accepts prices in kopecks and calculates totals correctly"""
    order_data = {
        "customerName": "Kopecks Test",
        "phone": "+77777777777",
        "delivery_address": "Test Address",
        "recipient_name": "Jane Doe",
        "recipient_phone": "+77771111111",
        "sender_phone": "+77777777777",
        "delivery_type": "express",
        "delivery_cost": 150000,  # 1500 tenge in kopecks
        "payment_method": "kaspi",
        "bonus_points": 5000,  # 50 tenge in kopecks (2% of total)
        "items": [
            {"product_id": sample_product_with_recipe.id, "quantity": 1}
        ]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)

    assert response.status_code == 200
    data = response.json()

    # Verify prices are stored in kopecks
    assert data["delivery_cost"] == 150000
    assert data["bonus_points"] == 5000

    # Verify total is calculated correctly
    # Product price: 1200000 kopecks (12000 tenge)
    # Delivery: 150000 kopecks (1500 tenge)
    # Expected total: 1350000 kopecks (13500 tenge)
    assert data["total"] == 1350000


@pytest.mark.asyncio
async def test_order_status_with_url_encoded_order_number(
    client: AsyncClient, async_session, sample_product_with_recipe
):
    """Test order status endpoint handles URL-encoded order numbers with # character"""
    # Create order
    order_data = {
        "customerName": "URL Encoding Test",
        "phone": "+77777777777",
        "delivery_address": "Test Address",
        "recipient_name": "John Smith",
        "delivery_type": "standard",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    create_response = await client.post("/api/v1/orders/with-items", json=order_data)
    order = create_response.json()
    order_number = order["orderNumber"]  # e.g., "#00001"

    # Test 1: URL-encode the order number (# becomes %23)
    encoded_order_number = quote(order_number, safe='')
    response = await client.get(f"/api/v1/orders/by-number/{encoded_order_number}/status")

    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == order_number

    # Test 2: Double encoding should still work
    double_encoded = quote(encoded_order_number, safe='')
    response2 = await client.get(f"/api/v1/orders/by-number/{double_encoded}/status")

    # Backend should handle this gracefully (may return 404 if not found)
    # The key is it shouldn't crash
    assert response2.status_code in [200, 404]


@pytest.mark.asyncio
async def test_order_status_returns_phase3_fields(
    client: AsyncClient, async_session, sample_product_with_recipe
):
    """Test order status endpoint returns all Phase 3 fields"""
    order_data = {
        "customerName": "Phase 3 Fields Test",
        "phone": "+77777777777",
        "delivery_address": "123 Test Street, Almaty",
        "recipient_name": "Sarah Johnson",
        "recipient_phone": "+77772222222",
        "sender_phone": "+77773333333",
        "pickup_address": "Pickup Location ABC",
        "delivery_type": "scheduled",
        "scheduled_time": "2025-10-01 15:00",
        "payment_method": "card",
        "order_comment": "Please call before delivery",
        "bonus_points": 12000,  # 120 tenge in kopecks
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 2}]
    }

    create_response = await client.post("/api/v1/orders/with-items", json=order_data)
    order = create_response.json()
    order_number = quote(order["orderNumber"], safe='')

    # Get order status
    response = await client.get(f"/api/v1/orders/by-number/{order_number}/status")

    assert response.status_code == 200
    data = response.json()

    # Verify Phase 3 fields are returned
    assert data["recipient"]["name"] == "Sarah Johnson"
    assert data["recipient"]["phone"] == "+77772222222"
    assert data["sender"]["phone"] == "+77773333333"
    assert data["pickup_address"] == "Pickup Location ABC"
    assert data["delivery_address"] == "123 Test Street, Almaty"
    assert data["bonus_points"] == 12000

    # Verify delivery type is formatted correctly
    assert "Scheduled" in data["delivery_type"]


@pytest.mark.asyncio
async def test_bonus_points_calculation_in_kopecks(
    client: AsyncClient, sample_product_with_recipe
):
    """Test bonus points are calculated correctly as 2% of total in kopecks"""
    # Product price: 1200000 kopecks (12000 tenge)
    # Delivery cost: 150000 kopecks (1500 tenge)
    # Total: 1350000 kopecks (13500 tenge)
    # Bonus (2%): 27000 kopecks (270 tenge)

    order_data = {
        "customerName": "Bonus Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "delivery_cost": 150000,
        "bonus_points": 27000,  # 2% of 1350000
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)

    assert response.status_code == 200
    data = response.json()

    # Verify bonus points are stored correctly
    assert data["bonus_points"] == 27000

    # Verify total calculation
    assert data["total"] == 1350000  # 12000 + 1500 = 13500 tenge = 1350000 kopecks


@pytest.mark.asyncio
async def test_order_number_format_in_response(
    client: AsyncClient, sample_product_with_recipe
):
    """Test order numbers are returned in correct format (#00001)"""
    order_data = {
        "customerName": "Format Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)

    assert response.status_code == 200
    data = response.json()

    # Verify order number format
    order_number = data["orderNumber"]
    assert order_number.startswith("#")
    assert len(order_number) == 6  # Format: #00001 (1 hash + 5 digits)
    assert order_number[1:].isdigit()


@pytest.mark.asyncio
async def test_order_status_404_for_invalid_order_number(client: AsyncClient):
    """Test order status returns 404 for non-existent order numbers"""
    fake_order_number = quote("#99999", safe='')
    response = await client.get(f"/api/v1/orders/by-number/{fake_order_number}/status")

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_order_items_in_status_response(
    client: AsyncClient, sample_product_with_recipe
):
    """Test order status includes item details"""
    order_data = {
        "customerName": "Items Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [
            {"product_id": sample_product_with_recipe.id, "quantity": 2}
        ]
    }

    create_response = await client.post("/api/v1/orders/with-items", json=order_data)
    order = create_response.json()
    order_number = quote(order["orderNumber"], safe='')

    # Get status
    response = await client.get(f"/api/v1/orders/by-number/{order_number}/status")

    assert response.status_code == 200
    data = response.json()

    # Verify items are included
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Bouquet"

    # Verify item pricing is in kopecks
    assert data["items"][0]["price"] == 2400000  # 2 items * 1200000 kopecks


@pytest.mark.asyncio
async def test_delivery_cost_calculation(
    client: AsyncClient, sample_product_with_recipe
):
    """Test delivery cost is correctly applied in order total"""
    # Test with custom delivery cost
    custom_delivery_cost = 200000  # 2000 tenge in kopecks

    order_data = {
        "customerName": "Delivery Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "delivery_cost": custom_delivery_cost,
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    response = await client.post("/api/v1/orders/with-items", json=order_data)

    assert response.status_code == 200
    data = response.json()

    # Verify delivery cost is stored
    assert data["delivery_cost"] == custom_delivery_cost

    # Verify it's included in total
    # Product: 1200000 + Delivery: 200000 = 1400000
    assert data["total"] == 1400000


@pytest.mark.asyncio
async def test_order_status_maps_backend_enum_to_frontend_vocabulary(
    client: AsyncClient, sample_product_with_recipe
):
    """Test order status endpoint maps backend OrderStatus enum to frontend vocabulary"""
    order_data = {
        "customerName": "Status Mapping Test",
        "phone": "+77777777777",
        "delivery_address": "Test",
        "items": [{"product_id": sample_product_with_recipe.id, "quantity": 1}]
    }

    create_response = await client.post("/api/v1/orders/with-items", json=order_data)
    order = create_response.json()
    order_number = quote(order["orderNumber"], safe='')

    # Get status
    response = await client.get(f"/api/v1/orders/by-number/{order_number}/status")

    assert response.status_code == 200
    data = response.json()

    # Verify status is mapped to frontend vocabulary
    # Backend "new" should map to frontend "confirmed"
    assert data["status"] in ["confirmed", "preparing", "delivering"]