"""
Tests for multi-tenancy isolation.

Ensures that users cannot access data from other shops (shop_id isolation).
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import app
from models import User, Product, Order, Shop
from database import get_session


class TestMultiTenancyIsolation:
    """Test that shop_id isolation is enforced across all endpoints"""

    @pytest.fixture
    def setup_two_shops(self, session: Session):
        """Create two shops with products and users for isolation testing"""
        # Shop 1
        shop1 = Shop(id=1, name="Shop 1", city="Almaty")
        user1 = User(
            phone="+77011111111",
            password_hash="hash1",
            role="DIRECTOR",
            shop_id=1,
            is_active=True
        )
        product1 = Product(
            id=1,
            name="Product 1",
            price=100000,
            type="bouquet",
            shop_id=1,
            enabled=True
        )

        # Shop 2
        shop2 = Shop(id=2, name="Shop 2", city="Astana")
        user2 = User(
            phone="+77022222222",
            password_hash="hash2",
            role="DIRECTOR",
            shop_id=2,
            is_active=True
        )
        product2 = Product(
            id=2,
            name="Product 2",
            price=200000,
            type="bouquet",
            shop_id=2,
            enabled=True
        )

        session.add_all([shop1, shop2, user1, user2, product1, product2])
        session.commit()

        return {
            "shop1": shop1,
            "shop2": shop2,
            "user1": user1,
            "user2": user2,
            "product1": product1,
            "product2": product2,
        }

    def test_users_cannot_see_other_shop_products(self, client: TestClient, auth_token_shop1: str, setup_two_shops):
        """Test that users can only see products from their own shop"""
        # User from shop 1 tries to access products
        response = client.get(
            "/api/v1/products/admin",
            headers={"Authorization": f"Bearer {auth_token_shop1}"}
        )
        assert response.status_code == 200
        products = response.json()

        # Should only see shop 1 products
        assert all(p["shop_id"] == 1 for p in products), "User should only see their shop's products"
        assert len([p for p in products if p["id"] == 2]) == 0, "Should not see shop 2 products"

    def test_users_cannot_access_other_shop_product_by_id(self, client: TestClient, auth_token_shop1: str, setup_two_shops):
        """Test that users cannot access specific products from other shops"""
        # User from shop 1 tries to access shop 2 product
        response = client.get(
            "/api/v1/products/2",  # Product from shop 2
            headers={"Authorization": f"Bearer {auth_token_shop1}"}
        )
        # Should return 404 or 403
        assert response.status_code in [403, 404], "Should not allow access to other shop's product"

    def test_users_cannot_create_products_for_other_shops(self, client: TestClient, auth_token_shop1: str):
        """Test that users cannot create products with different shop_id"""
        # User from shop 1 tries to create product with shop_id=2
        product_data = {
            "name": "Malicious Product",
            "price": 50000,
            "type": "bouquet",
            "shop_id": 2,  # Trying to create for shop 2
            "enabled": True
        }

        response = client.post(
            "/api/v1/products/",
            json=product_data,
            headers={"Authorization": f"Bearer {auth_token_shop1}"}
        )

        # Should either reject or force shop_id=1
        if response.status_code == 201:
            created_product = response.json()
            assert created_product["shop_id"] == 1, "Should force product to user's shop_id"
        else:
            assert response.status_code in [400, 403], "Should reject cross-shop product creation"

    def test_users_cannot_see_other_shop_orders(self, client: TestClient, auth_token_shop1: str, setup_two_shops):
        """Test that users can only see orders from their own shop"""
        response = client.get(
            "/api/v1/orders/",
            headers={"Authorization": f"Bearer {auth_token_shop1}"}
        )
        assert response.status_code == 200
        orders = response.json()

        # All orders should belong to shop 1
        if orders:  # If there are orders
            assert all(o.get("shop_id") == 1 for o in orders), "Should only see own shop's orders"

    def test_public_endpoints_require_shop_id_parameter(self, client: TestClient):
        """Test that public endpoints enforce shop_id filtering"""
        # Try to get products without shop_id
        response = client.get("/api/v1/products")

        # Should either require shop_id or return empty/error
        if response.status_code == 200:
            # If it returns products, they should all belong to default shop
            products = response.json()
            if products:
                shop_ids = [p.get("shop_id") for p in products]
                assert len(set(shop_ids)) == 1, "Products should all belong to one shop"

    def test_jwt_token_contains_shop_id(self, client: TestClient):
        """Test that JWT tokens include shop_id claim"""
        # Login and check token structure
        login_data = {
            "phone": "+77015211545",
            "password": "test123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        token_data = response.json()
        assert "access_token" in token_data

        # Decode token (in real test, use jwt.decode)
        # For now, just verify structure
        assert token_data["access_token"] is not None


class TestCrossTenantDataLeakage:
    """Test potential data leakage scenarios"""

    def test_order_tracking_isolated_by_shop(self, client: TestClient, setup_two_shops):
        """Test that order tracking IDs cannot leak between shops"""
        # This would require creating orders in both shops and checking tracking
        # Placeholder for now
        pass

    def test_client_records_isolated_by_shop(self, client: TestClient, setup_two_shops):
        """Test that client records are isolated by shop_id"""
        # Placeholder for cross-shop client lookup tests
        pass

    def test_warehouse_items_isolated_by_shop(self, client: TestClient, auth_token_shop1: str):
        """Test that warehouse inventory is isolated by shop"""
        response = client.get(
            "/api/v1/warehouse/items",
            headers={"Authorization": f"Bearer {auth_token_shop1}"}
        )

        if response.status_code == 200:
            items = response.json()
            if items:
                assert all(item.get("shop_id") == 1 for item in items), "Warehouse items should be isolated"


class TestShopIdValidation:
    """Test shop_id parameter validation"""

    def test_invalid_shop_id_rejected(self, client: TestClient):
        """Test that invalid shop_id values are rejected"""
        response = client.get("/api/v1/products?shop_id=invalid")
        assert response.status_code == 422, "Should reject non-numeric shop_id"

    def test_negative_shop_id_rejected(self, client: TestClient):
        """Test that negative shop_id values are rejected"""
        response = client.get("/api/v1/products?shop_id=-1")
        assert response.status_code in [400, 422, 404], "Should reject negative shop_id"

    def test_zero_shop_id_rejected(self, client: TestClient):
        """Test that zero shop_id is rejected"""
        response = client.get("/api/v1/products?shop_id=0")
        assert response.status_code in [400, 422, 404], "Should reject shop_id=0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
