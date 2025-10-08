#!/usr/bin/env python3
"""Quick test for product listing with corrected product types."""
import asyncio
import httpx

async def test_product_listing():
    """Test product listing with flowers type."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🧪 Testing product listing with corrected product_type...")

        response = await client.post(
            "http://localhost:8000/chat",
            json={
                "message": "покажи мне цветы до 10000 тенге",
                "user_id": "test_flowers_fix",
                "channel": "telegram"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success! Status: {response.status_code}")
            print(f"🤖 Response:\n{result['text']}\n")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}\n")

if __name__ == "__main__":
    asyncio.run(test_product_listing())
