#!/usr/bin/env python3
"""
Clear Test Data Script

Removes all test products (IDs 1-6) that contain Figma URLs from the database.
Related records (images, variants, recipes, addons, bundles, reviews) will be
deleted via database cascade constraints.

Usage:
    python3 clear_test_data.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database import async_session
from models import Product


async def clear_test_products():
    """Delete all test products with Figma URLs"""
    from models import OrderItem, ProductImage, ProductVariant, ProductRecipe, ProductAddon, ProductBundle, ProductReview

    async with async_session() as session:
        print("🔍 Finding test products to delete...")

        # Test product IDs from seed_data.py
        test_product_ids = [1, 2, 3, 4, 5, 6]

        # Find products
        result = await session.execute(
            select(Product).where(Product.id.in_(test_product_ids))
        )
        products = result.scalars().all()

        if not products:
            print("✅ No test products found. Database is clean.")
            return

        print(f"📦 Found {len(products)} test products to delete:")
        for product in products:
            print(f"   - ID {product.id}: {product.name}")

        # Step 1: Delete OrderItems first (NOT NULL constraint on product_id)
        print("\n🗑️  Deleting OrderItems...")
        order_items_result = await session.execute(
            select(OrderItem).where(OrderItem.product_id.in_(test_product_ids))
        )
        order_items = order_items_result.scalars().all()
        for item in order_items:
            await session.delete(item)
        print(f"   Deleted {len(order_items)} OrderItem records")

        # Step 2: Delete related records
        print("\n🗑️  Deleting related records...")

        # ProductImages
        images_result = await session.execute(
            select(ProductImage).where(ProductImage.product_id.in_(test_product_ids))
        )
        images = images_result.scalars().all()
        for image in images:
            await session.delete(image)
        print(f"   Deleted {len(images)} ProductImage records")

        # ProductVariants
        variants_result = await session.execute(
            select(ProductVariant).where(ProductVariant.product_id.in_(test_product_ids))
        )
        variants = variants_result.scalars().all()
        for variant in variants:
            await session.delete(variant)
        print(f"   Deleted {len(variants)} ProductVariant records")

        # ProductRecipes
        recipes_result = await session.execute(
            select(ProductRecipe).where(ProductRecipe.product_id.in_(test_product_ids))
        )
        recipes = recipes_result.scalars().all()
        for recipe in recipes:
            await session.delete(recipe)
        print(f"   Deleted {len(recipes)} ProductRecipe records")

        # ProductAddons
        addons_result = await session.execute(
            select(ProductAddon).where(ProductAddon.product_id.in_(test_product_ids))
        )
        addons = addons_result.scalars().all()
        for addon in addons:
            await session.delete(addon)
        print(f"   Deleted {len(addons)} ProductAddon records")

        # ProductBundles (both main_product_id and bundled_product_id)
        bundles_result = await session.execute(
            select(ProductBundle).where(
                (ProductBundle.main_product_id.in_(test_product_ids)) |
                (ProductBundle.bundled_product_id.in_(test_product_ids))
            )
        )
        bundles = bundles_result.scalars().all()
        for bundle in bundles:
            await session.delete(bundle)
        print(f"   Deleted {len(bundles)} ProductBundle records")

        # ProductReviews (need to delete ReviewPhotos first)
        reviews_result = await session.execute(
            select(ProductReview).where(ProductReview.product_id.in_(test_product_ids))
        )
        reviews = reviews_result.scalars().all()

        # Delete ReviewPhotos first
        from models import ReviewPhoto
        review_ids = [r.id for r in reviews]
        if review_ids:
            review_photos_result = await session.execute(
                select(ReviewPhoto).where(ReviewPhoto.review_id.in_(review_ids))
            )
            review_photos = review_photos_result.scalars().all()
            for photo in review_photos:
                await session.delete(photo)
            print(f"   Deleted {len(review_photos)} ReviewPhoto records")

        # Now delete reviews
        for review in reviews:
            await session.delete(review)
        print(f"   Deleted {len(reviews)} ProductReview records")

        # Step 3: Finally delete products
        print("\n🗑️  Deleting products...")
        for product in products:
            await session.delete(product)

        await session.commit()

        print(f"\n✅ Successfully deleted {len(products)} test products and all related data")


async def main():
    print("=" * 60)
    print("🧹 Test Data Cleanup Script")
    print("=" * 60)
    print()

    try:
        await clear_test_products()
        print()
        print("=" * 60)
        print("✅ Cleanup completed successfully!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error during cleanup: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    asyncio.run(main())