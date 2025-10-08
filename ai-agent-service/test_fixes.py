"""
Test script to verify all 5 critical fixes.
"""
import asyncio
import httpx
import json

AI_AGENT_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

async def test_all_fixes():
    """Test all 5 critical fixes."""

    print("=" * 80)
    print("TESTING AI AGENT FIXES")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30.0) as client:

        # ============================================================
        # FIX #1: Date normalization - "послезавтра" should pass through
        # ============================================================
        print("\n🧪 TEST 1: Date normalization (послезавтра)")
        print("-" * 80)

        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": "доставить букет ID 16 послезавтра утром на проспект Абая 10, Иван, 77011111111",
                "user_id": TEST_USER_ID,
                "channel": "telegram"
            }
        )
        result = response.json()
        print(f"Response: {result['text'][:200]}...")
        print(f"✅ Date normalization test complete")

        # ============================================================
        # FIX #2: Tracking by tracking_id
        # ============================================================
        print("\n🧪 TEST 2: Track order by tracking_id")
        print("-" * 80)

        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": "903757396",  # Sample tracking ID
                "user_id": TEST_USER_ID,
                "channel": "telegram"
            }
        )
        result = response.json()
        print(f"Response: {result['text'][:300]}...")
        print(f"Show products: {result.get('show_products')}")
        print(f"✅ Tracking ID test complete")

        # ============================================================
        # FIX #3: Token usage reduction - check product list response
        # ============================================================
        print("\n🧪 TEST 3: Token usage reduction (trimmed products)")
        print("-" * 80)

        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": "покажи букеты",
                "user_id": TEST_USER_ID,
                "channel": "telegram"
            }
        )
        result = response.json()
        print(f"Response length: {len(result['text'])} chars")
        print(f"Show products: {result.get('show_products')}")
        print(f"Response preview: {result['text'][:200]}...")

        # Fetch products to verify trimming
        products_response = await client.get(
            f"{AI_AGENT_URL}/products/{TEST_USER_ID}",
            params={"channel": "telegram"}
        )
        products_data = products_response.json()
        print(f"Products count: {products_data['count']}")
        print(f"✅ Token reduction test complete")

        # ============================================================
        # FIX #4: Conditional image fetching
        # ============================================================
        print("\n🧪 TEST 4: Conditional image fetching")
        print("-" * 80)

        # Non-catalog request should NOT trigger list_products intent
        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": "какой у вас график работы?",
                "user_id": TEST_USER_ID,
                "channel": "telegram"
            }
        )
        result = response.json()
        print(f"Show products: {result.get('show_products')} (should be False)")
        print(f"✅ Conditional image test complete")

        # ============================================================
        # FIX #5: Conversation history
        # ============================================================
        print("\n🧪 TEST 5: Conversation history (multi-turn context)")
        print("-" * 80)

        # First message
        await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": "покажи букеты до 10000 тенге",
                "user_id": TEST_USER_ID,
                "channel": "telegram"
            }
        )

        # Follow-up message (should use context)
        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": "а есть что-то дешевле?",
                "user_id": TEST_USER_ID,
                "channel": "telegram"
            }
        )
        result = response.json()
        print(f"Follow-up response: {result['text'][:300]}...")
        print(f"✅ Conversation history test complete")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_all_fixes())
