#!/usr/bin/env python3
"""
Create test product for Kaspi Pay testing (9 tenge = 900 kopecks)
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Product, ProductType

async def create_test_product():
    """Create a test product priced at 9 tenge (900 kopecks)"""

    async for session in get_session():
        try:
            # Create test product
            test_product = Product(
                name="Тестовый букет (9₸)",
                description="Товар для тестирования Kaspi Pay интеграции. Цена: 9 тенге.",
                price=900,  # 900 kopecks = 9 tenge
                type=ProductType.FLOWERS,
                shop_id=8,  # Cvety.kz shop
                enabled=True
            )

            session.add(test_product)
            await session.commit()
            await session.refresh(test_product)

            print("✅ Test product created successfully!")
            print(f"   ID: {test_product.id}")
            print(f"   Name: {test_product.name}")
            print(f"   Price: {test_product.price} kopecks ({test_product.price / 100} tenge)")
            print(f"   Type: {test_product.type}")
            print(f"   Shop ID: {test_product.shop_id}")
            print(f"   Enabled: {test_product.enabled}")

        except Exception as e:
            print(f"❌ Failed to create test product: {e}")
            await session.rollback()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(create_test_product())
