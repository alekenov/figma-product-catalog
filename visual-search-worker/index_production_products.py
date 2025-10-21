#!/usr/bin/env python3
"""
Index production products from cvety.kz API into Visual Search Worker.

This script fetches all active products from the production Bitrix API
and indexes them into the Cloudflare Visual Search Worker using
Google Vertex AI multimodal embeddings.

Usage:
    python3 index_production_products.py
"""

import requests
import time
import json
from typing import List, Dict, Any

# Configuration
PRODUCTION_API = "https://cvety.kz/api/v2/products"
ACCESS_TOKEN = "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"
VISUAL_SEARCH_WORKER = "https://visual-search.alekenov.workers.dev"
SHOP_ID = 8

# Color formatting
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def fetch_all_products() -> List[Dict[str, Any]]:
    """Fetch all products from production API."""
    print(f"{Colors.CYAN}📡 Fetching products from production API...{Colors.RESET}")

    all_products = []
    offset = 0
    limit = 50

    while True:
        url = f"{PRODUCTION_API}?access_token={ACCESS_TOKEN}&limit={limit}&offset={offset}"
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        data = response.json()
        products = data.get('data', [])

        if not products:
            break

        all_products.extend(products)

        pagination = data.get('pagination', {})
        has_more = pagination.get('hasMore', False)

        print(f"  Fetched {len(products)} products (offset={offset})")

        if not has_more:
            break

        offset += limit

    print(f"{Colors.GREEN}✅ Fetched {len(all_products)} total products{Colors.RESET}\n")
    return all_products


def index_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Index a single product via Visual Search Worker."""
    product_id = product['id']
    title = product['title']
    image_url = product['image']

    # Parse price (remove currency symbol and spaces)
    price_str = product['price'].replace('₸', '').replace(' ', '').strip()
    try:
        price = int(float(price_str) * 100)  # Convert to kopecks
    except ValueError:
        price = 0

    print(f"{Colors.BLUE}🔄 Indexing product {product_id}: {title[:50]}...{Colors.RESET}")

    try:
        response = requests.post(
            f"{VISUAL_SEARCH_WORKER}/reindex-one",
            json={
                "product_id": product_id,
                "shop_id": SHOP_ID
            },
            timeout=60  # Vertex AI can be slow on first requests
        )

        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            duration = result.get('duration_ms', 0)
            print(f"{Colors.GREEN}  ✅ Indexed in {duration}ms{Colors.RESET}")
            return {"success": True, "product_id": product_id, "duration_ms": duration}
        else:
            error = result.get('error', 'Unknown error')
            print(f"{Colors.RED}  ❌ Failed: {error}{Colors.RESET}")
            return {"success": False, "product_id": product_id, "error": error}

    except requests.exceptions.Timeout:
        print(f"{Colors.RED}  ❌ Timeout (>60s){Colors.RESET}")
        return {"success": False, "product_id": product_id, "error": "Timeout"}
    except Exception as e:
        print(f"{Colors.RED}  ❌ Error: {str(e)}{Colors.RESET}")
        return {"success": False, "product_id": product_id, "error": str(e)}


def check_stats() -> Dict[str, Any]:
    """Check Visual Search index statistics."""
    response = requests.get(f"{VISUAL_SEARCH_WORKER}/stats")
    response.raise_for_status()
    return response.json()


def main():
    """Main indexing flow."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Visual Search Production Indexing{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

    # Check initial stats
    print(f"{Colors.YELLOW}📊 Initial stats:{Colors.RESET}")
    try:
        stats = check_stats()
        print(f"  Total indexed: {stats.get('total_indexed', 0)}")
        print(f"  D1 rows: {stats.get('d1_rows', 0)}")
        print(f"  Status: {stats.get('vectorize_status', 'unknown')}\n")
    except Exception as e:
        print(f"{Colors.RED}  ⚠️  Could not fetch stats: {e}{Colors.RESET}\n")

    # Fetch products
    start_time = time.time()
    products = fetch_all_products()

    if not products:
        print(f"{Colors.YELLOW}⚠️  No products found{Colors.RESET}")
        return

    # Index each product
    print(f"{Colors.BOLD}🚀 Starting indexing of {len(products)} products...{Colors.RESET}\n")

    results = []
    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{len(products)}]")
        result = index_product(product)
        results.append(result)

        # Small delay to avoid overwhelming the API
        time.sleep(0.5)

    # Summary
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}📈 Indexing Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

    print(f"{Colors.GREEN}✅ Successful: {successful}{Colors.RESET}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.RESET}")
    print(f"⏱️  Total time: {total_time:.1f}s")
    print(f"⚡ Avg time per product: {total_time/len(results):.1f}s\n")

    # Show failed products
    if failed > 0:
        print(f"{Colors.YELLOW}Failed products:{Colors.RESET}")
        for result in results:
            if not result['success']:
                print(f"  - Product {result['product_id']}: {result.get('error', 'Unknown')}")
        print()

    # Final stats
    print(f"{Colors.YELLOW}📊 Final stats:{Colors.RESET}")
    try:
        stats = check_stats()
        print(f"  Total indexed: {stats.get('total_indexed', 0)}")
        print(f"  D1 rows: {stats.get('d1_rows', 0)}")
        print(f"  Last indexed: {stats.get('last_indexed_at', 'Never')}")
        print(f"  Status: {stats.get('vectorize_status', 'unknown')}\n")
    except Exception as e:
        print(f"{Colors.RED}  ⚠️  Could not fetch stats: {e}{Colors.RESET}\n")

    print(f"{Colors.BOLD}{Colors.GREEN}🎉 Indexing complete!{Colors.RESET}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Indexing interrupted by user{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}\n")
        raise
