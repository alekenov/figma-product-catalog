#!/usr/bin/env python3
"""
Test INTENT extraction with new 3-step Structured Outputs approach.
"""
import asyncio
import httpx
import json
from datetime import datetime

AI_AGENT_URL = "http://localhost:8000"

async def test_intent(message: str, test_name: str):
    """Test INTENT extraction and response."""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"📤 USER: {message}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": message,
                "user_id": f"test_intent_{datetime.now().strftime('%H%M%S')}",
                "channel": "telegram"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Status: {response.status_code}")
            print(f"🤖 RESPONSE:\n{result.get('text', '')}\n")
            if result.get('tracking_id'):
                print(f"📦 Tracking ID: {result['tracking_id']}")
            if result.get('order_number'):
                print(f"🔢 Order Number: {result['order_number']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")

async def main():
    """Run all tests."""
    print(f"\n🧪 Testing INTENT Extraction with Structured Outputs")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test 1: Product listing
    await test_intent(
        "покажи мне букеты роз",
        "Product Listing - should extract list_products intent"
    )

    # Test 2: Price filter
    await test_intent(
        "есть что-то до 15000 тенге?",
        "Price Filter - should extract list_products with max_price"
    )

    # Test 3: Order with missing fields
    await test_intent(
        "Чингис, 77015211545, адрес и дату доставки у получателя уточни",
        "Order with Missing Fields - should detect missing_fields and ask"
    )

    # Test 4: Shop info
    await test_intent(
        "какой у вас график работы?",
        "Shop Info - should extract get_shop_info intent"
    )

    print(f"\n{'='*70}")
    print("✅ All tests completed!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    asyncio.run(main())
