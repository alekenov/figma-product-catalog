"""
Pytest configuration and fixtures for backend tests
"""
# IMPORTANT: Set environment variables FIRST, before any imports
import os
# Unset DATABASE_URL to force SQLite config
if "DATABASE_URL" in os.environ:
    del os.environ["DATABASE_URL"]

import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def async_engine():
    """Create a fresh async engine for each test"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import models to register them
    import models  # noqa

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine):
    """Create async session for each test"""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(async_session):
    """
    Create test client with overridden database session
    """
    # Import app after engine is set up
    from main import app
    from database import get_session

    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_product(async_session):
    """Create a sample product for testing"""
    from models import Product, ProductType

    product = Product(
        name="Test Bouquet",
        price=1200000,  # 12000 tenge in kopecks
        type=ProductType.FLOWERS,  # Use enum instead of string
        description="Beautiful test bouquet",
        manufacturingTime=24,
        enabled=True,
        is_featured=True,
        tags=["roses", "urgent"],
        cities=["almaty", "astana"],
        image="https://example.com/test.jpg"
    )

    async_session.add(product)
    await async_session.commit()
    await async_session.refresh(product)

    return product


@pytest.fixture
async def sample_warehouse_items(async_session):
    """Create sample warehouse items for testing"""
    from models import WarehouseItem

    items = [
        WarehouseItem(
            name="Red Roses",
            quantity=50,
            cost_price=50000,
            retail_price=80000,
            min_quantity=10
        ),
        WarehouseItem(
            name="Green Leaves",
            quantity=100,
            cost_price=10000,
            retail_price=15000,
            min_quantity=20
        ),
        WarehouseItem(
            name="Ribbon",
            quantity=30,
            cost_price=5000,
            retail_price=8000,
            min_quantity=5
        )
    ]

    for item in items:
        async_session.add(item)

    await async_session.commit()

    # Refresh all items
    for item in items:
        await async_session.refresh(item)

    return items


@pytest.fixture
async def sample_product_with_recipe(async_session, sample_product, sample_warehouse_items):
    """Create a product with recipe (composition)"""
    from models import ProductRecipe

    recipes = [
        ProductRecipe(
            product_id=sample_product.id,
            warehouse_item_id=sample_warehouse_items[0].id,
            quantity=15,
            is_optional=False
        ),
        ProductRecipe(
            product_id=sample_product.id,
            warehouse_item_id=sample_warehouse_items[1].id,
            quantity=5,
            is_optional=False
        ),
        ProductRecipe(
            product_id=sample_product.id,
            warehouse_item_id=sample_warehouse_items[2].id,
            quantity=1,
            is_optional=True
        )
    ]

    for recipe in recipes:
        async_session.add(recipe)

    await async_session.commit()

    return sample_product