"""
Reindex Visual Search Worker from local database.

This is a fallback script that reads products from the local SQLite database
and sends them to the Visual Search Worker one-by-one using the /index endpoint.

Use this when the Railway backend is down or when batch-index endpoint is not available.

Usage:
    python3 scripts/reindex_visual_search_local.py [--shop-id SHOP_ID]
"""

import sys
import os
import httpx
import asyncio
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product

VISUAL_SEARCH_API = "https://visual-search.alekenov.workers.dev"


def get_database_products(shop_id: int) -> List[Dict[str, Any]]:
    """Fetch all products with images from local database"""

    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figma_catalog.db')
    database_url = f'sqlite:///{db_path}'

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get all enabled products with images for the shop
        products = session.query(Product).filter(
            Product.shop_id == shop_id,
            Product.enabled == True,
            Product.image.isnot(None),
            Product.image != ''
        ).all()

        print(f"Found {len(products)} products with images for shop_id={shop_id}")

        # Convert to dict format expected by Visual Search Worker
        product_list = []
        for p in products:
            product_list.append({
                "product_id": p.id,
                "image_url": p.image,
                "name": p.name,
                "price": p.price,  # Price in kopecks
                "shop_id": p.shop_id
            })

        return product_list

    finally:
        session.close()


async def index_product_single(client: httpx.AsyncClient, product: Dict[str, Any]) -> Dict[str, Any]:
    """Index a single product"""
    try:
        response = await client.post(
            f"{VISUAL_SEARCH_API}/index",
            json=product
        )
        response.raise_for_status()
        result = response.json()
        return {"success": True, "product_id": product["product_id"], **result}
    except Exception as e:
        return {
            "success": False,
            "product_id": product["product_id"],
            "error": str(e)
        }


async def reindex_products_sequential(products: List[Dict[str, Any]]):
    """Send products to Visual Search Worker one-by-one"""

    if not products:
        print("No products to index")
        return

    print(f"\n📦 Reindexing {len(products)} products sequentially...")
    print("   Each product will be indexed separately (slower but more reliable)")

    # Show sample of products being indexed
    print("\nSample products:")
    for p in products[:3]:
        price_tenge = p['price'] / 100
        print(f"  - ID {p['product_id']}: {p['name']} - {price_tenge:.0f} ₸")

    async with httpx.AsyncClient(timeout=60.0) as client:
        indexed = 0
        failed = 0
        errors = []

        for i, product in enumerate(products, 1):
            print(f"\n[{i}/{len(products)}] Indexing product {product['product_id']}: {product['name'][:40]}...")

            result = await index_product_single(client, product)

            if result["success"]:
                indexed += 1
                print(f"  ✅ Success")
            else:
                failed += 1
                errors.append({
                    "product_id": product["product_id"],
                    "error": result["error"]
                })
                print(f"  ❌ Failed: {result['error']}")

            # Small delay to avoid rate limiting
            if i < len(products):
                await asyncio.sleep(1)

        print(f"\n{'='*60}")
        print(f"✅ Reindexing complete!")
        print(f"   Total products: {len(products)}")
        print(f"   Indexed successfully: {indexed}")
        print(f"   Failed: {failed}")

        if errors:
            print(f"\n⚠️  Errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   - Product {error['product_id']}: {error['error']}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Reindex Visual Search from local database')
    parser.add_argument('--shop-id', type=int, default=8, help='Shop ID to reindex (default: 8)')
    args = parser.parse_args()

    print("=" * 60)
    print("REINDEX VISUAL SEARCH WORKER (LOCAL DATABASE)")
    print("=" * 60)
    print(f"Shop ID: {args.shop_id}")
    print(f"Target: {VISUAL_SEARCH_API}")
    print(f"Source: Local SQLite database")
    print()

    # Fetch products from local database
    products = get_database_products(args.shop_id)

    if not products:
        print("No products found to index!")
        return

    # Reindex one-by-one
    asyncio.run(reindex_products_sequential(products))

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
