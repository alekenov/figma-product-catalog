#!/usr/bin/env python3
"""
Batch script to generate CLIP embeddings for all products without embeddings

Run this ONCE after deploying visual search feature to generate embeddings for
all existing products in production database.

Usage:
    python scripts/generate_embeddings_batch.py [--shop-id 8] [--dry-run]

Environment variables:
    DATABASE_URL: PostgreSQL connection string (required for production)
    HUGGING_FACE_TOKEN: Hugging Face API token (required)
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Environment detection
DB_TYPE = None


def detect_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    global DB_TYPE

    if os.getenv("DATABASE_URL"):
        DB_TYPE = "postgresql"
    else:
        DB_TYPE = "sqlite"

    print(f"🗄️  Database type: {DB_TYPE}")
    return DB_TYPE


def get_db_session():
    """Get SQLModel session"""
    if DB_TYPE == "postgresql":
        from config_render import settings
    else:
        from config_sqlite import settings

    from database import SessionLocal
    return SessionLocal()


def main():
    parser = argparse.ArgumentParser(
        description="Generate CLIP embeddings for all products without embeddings"
    )
    parser.add_argument(
        "--shop-id",
        type=int,
        default=8,
        help="Shop ID to generate embeddings for (default: 8)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of products to process (useful for testing)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🖼️  Batch Embedding Generation for Products")
    print("=" * 60)

    # Detect database
    detect_database_type()

    # Check environment variables
    if not os.getenv("HUGGING_FACE_TOKEN"):
        print("❌ Error: HUGGING_FACE_TOKEN environment variable not set")
        print("   Get token from: https://huggingface.co/settings/tokens")
        sys.exit(1)

    from models.products import Product
    from services.embedding_service import (
        generate_clip_embedding,
        download_image_from_url,
        db_format_to_embedding_vector,
        EmbeddingError
    )
    from sqlmodel import select

    session = get_db_session()

    try:
        # Get products without embeddings
        print(f"\n📊 Fetching products without embeddings (shop_id={args.shop_id})...")

        statement = select(Product).where(
            (Product.shop_id == args.shop_id) &
            (Product.image.isnot(None)) &
            (Product.image_embedding.is_(None)) &
            (Product.enabled == True)
        )

        products = session.exec(statement).all()

        if args.limit:
            products = products[:args.limit]

        print(f"✅ Found {len(products)} products to process")

        if not products:
            print("✨ No products to process - all done!")
            return

        if args.dry_run:
            print("\n🔍 DRY RUN MODE - showing what would be done:")
            for i, product in enumerate(products[:5], 1):
                print(f"  {i}. Product #{product.id}: {product.name}")
            if len(products) > 5:
                print(f"  ... and {len(products) - 5} more")
            print(f"\nWould process: {len(products)} products")
            return

        # Process products
        print(f"\n🚀 Starting embedding generation for {len(products)} products...")
        print(f"⏱️  Estimated time: ~{len(products) * 2} seconds (with rate limiting)")
        print()

        processed = 0
        failed = 0
        start_time = time.time()

        for i, product in enumerate(products, 1):
            try:
                # Download image
                print(f"[{i}/{len(products)}] Processing: {product.name[:40]:<40}", end="")
                sys.stdout.flush()

                image_bytes = download_image_from_url(product.image)
                if not image_bytes:
                    print(" ❌ Failed to download")
                    failed += 1
                    continue

                # Generate embedding
                embedding = generate_clip_embedding(image_bytes)
                if not embedding:
                    print(" ❌ Failed to generate embedding")
                    failed += 1
                    continue

                # Save to database
                product.image_embedding = embedding
                product.embedding_generated_at = datetime.utcnow()
                session.add(product)
                session.commit()

                processed += 1
                print(" ✅")

                # Rate limiting - sleep between requests
                time.sleep(0.1)

            except EmbeddingError as e:
                print(f" ❌ Error: {str(e)[:50]}")
                failed += 1
                continue

            except Exception as e:
                print(f" ❌ Unexpected error: {str(e)[:50]}")
                failed += 1
                session.rollback()
                continue

        elapsed = time.time() - start_time

        # Summary
        print("\n" + "=" * 60)
        print("📈 RESULTS:")
        print("=" * 60)
        print(f"✅ Successfully processed: {processed}/{len(products)}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Total time: {elapsed:.1f}s")
        print(f"⚡ Speed: {len(products)/elapsed:.1f} products/sec")

        if processed > 0:
            print(f"\n✨ {processed} products now have embeddings!")
            print("   You can test visual search now at:")
            print("   POST /api/v1/search/visual")
        else:
            print("\n⚠️  No products were successfully processed")

    except Exception as e:
        print(f"\n❌ Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        session.close()


if __name__ == "__main__":
    main()
