#!/usr/bin/env python3
"""
Sync products from Production cvety.kz API to Railway PostgreSQL
and generate embeddings for visual search.
"""
import asyncio
import httpx
import os
from typing import List, Dict, Optional
import asyncpg
from datetime import datetime

# Production API
PRODUCTION_API = "https://cvety.kz/api/v2/products"
ACCESS_TOKEN = "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"

# Embedding Service
EMBEDDING_SERVICE = "https://embedding-service-production-4aaa.up.railway.app"

# Railway PostgreSQL
DATABASE_URL = "postgresql://postgres:ua4k2kfhzypqpqlolvtsfx382w4ravqw@maglev.proxy.rlwy.net:49800/railway"

# Shop ID for Railway
SHOP_ID = 17008


async def fetch_production_products() -> List[Dict]:
    """Fetch all products from Production API."""
    print("📦 Fetching products from Production API...")

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response = await client.get(
            PRODUCTION_API,
            params={"access_token": ACCESS_TOKEN, "limit": 200}
        )

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(response.text[:500])
            return []

        data = response.json()
        products = data.get("data", [])
        print(f"✅ Fetched {len(products)} products from Production")
        return products


async def generate_embedding(image_url: str, product_id: int) -> Optional[List[float]]:
    """Generate embedding for an image."""
    print(f"  🧠 Generating embedding for product {product_id}...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{EMBEDDING_SERVICE}/embed/image",
                json={"image_url": image_url, "product_id": product_id}
            )

            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding")
                if embedding and len(embedding) == 512:
                    print(f"  ✅ Embedding generated: 512 dimensions")
                    return embedding
                else:
                    print(f"  ⚠️  Invalid embedding size: {len(embedding) if embedding else 0}")
                    return None
            else:
                print(f"  ❌ Embedding service error: {response.status_code}")
                return None

        except Exception as e:
            print(f"  ❌ Failed to generate embedding: {e}")
            return None


async def save_product_to_db(conn: asyncpg.Connection, product: Dict, embedding: Optional[List[float]]) -> bool:
    """Save product and its embedding to PostgreSQL."""

    # Extract product data
    product_id = product.get("id")
    name = product.get("title", "").strip()
    price_str = product.get("price", "0")
    image_url = product.get("image")
    is_available = product.get("isAvailable", True)
    created_at_str = product.get("createdAt")

    # Parse createdAt (format: "2025-10-21T14:24:50+0500")
    from dateutil import parser as date_parser
    try:
        if created_at_str:
            parsed_dt = date_parser.parse(created_at_str)
            # Convert to UTC and remove timezone info for PostgreSQL
            product_created_at = parsed_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        else:
            product_created_at = datetime.utcnow()
    except:
        product_created_at = datetime.utcnow()

    # Parse price (handle string format like "15,000 ₸")
    try:
        price_clean = price_str.replace(",", "").replace("₸", "").replace(" ", "").strip()
        price_kopecks = int(float(price_clean) * 100)
    except:
        print(f"  ⚠️  Failed to parse price: {price_str}, using 0")
        price_kopecks = 0

    if not name or not image_url:
        print(f"  ⚠️  Skipping product {product_id}: missing name or image")
        return False

    try:
        # Insert or update product
        await conn.execute("""
            INSERT INTO product (id, name, price, image, type, enabled, shop_id, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id, shop_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                price = EXCLUDED.price,
                image = EXCLUDED.image,
                enabled = EXCLUDED.enabled,
                updated_at = EXCLUDED.updated_at
        """, product_id, name, price_kopecks, image_url, "FLOWERS", is_available, SHOP_ID,
             product_created_at, datetime.utcnow())

        print(f"  ✅ Saved product: {name} (ID: {product_id}, {price_kopecks/100:.0f}₸)")

        # Save embedding if available
        if embedding:
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

            await conn.execute("""
                INSERT INTO product_embeddings (product_id, embedding, embedding_type, created_at)
                VALUES ($1, $2::vector, $3, $4)
                ON CONFLICT (product_id, embedding_type)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    created_at = EXCLUDED.created_at
            """, product_id, embedding_str, "image", datetime.utcnow())

            print(f"  ✅ Saved embedding for product {product_id}")

        return True

    except Exception as e:
        print(f"  ❌ Failed to save product {product_id}: {e}")
        return False


async def main():
    print("🚀 Starting Production Products Sync")
    print("=" * 60)

    # Step 1: Fetch products from Production
    products = await fetch_production_products()
    if not products:
        print("❌ No products fetched. Exiting.")
        return

    # Filter products with images
    products_with_images = [p for p in products if p.get("image")]
    print(f"📷 Products with images: {len(products_with_images)}/{len(products)}")

    # Step 2: Connect to PostgreSQL
    print("\n🔌 Connecting to Railway PostgreSQL...")
    conn = await asyncpg.connect(DATABASE_URL)
    print("✅ Connected to PostgreSQL")

    # Step 3: Process each product
    print(f"\n🔄 Processing {len(products_with_images)} products...\n")

    success_count = 0
    embedding_count = 0

    for i, product in enumerate(products_with_images[:50], 1):  # Limit to first 50
        print(f"\n[{i}/{len(products_with_images[:50])}] Processing: {product.get('title', 'Unknown')} (created: {product.get('createdAt', 'unknown')[:10]})")

        # Generate embedding
        image_url = product.get("image")
        product_id = product.get("id")

        embedding = await generate_embedding(image_url, product_id)
        if embedding:
            embedding_count += 1

        # Save to database
        saved = await save_product_to_db(conn, product, embedding)
        if saved:
            success_count += 1

        # Small delay to avoid overwhelming Vertex AI
        await asyncio.sleep(1)

    # Close connection
    await conn.close()

    # Summary
    print("\n" + "=" * 60)
    print("✅ Sync Complete!")
    print(f"📦 Products saved: {success_count}/{len(products_with_images[:50])}")
    print(f"🧠 Embeddings generated: {embedding_count}/{len(products_with_images[:50])}")
    if success_count > 0:
        print(f"📊 Coverage: {(embedding_count/success_count*100):.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
