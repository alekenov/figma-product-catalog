"""
Tests for product API endpoints with detail enrichment
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_product_detail_success(client: AsyncClient, sample_product_with_recipe):
    """Test /products/{id}/detail returns enriched product data"""
    product_id = sample_product_with_recipe.id

    response = await client.get(f"/api/v1/products/{product_id}/detail")

    assert response.status_code == 200
    data = response.json()

    # Basic product fields
    assert data["id"] == product_id
    assert data["name"] == "Test Bouquet"
    assert data["price"] == 1200000

    # Check enrichment: composition
    assert "composition" in data
    assert len(data["composition"]) == 3
    assert data["composition"][0]["name"] == "Red Roses"
    assert data["composition"][0]["quantity"] == 15

    # Check enrichment: variants (even if empty)
    assert "variants" in data

    # Check enrichment: addons (even if empty)
    assert "addons" in data

    # Check enrichment: frequently_bought (even if empty)
    assert "frequently_bought" in data

    # Check enrichment: reviews structure
    assert "reviews" in data
    assert "product" in data["reviews"]
    assert "company" in data["reviews"]

    # Check enrichment: pickup_locations (even if empty)
    assert "pickup_locations" in data


@pytest.mark.asyncio
async def test_get_product_detail_not_found(client: AsyncClient):
    """Test /products/{id}/detail returns 404 for non-existent product"""
    response = await client.get("/api/v1/products/999999/detail")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_home_products(client: AsyncClient, sample_product):
    """Test /products/home returns featured products"""
    response = await client.get("/api/v1/products/home")

    assert response.status_code == 200
    data = response.json()

    assert "featured" in data
    assert "available_tags" in data
    assert "bestsellers" in data

    # Should include our featured product
    assert len(data["featured"]) >= 1
    featured_product = next((p for p in data["featured"] if p["id"] == sample_product.id), None)
    assert featured_product is not None
    assert featured_product["name"] == "Test Bouquet"


@pytest.mark.asyncio
async def test_get_home_products_with_tag_filter(client: AsyncClient, sample_product):
    """Test /products/home filters by tags"""
    # Filter by 'roses' tag
    response = await client.get("/api/v1/products/home?tags=roses")

    assert response.status_code == 200
    data = response.json()

    # Should include product with 'roses' tag
    assert len(data["featured"]) >= 1
    product_ids = [p["id"] for p in data["featured"]]
    assert sample_product.id in product_ids


@pytest.mark.asyncio
async def test_get_home_products_with_city_filter(client: AsyncClient, sample_product):
    """Test /products/home filters by city"""
    # Filter by 'almaty' city
    response = await client.get("/api/v1/products/home?city=almaty")

    assert response.status_code == 200
    data = response.json()

    # Should include product available in Almaty
    product_ids = [p["id"] for p in data["featured"]]
    assert sample_product.id in product_ids


@pytest.mark.asyncio
async def test_get_filters(client: AsyncClient, sample_product):
    """Test /products/filters returns available filter options"""
    response = await client.get("/api/v1/products/filters")

    assert response.status_code == 200
    data = response.json()

    assert "tags" in data
    assert "cities" in data
    assert "price_range" in data
    assert "product_types" in data

    # Should include tags from our sample product
    assert "roses" in data["tags"]
    assert "urgent" in data["tags"]

    # Should include cities
    assert "almaty" in data["cities"]
    assert "astana" in data["cities"]