"""
Add product images to shop_id=8 products using existing R2 URLs.
"""
import asyncio
from sqlmodel import select
from models import Product, ProductImage
from database import async_session

# Existing R2 image URLs from shop_id=1
IMAGE_URLS = [
    "https://flower-shop-images.alekenov.workers.dev/mg6l8u8m-ozvi19rnnmp.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg6l8x64-5faaoyisrqx.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg6l8yys-tmfup88jomo.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg6l91q4-3rsc2jcpncm.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg6l945s-6pkc2zyqr6b.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg6l95yp-0z3nck6gxrb.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg6l98au-8dajmflljlr.jpeg",
    "https://flower-shop-images.alekenov.workers.dev/mg92y6aa-n7eo6xcnct.jpg",
    "https://flower-shop-images.alekenov.workers.dev/mg92y83h-op6fldb085r.jpg",
    "https://flower-shop-images.alekenov.workers.dev/mg92y9hq-x1as7hr3h3i.jpg",
]

async def add_images():
    """Add images to shop_id=8 products."""

    async with async_session() as session:
        # Get all products from shop_id=8
        result = await session.execute(
            select(Product).where(Product.shop_id == 8).limit(10)
        )
        products = list(result.scalars().all())

        print(f"\n📊 Found {len(products)} products in shop_id=8")

        created_count = 0

        for i, product in enumerate(products):
            # Check if product already has images
            result = await session.execute(
                select(ProductImage).where(ProductImage.product_id == product.id)
            )
            existing_images = list(result.scalars().all())

            if existing_images:
                print(f"  ⏭️  Product {product.id} ({product.name}) already has images, skipping")
                continue

            # Add image (cycle through available URLs)
            image_url = IMAGE_URLS[i % len(IMAGE_URLS)]

            product_image = ProductImage(
                product_id=product.id,
                url=image_url,
                order=0,
                is_primary=True
            )
            session.add(product_image)
            print(f"  ✅ Added image to product {product.id} ({product.name})")
            created_count += 1

        # Commit all changes
        await session.commit()

        print(f"\n📊 Migration complete!")
        print(f"  - Created: {created_count} ProductImage records")
        print(f"  - Skipped: {len(products) - created_count} products")

if __name__ == "__main__":
    asyncio.run(add_images())
