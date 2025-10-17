#!/usr/bin/env python3
"""
Script to populate product data for better AI consultation
Updates: colors, tags, descriptions, manufacturingTime
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = backend_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import select
from models import Product

# Database connection - same logic as database.py
if os.getenv("DATABASE_URL"):
    # Production (Railway/Render) - PostgreSQL
    from config_render import settings
    DATABASE_URL = settings.database_url_async
    print(f"✅ Using PostgreSQL from DATABASE_URL")
else:
    # Local development - SQLite
    from config_sqlite import settings
    DATABASE_URL = settings.database_url
    print(f"✅ Using SQLite: {DATABASE_URL}")

# Product data updates based on approved plan
PRODUCT_UPDATES = {
    1: {  # Букет роз (21 шт)
        "colors": ["красный"],
        "tags": ["bestseller", "same-day"],
        "description": "Классический букет из 21 красной розы премиум класса (60 см). Розы Freedom - голландская селекция с насыщенным красным цветом и крупными бутонами. Упакован в дизайнерскую крафт-бумагу с атласной лентой. Идеальный выбор для романтического подарка.",
        "manufacturingTime": 20,
        "shelfLife": 7
    },
    2: {  # Букет тюльпанов (25 шт)
        "colors": ["желтый"],
        "tags": ["seasonal", "same-day"],
        "description": "Весенний букет из 25 желтых тюльпанов сорта Strong Gold (40 см). Свежие голландские тюльпаны с крупными бутонами, собранные в изящную композицию. Упаковка - натуральная крафт-бумага с джутовой лентой. Дарит весеннее настроение и радость.",
        "manufacturingTime": 15,
        "shelfLife": 5
    },
    3: {  # Букет невесты
        "colors": ["белый", "розовый"],
        "tags": ["premium", "new"],
        "description": "Элегантный свадебный букет из белых роз Avalanche и нежно-розовых пионов. Состав: 15 роз (50 см), 7 пионов, зелень (эвкалипт, питтоспорум). Оформление в европейском стиле с атласными лентами. Создается флористом индивидуально по предварительному заказу.",
        "manufacturingTime": 60,
        "shelfLife": 5
    },
    4: {  # Букет ромашек (11 шт)
        "colors": ["белый"],
        "tags": ["budget", "same-day"],
        "description": "Летний букет из 11 белых ромашек (кустовая хризантема) с желтой серединкой. Простота и нежность полевых цветов в стильной упаковке. Дополнен декоративной зеленью. Отличный выбор для повседневного подарка и поднятия настроения.",
        "manufacturingTime": 10,
        "shelfLife": 7
    },
    5: {  # Набор конфет Raffaello
        "colors": None,  # Sweets don't have flower colors
        "tags": ["bestseller", "addon"],
        "description": "Элитные конфеты Ferrero Raffaello (150г) - нежное кокосовое лакомство с миндалем внутри. Идеальное дополнение к букету цветов. Изысканная упаковка делает подарок еще более праздничным. Производство: Италия.",
        "manufacturingTime": None,  # No preparation needed
        "shelfLife": 180  # 6 months shelf life for chocolates
    }
}


async def update_products():
    """Update products with enriched data for AI consultation"""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n=== Starting Product Data Update ===\n")

        for product_id, updates in PRODUCT_UPDATES.items():
            # Fetch product
            result = await session.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()

            if not product:
                print(f"⚠️  Product ID {product_id} not found, skipping...")
                continue

            print(f"\n📦 Updating: {product.name} (ID: {product.id})")
            print(f"   Before: colors={product.colors}, tags={product.tags}, "
                  f"manufacturingTime={product.manufacturingTime}")

            # Apply updates
            product.colors = updates["colors"]
            product.tags = updates["tags"]
            product.description = updates["description"]
            product.manufacturingTime = updates["manufacturingTime"]
            product.shelfLife = updates["shelfLife"]

            print(f"   After:  colors={product.colors}, tags={product.tags}, "
                  f"manufacturingTime={product.manufacturingTime}")
            print(f"   ✅ Updated successfully")

        # Commit all changes
        await session.commit()
        print("\n=== All products updated successfully! ===\n")

    await engine.dispose()


async def verify_updates():
    """Verify that updates were applied correctly"""

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n=== Verifying Updates ===\n")

        result = await session.execute(
            select(Product).where(Product.id.in_(PRODUCT_UPDATES.keys()))
        )
        products = result.scalars().all()

        for product in products:
            print(f"\n{product.name}:")
            print(f"  • Colors: {product.colors}")
            print(f"  • Tags: {product.tags}")
            print(f"  • Manufacturing Time: {product.manufacturingTime} min")
            print(f"  • Shelf Life: {product.shelfLife} days")
            print(f"  • Description: {product.description[:100]}...")

    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Product Data Population Script")
    print("=" * 50)

    try:
        # Run updates
        asyncio.run(update_products())

        # Verify
        asyncio.run(verify_updates())

        print("\n✨ All done! Products are now AI-ready for better consultation.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
