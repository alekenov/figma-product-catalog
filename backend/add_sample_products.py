#!/usr/bin/env python3
"""
Add sample products to local database with vitrina and catalog types
Based on real production API data structure
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Product, ProductImage
from datetime import datetime

# Database connection
DATABASE_URL = "sqlite+aiosqlite:///./figma_catalog.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def add_sample_products():
    async with AsyncSessionLocal() as session:
        # Sample Vitrina products (готовые букеты)
        vitrina_products = [
            {
                "name": "Собранный букет",
                "type": "vitrina",
                "price": 2000000,  # 20000 tenge in kopecks
                "description": "Красивый собранный букет из свежих цветов",
                "enabled": True,
                "is_featured": True,
                "image": "https://cvety.kz/upload/resize_cache/iblock/24e/qqa0csfw0277wr9y67fivoo09og8owtx/435_545_2/image.jpg",
                "images": [
                    "https://cvety.kz/upload/resize_cache/iblock/24e/qqa0csfw0277wr9y67fivoo09og8owtx/435_545_2/image.jpg"
                ],
                "discount": 0,
                "width": None,
                "height": None,
            },
            {
                "name": "Букет роз премиум",
                "type": "vitrina",
                "price": 3500000,  # 35000 tenge
                "description": "Премиальный букет из 25 роз",
                "enabled": True,
                "is_featured": False,
                "image": "https://cvety.kz/upload/resize_cache/iblock/123/placeholder.jpg",
                "images": [
                    "https://cvety.kz/upload/resize_cache/iblock/123/placeholder.jpg"
                ],
                "discount": 10,  # 10% discount
                "width": None,
                "height": None,
            },
            {
                "name": "Микс тюльпанов",
                "type": "vitrina",
                "price": 1500000,  # 15000 tenge
                "description": "Яркий букет из разноцветных тюльпанов",
                "enabled": True,
                "is_featured": True,
                "image": "https://cvety.kz/upload/resize_cache/iblock/456/placeholder.jpg",
                "images": [
                    "https://cvety.kz/upload/resize_cache/iblock/456/placeholder.jpg",
                    "https://cvety.kz/upload/resize_cache/iblock/457/placeholder2.jpg"
                ],
                "discount": 0,
                "width": None,
                "height": None,
            }
        ]

        # Sample Catalog products (каталожные товары)
        catalog_products = [
            {
                "name": "25 белых роз в пачке оптом",
                "type": "catalog",
                "price": 1687500,  # 16875 tenge
                "description": "Оптовая поставка белых роз",
                "enabled": True,
                "is_featured": False,
                "image": "https://cvety.kz/upload/resize_cache/iblock/7d0/etsgzuvcffmcgmufn55znbt7iw0xihuu/435_545_2/24c3c85e_45be_46bb_898c_d009e4656593.jpeg",
                "images": [
                    "https://cvety.kz/upload/resize_cache/iblock/7d0/etsgzuvcffmcgmufn55znbt7iw0xihuu/435_545_2/24c3c85e_45be_46bb_898c_d009e4656593.jpeg"
                ],
                "discount": 0,
                "width": "",
                "height": "50 см",
            },
            {
                "name": "Пионы розовые (каталог)",
                "type": "catalog",
                "price": 2500000,  # 25000 tenge
                "description": "Сезонные пионы для флористов",
                "enabled": True,
                "is_featured": False,
                "image": "https://cvety.kz/upload/resize_cache/iblock/789/placeholder.jpg",
                "images": [
                    "https://cvety.kz/upload/resize_cache/iblock/789/placeholder.jpg"
                ],
                "discount": 15,  # 15% discount
                "width": "40 см",
                "height": "60 см",
            },
            {
                "name": "Эустома белая (каталог)",
                "type": "catalog",
                "price": 800000,  # 8000 tenge
                "description": "Белая эустома для композиций",
                "enabled": True,
                "is_featured": False,
                "image": "https://cvety.kz/upload/resize_cache/iblock/101/placeholder.jpg",
                "images": [
                    "https://cvety.kz/upload/resize_cache/iblock/101/placeholder.jpg",
                    "https://cvety.kz/upload/resize_cache/iblock/102/placeholder2.jpg"
                ],
                "discount": 0,
                "width": "30 см",
                "height": "45 см",
            }
        ]

        all_products = vitrina_products + catalog_products

        # Add products with images
        for product_data in all_products:
            # Extract images list
            images_list = product_data.pop("images", [])

            # Create product
            product = Product(
                **product_data,
                shop_id=8,  # Default shop_id for local dev
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(product)
            await session.flush()  # Get product ID

            # Add product images
            for idx, image_url in enumerate(images_list):
                product_image = ProductImage(
                    product_id=product.id,
                    shop_id=8,
                    url=image_url,
                    is_primary=(idx == 0),
                    created_at=datetime.utcnow()
                )
                session.add(product_image)

        await session.commit()
        print(f"✅ Added {len(all_products)} sample products:")
        print(f"   - {len(vitrina_products)} vitrina products (готовые букеты)")
        print(f"   - {len(catalog_products)} catalog products (каталожные товары)")

if __name__ == "__main__":
    asyncio.run(add_sample_products())
