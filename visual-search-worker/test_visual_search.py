#!/usr/bin/env python3
"""
Test visual search functionality with indexed products.
"""

import requests
import json

VISUAL_SEARCH_WORKER = "https://visual-search.alekenov.workers.dev"

# Test with one of the indexed images
TEST_IMAGE_URL = "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png"

print("🔍 Testing Visual Search\n")
print(f"Test image: {TEST_IMAGE_URL}\n")

try:
    print("Searching for similar bouquets...")
    response = requests.post(
        f"{VISUAL_SEARCH_WORKER}/search",
        json={
            "image_url": TEST_IMAGE_URL,
            "topK": 5
        },
        timeout=30
    )

    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ Search successful!\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        exact_count = len(result.get('exact', []))
        similar_count = len(result.get('similar', []))

        print(f"\n📊 Results:")
        print(f"  Exact matches: {exact_count}")
        print(f"  Similar matches: {similar_count}")
        print(f"  Search time: {result.get('search_time_ms', 'N/A')}ms")
        print(f"  Total indexed: {result.get('total_indexed', 'N/A')}")

    else:
        print(f"\n❌ Search failed: {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("\n❌ Request timed out (>30s)")
except Exception as e:
    print(f"\n❌ Error: {e}")
