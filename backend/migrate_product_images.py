"""
Migration script to create ProductImage records from Product.image field.

This script finds products that have an image URL but no ProductImage records,
and creates a single ProductImage record for each with is_primary=True.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from models import Product, ProductImage
from database import settings, async_session

async def migrate_product_images():
    """Create ProductImage records for products that don't have any."""

    async with async_session() as session:
        # Get all products
        result = await session.execute(
            select(Product).where(Product.enabled == True)
        )
        products = list(result.scalars().all())

        print(f"\n📊 Found {len(products)} enabled products")

        created_count = 0
        skipped_count = 0

        for product in products:
            # Check if product already has ProductImage records
            result = await session.execute(
                select(ProductImage).where(ProductImage.product_id == product.id)
            )
            existing_images = list(result.scalars().all())

            if existing_images:
                print(f"  ⏭️  Product {product.id} ({product.name}) already has {len(existing_images)} image(s), skipping")
                skipped_count += 1
                continue

            # Check if product has image URL
            if not product.image:
                print(f"  ⚠️  Product {product.id} ({product.name}) has no image URL, skipping")
                skipped_count += 1
                continue

            # Create ProductImage record
            product_image = ProductImage(
                product_id=product.id,
                url=product.image,
                order=0,
                is_primary=True
            )
            session.add(product_image)
            print(f"  ✅ Created ProductImage for product {product.id} ({product.name})")
            created_count += 1

        # Commit all changes
        await session.commit()

        print(f"\n📊 Migration complete!")
        print(f"  - Created: {created_count} ProductImage records")
        print(f"  - Skipped: {skipped_count} products")

if __name__ == "__main__":
    asyncio.run(migrate_product_images())
