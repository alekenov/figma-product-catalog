"""
Reindex Visual Search Worker with current product prices from database.

This script triggers the Visual Search Worker to re-fetch all products from
the backend API and regenerate their embeddings. This ensures that visual
search results show current prices, not outdated cached values.

The Visual Search Worker will:
1. Fetch products from PostgreSQL backend API
2. Download images from Cloudflare R2
3. Generate CLIP embeddings using Google Vertex AI
4. Store vectors in Cloudflare Vectorize
5. Update metadata in D1 database

Usage:
    python3 scripts/reindex_visual_search.py [--shop-id SHOP_ID]
"""

import sys
import os
import httpx
import asyncio

VISUAL_SEARCH_API = "https://visual-search.alekenov.workers.dev"


async def reindex_shop(shop_id: int):
    """Trigger Visual Search Worker to reindex all products for a shop"""

    print(f"\n📦 Triggering Visual Search Worker to reindex shop_id={shop_id}...")
    print(f"   Worker will fetch products from backend API")
    print(f"   This may take 30-60 seconds for 10 products...")

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            # Send batch index request
            # The Worker will fetch products itself from the backend API
            print(f"\n🚀 Sending batch index request to {VISUAL_SEARCH_API}/batch-index...")
            response = await client.post(
                f"{VISUAL_SEARCH_API}/batch-index",
                json={
                    "source": "postgresql",  # Fetch from PostgreSQL backend
                    "shop_id": shop_id,
                    "limit": 100  # Process up to 100 products
                }
            )

            response.raise_for_status()
            result = response.json()

            print(f"\n✅ Reindexing complete!")
            print(f"   Total products: {result.get('total', 0)}")
            print(f"   Indexed successfully: {result.get('indexed', 0)} products")
            print(f"   Failed: {result.get('failed', 0)} products")
            print(f"   Duration: {result.get('duration_ms', 0)}ms")

            if result.get('errors') and len(result['errors']) > 0:
                print(f"\n⚠️  Errors occurred:")
                for error in result['errors'][:5]:  # Show first 5 errors
                    print(f"   - Product {error.get('product_id')}: {error.get('error')}")

        except httpx.HTTPError as e:
            print(f"\n❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response status: {e.response.status_code}")
                try:
                    error_body = e.response.json()
                    print(f"   Error details: {error_body}")
                except:
                    print(f"   Response text: {e.response.text[:500]}")
            raise
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Reindex Visual Search with current prices')
    parser.add_argument('--shop-id', type=int, default=8, help='Shop ID to reindex (default: 8)')
    args = parser.parse_args()

    print("=" * 60)
    print("REINDEX VISUAL SEARCH WORKER")
    print("=" * 60)
    print(f"Shop ID: {args.shop_id}")
    print(f"Target: {VISUAL_SEARCH_API}")
    print()

    # Trigger reindexing
    asyncio.run(reindex_shop(args.shop_id))

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
