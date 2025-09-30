"""
Test Suite for Phase 2: Product Detail Endpoint

Tests the GET /products/{id}/detail endpoint with all relationships:
- Images, variants, composition, addons, bundles
- Product and company reviews with aggregates
- Pickup locations
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from main import app


@pytest_asyncio.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_detail_endpoint_success(client):
    """Test that detail endpoint returns 200 for valid product"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "price" in data


@pytest.mark.asyncio
async def test_detail_endpoint_not_found(client):
    """Test that detail endpoint returns 404 for non-existent product"""
    response = await client.get("/api/v1/products/99999/detail")
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_detail_response_structure(client):
    """Test that response has all required fields"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    # Basic product fields
    required_fields = [
        "id", "name", "price", "type", "description", "image",
        "enabled", "is_featured", "rating", "review_count", "rating_count"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    # Relationship fields
    relationship_fields = [
        "images", "variants", "composition", "addons",
        "frequently_bought", "pickup_locations", "reviews"
    ]
    for field in relationship_fields:
        assert field in data, f"Missing relationship field: {field}"


@pytest.mark.asyncio
async def test_images_loaded(client):
    """Test that product images are loaded"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "images" in data
    assert isinstance(data["images"], list)

    # Validate image structure if images exist
    if len(data["images"]) > 0:
        image = data["images"][0]
        assert "id" in image
        assert "url" in image
        assert "order" in image


@pytest.mark.asyncio
async def test_variants_loaded(client):
    """Test that product variants (sizes) are loaded"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "variants" in data
    assert isinstance(data["variants"], list)

    # Validate variant structure if variants exist
    if len(data["variants"]) > 0:
        variant = data["variants"][0]
        assert "id" in variant
        assert "size" in variant
        assert "price" in variant
        assert "enabled" in variant


@pytest.mark.asyncio
async def test_composition_loaded(client):
    """Test that product composition (recipe) is loaded"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "composition" in data
    assert isinstance(data["composition"], list)

    # Validate composition structure if items exist
    if len(data["composition"]) > 0:
        item = data["composition"][0]
        assert "id" in item
        assert "name" in item
        assert "quantity" in item


@pytest.mark.asyncio
async def test_addons_loaded(client):
    """Test that product addons are loaded"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "addons" in data
    assert isinstance(data["addons"], list)

    # Validate addon structure if addons exist
    if len(data["addons"]) > 0:
        addon = data["addons"][0]
        assert "id" in addon
        assert "name" in addon
        assert "price" in addon
        assert "enabled" in addon


@pytest.mark.asyncio
async def test_frequently_bought_loaded(client):
    """Test that frequently bought products are loaded"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "frequently_bought" in data
    assert isinstance(data["frequently_bought"], list)

    # Validate bundle structure if bundles exist
    if len(data["frequently_bought"]) > 0:
        bundle = data["frequently_bought"][0]
        assert "id" in bundle
        assert "name" in bundle
        assert "price" in bundle
        assert "image" in bundle


@pytest.mark.asyncio
async def test_pickup_locations_loaded(client):
    """Test that pickup locations are loaded"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "pickup_locations" in data
    assert isinstance(data["pickup_locations"], list)

    # Validate that locations are strings
    if len(data["pickup_locations"]) > 0:
        location = data["pickup_locations"][0]
        assert isinstance(location, str)


@pytest.mark.asyncio
async def test_reviews_structure(client):
    """Test that reviews have correct structure"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    assert "reviews" in data
    reviews = data["reviews"]

    # Both product and company reviews should exist
    assert "product" in reviews
    assert "company" in reviews

    # Validate product reviews structure
    product_reviews = reviews["product"]
    assert "count" in product_reviews
    assert "average_rating" in product_reviews
    assert "breakdown" in product_reviews
    assert "photos" in product_reviews
    assert "items" in product_reviews

    # Validate company reviews structure
    company_reviews = reviews["company"]
    assert "count" in company_reviews
    assert "average_rating" in company_reviews
    assert "breakdown" in company_reviews
    assert "photos" in company_reviews
    assert "items" in company_reviews


@pytest.mark.asyncio
async def test_review_aggregates_calculation(client):
    """Test that review aggregates are calculated correctly"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    product_reviews = data["reviews"]["product"]

    # Count should match items length
    assert product_reviews["count"] == len(product_reviews["items"])

    # Average rating should be between 0 and 5
    if product_reviews["count"] > 0:
        assert 0 <= product_reviews["average_rating"] <= 5

    # Breakdown should have all rating levels
    breakdown = product_reviews["breakdown"]
    assert 1 in breakdown or "1" in breakdown
    assert 2 in breakdown or "2" in breakdown
    assert 3 in breakdown or "3" in breakdown
    assert 4 in breakdown or "4" in breakdown
    assert 5 in breakdown or "5" in breakdown

    # Sum of breakdown counts should equal total count
    breakdown_sum = sum(int(v) for v in breakdown.values())
    assert breakdown_sum == product_reviews["count"]


@pytest.mark.asyncio
async def test_review_items_structure(client):
    """Test that review items have correct structure"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    product_reviews = data["reviews"]["product"]["items"]

    if len(product_reviews) > 0:
        review = product_reviews[0]
        assert "id" in review
        assert "rating" in review
        assert "author_name" in review
        assert "created_at" in review

        # Rating should be 1-5
        assert 1 <= review["rating"] <= 5


@pytest.mark.asyncio
async def test_price_format(client):
    """Test that prices are returned in kopecks (integers)"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    # Main product price
    assert isinstance(data["price"], int)
    assert data["price"] > 0

    # Variant prices
    if len(data["variants"]) > 0:
        for variant in data["variants"]:
            assert isinstance(variant["price"], int)
            assert variant["price"] > 0

    # Addon prices
    if len(data["addons"]) > 0:
        for addon in data["addons"]:
            assert isinstance(addon["price"], int)
            assert addon["price"] >= 0  # Can be 0 for free addons


@pytest.mark.asyncio
async def test_enabled_variants_only(client):
    """Test that only enabled variants are returned"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    # All returned variants should be enabled
    for variant in data["variants"]:
        assert variant["enabled"] is True


@pytest.mark.asyncio
async def test_enabled_addons_only(client):
    """Test that only enabled addons are returned"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    # All returned addons should be enabled
    for addon in data["addons"]:
        assert addon["enabled"] is True


@pytest.mark.asyncio
async def test_bundle_limit(client):
    """Test that frequently bought products are limited to 5"""
    response = await client.get("/api/v1/products/1/detail")
    assert response.status_code == 200
    data = response.json()

    # Should return at most 5 bundled products
    assert len(data["frequently_bought"]) <= 5