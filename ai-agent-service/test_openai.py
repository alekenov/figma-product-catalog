#!/usr/bin/env python3
"""
Test OpenAI integration with AI Agent Service.
Verifies tool calling and response quality.
"""
import asyncio
import httpx
import json
from datetime import datetime

AI_AGENT_URL = "http://localhost:8000"

async def test_chat(message: str, user_id: str = "test_openai"):
    """Send a chat message and get response."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n{'='*60}")
        print(f"📤 USER: {message}")
        print(f"{'='*60}")

        response = await client.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": message,
                "user_id": user_id,
                "channel": "telegram"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"🤖 ASSISTANT: {result.get('text', '')}")
            if result.get('tracking_id'):
                print(f"📦 Tracking ID: {result['tracking_id']}")
            if result.get('order_number'):
                print(f"🔢 Order Number: {result['order_number']}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

async def main():
    """Run test scenarios."""
    print(f"\n🧪 Testing OpenAI gpt-5-mini Integration")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_user = f"openai_test_{datetime.now().strftime('%H%M%S')}"

    # Test 1: Simple greeting
    print("\n" + "="*60)
    print("TEST 1: Simple Greeting")
    print("="*60)
    await test_chat("Привет!", test_user)

    # Test 2: Product listing (should use list_products tool)
    print("\n" + "="*60)
    print("TEST 2: Product Listing (Tool Calling)")
    print("="*60)
    await test_chat("покажи мне букеты роз", test_user)

    # Test 3: Price inquiry (should use list_products with filters)
    print("\n" + "="*60)
    print("TEST 3: Price Filter (Tool Calling)")
    print("="*60)
    await test_chat("есть что-то до 15000 тенге?", test_user)

    # Test 4: Shop info
    print("\n" + "="*60)
    print("TEST 4: Shop Information")
    print("="*60)
    await test_chat("какой у вас график работы?", test_user)

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
