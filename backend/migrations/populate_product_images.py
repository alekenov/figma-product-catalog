"""
Migration: Populate productimage table from product.image field

This migration creates ProductImage records from the legacy product.image field
to support the new multi-image architecture while maintaining backward compatibility.

Run this ONCE to migrate existing products to the new image system.
"""

import sys
import os

# Add backend directory to path so we can import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product, ProductImage

def migrate_product_images():
    """Migrate product.image to productimage table"""

    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figma_catalog.db')
    database_url = f'sqlite:///{db_path}'

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get all products that have an image but no ProductImage records
        products = session.query(Product).filter(
            Product.image.isnot(None),
            Product.image != ''
        ).all()

        print(f"Found {len(products)} products with images")

        migrated_count = 0
        skipped_count = 0

        for product in products:
            # Check if product already has ProductImage records
            existing_images = session.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).count()

            if existing_images > 0:
                print(f"  Skipping product {product.id} (already has {existing_images} images)")
                skipped_count += 1
                continue

            # Create new ProductImage record from product.image
            product_image = ProductImage(
                product_id=product.id,
                url=product.image,
                is_primary=True,  # First image is primary
                order=0  # First in order
            )

            session.add(product_image)
            migrated_count += 1
            print(f"  Migrated product {product.id}: {product.name[:50]}...")

        # Commit all changes
        session.commit()

        print(f"\n✅ Migration complete!")
        print(f"   Migrated: {migrated_count} products")
        print(f"   Skipped: {skipped_count} products (already had images)")

    except Exception as e:
        session.rollback()
        print(f"❌ Migration failed: {e}")
        raise

    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Populate productimage table")
    print("=" * 60)

    migrate_product_images()
