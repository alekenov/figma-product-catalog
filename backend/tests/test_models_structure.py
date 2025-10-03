"""
Tests for modular models structure

Verifies that the new modular models package maintains backward compatibility
and all models can be imported and instantiated correctly.
"""
import pytest
from sqlmodel import Session


class TestModelImports:
    """Test that all models can be imported from the models package"""

    def test_import_enums(self):
        """Test importing all enum types"""
        from models import (
            ProductType,
            OrderStatus,
            UserRole,
            WarehouseOperationType,
            City,
            InvitationStatus
        )

        # Verify enum values
        assert ProductType.FLOWERS == "flowers"
        assert OrderStatus.NEW == "new"
        assert UserRole.DIRECTOR == "DIRECTOR"
        assert City.ALMATY == "Almaty"

    def test_import_product_models(self):
        """Test importing product-related models"""
        from models import (
            Product,
            ProductCreate,
            ProductRead,
            ProductUpdate,
            ProductVariant,
            ProductImage,
            ProductAddon,
            ProductBundle
        )

        # Verify classes are importable
        assert Product is not None
        assert ProductCreate is not None

    def test_import_order_models(self):
        """Test importing order-related models"""
        from models import (
            Order,
            OrderCreate,
            OrderRead,
            OrderItem,
            OrderPhoto,
            OrderHistory
        )

        assert Order is not None
        assert OrderCreate is not None

    def test_import_warehouse_models(self):
        """Test importing warehouse-related models"""
        from models import (
            WarehouseItem,
            WarehouseOperation,
            ProductRecipe,
            OrderReservation,
            InventoryCheck
        )

        assert WarehouseItem is not None
        assert ProductRecipe is not None

    def test_import_user_models(self):
        """Test importing user-related models"""
        from models import (
            User,
            Client,
            TeamInvitation,
            LoginRequest,
            LoginResponse
        )

        assert User is not None
        assert Client is not None

    def test_import_shop_models(self):
        """Test importing shop-related models"""
        from models import (
            Shop,
            ShopSettings,
            PickupLocation,
            OrderCounter
        )

        assert Shop is not None
        assert ShopSettings is not None

    def test_import_review_models(self):
        """Test importing review-related models"""
        from models import (
            ProductReview,
            CompanyReview,
            FAQ,
            StaticPage
        )

        assert ProductReview is not None
        assert FAQ is not None


@pytest.mark.asyncio
class TestModelCreation:
    """Test creating instances of models"""

    async def test_create_product(self, async_session, sample_shop):
        """Test creating a Product instance"""
        from models import Product, ProductType

        product = Product(
            name="Test Product",
            price=100000,
            type=ProductType.FLOWERS,
            enabled=True,
            shop_id=sample_shop.id
        )

        async_session.add(product)
        await async_session.commit()
        await async_session.refresh(product)

        assert product.id is not None
        assert product.name == "Test Product"
        assert product.type == ProductType.FLOWERS

    async def test_create_warehouse_item(self, async_session, sample_shop):
        """Test creating a WarehouseItem instance"""
        from models import WarehouseItem

        item = WarehouseItem(
            name="Test Item",
            quantity=10,
            cost_price=5000,
            retail_price=8000,
            shop_id=sample_shop.id
        )

        async_session.add(item)
        await async_session.commit()
        await async_session.refresh(item)

        assert item.id is not None
        assert item.name == "Test Item"
        assert item.quantity == 10


@pytest.mark.asyncio
class TestModelRelationships:
    """Test relationships between models work correctly"""

    async def test_product_recipe_relationship(self, async_session, sample_shop):
        """Test Product -> ProductRecipe -> WarehouseItem relationship"""
        from models import Product, ProductType, WarehouseItem, ProductRecipe

        # Create warehouse item
        warehouse_item = WarehouseItem(
            name="Roses",
            quantity=100,
            cost_price=5000,
            retail_price=8000,
            shop_id=sample_shop.id
        )
        async_session.add(warehouse_item)
        await async_session.commit()
        await async_session.refresh(warehouse_item)

        # Create product
        product = Product(
            name="Bouquet",
            price=200000,
            type=ProductType.FLOWERS,
            enabled=True,
            shop_id=sample_shop.id
        )
        async_session.add(product)
        await async_session.commit()
        await async_session.refresh(product)

        # Create recipe linking them
        recipe = ProductRecipe(
            product_id=product.id,
            warehouse_item_id=warehouse_item.id,
            quantity=10
        )
        async_session.add(recipe)
        await async_session.commit()

        # Verify relationship
        assert recipe.product_id == product.id
        assert recipe.warehouse_item_id == warehouse_item.id

    async def test_order_items_relationship(self, async_session, sample_shop):
        """Test Order -> OrderItem relationship"""
        from models import Order, OrderItem, Product, ProductType, OrderStatus

        # Create product first
        product = Product(
            name="Test Product",
            price=100000,
            type=ProductType.FLOWERS,
            enabled=True,
            shop_id=sample_shop.id
        )
        async_session.add(product)
        await async_session.commit()
        await async_session.refresh(product)

        # Create order
        order = Order(
            tracking_id="123456789",
            orderNumber="#00001",
            customerName="Test Customer",
            phone="+77001234567",
            subtotal=100000,
            total=100000,
            status=OrderStatus.NEW,
            shop_id=sample_shop.id
        )
        async_session.add(order)
        await async_session.commit()
        await async_session.refresh(order)

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=1,
            item_total=product.price
        )
        async_session.add(order_item)
        await async_session.commit()

        # Verify relationship
        assert order_item.order_id == order.id
        assert order_item.product_id == product.id


class TestSchemas:
    """Test that schemas can be instantiated"""

    def test_product_create_schema(self):
        """Test ProductCreate schema"""
        from models import ProductCreate, ProductType

        data = ProductCreate(
            name="Test",
            price=100000,
            type=ProductType.FLOWERS
        )

        assert data.name == "Test"
        assert data.price == 100000

    def test_order_create_schema(self):
        """Test OrderCreate schema"""
        from models import OrderCreate

        data = OrderCreate(
            customerName="John Doe",
            phone="+77001234567"
        )

        assert data.customerName == "John Doe"
        assert data.phone == "+77001234567"

    def test_warehouse_item_create_schema(self):
        """Test WarehouseItemCreate schema"""
        from models import WarehouseItemCreate

        data = WarehouseItemCreate(
            name="Roses",
            quantity=50,
            cost_price_tenge=500,
            retail_price_tenge=800
        )

        assert data.name == "Roses"
        assert data.quantity == 50
        # Test tenge to kopecks conversion
        assert data.cost_price == 50000
        assert data.retail_price == 80000


class TestBackwardCompatibility:
    """Test that old import style still works"""

    def test_import_from_models_package(self):
        """Test that models can be imported directly from models package"""
        # This should work exactly as before the refactoring
        from models import Product, Order, WarehouseItem, User, Shop
        from models import ProductType, OrderStatus, UserRole

        assert Product is not None
        assert Order is not None
        assert WarehouseItem is not None
        assert User is not None
        assert Shop is not None
        assert ProductType is not None
        assert OrderStatus is not None
        assert UserRole is not None
