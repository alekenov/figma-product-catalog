#!/usr/bin/env python3
"""
Simple production test for pickup functionality.
Tests AI Agent Service deployed on Railway with real shop_id=8.
"""
import httpx
import asyncio
import uuid
from datetime import datetime

# Production URLs
AI_AGENT_URL = "https://ai-agent-service-production-c331.up.railway.app"
SHOP_ID = 8

async def test_pickup_flow():
    """Test complete pickup ordering flow on production."""

    # Unique user ID for this test
    test_user_id = f"test_pickup_{uuid.uuid4().hex[:8]}"

    print("🏪 Testing Pickup Functionality on PRODUCTION")
    print("=" * 60)
    print(f"AI Agent: {AI_AGENT_URL}")
    print(f"Shop ID: {SHOP_ID}")
    print(f"Test User: {test_user_id}")
    print()

    # Test conversation flow
    messages = [
        "Привет! Хочу заказать букет с самовывозом.",
        "Розы",
        "Да, подойдет. Заберу сегодня к 18:00. Мой телефон 77011111111, меня зовут Тестовый Клиент"
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, message in enumerate(messages, 1):
            print(f"\n{'='*60}")
            print(f"Turn {i}/{len(messages)}")
            print(f"{'='*60}")
            print(f"👤 USER: {message}")
            print()

            try:
                # Call AI Agent
                response = await client.post(
                    f"{AI_AGENT_URL}/chat",
                    json={
                        "message": message,
                        "user_id": test_user_id,
                        "channel": "telegram",
                        "context": {
                            "username": "test_user",
                            "first_name": "Тестовый"
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()

                # Print response
                print(f"🤖 ASSISTANT:")
                print(result.get("text", ""))
                print()

                # Check for products
                if result.get("show_products"):
                    try:
                        products_resp = await client.get(
                            f"{AI_AGENT_URL}/products/{test_user_id}",
                            params={"channel": "telegram"}
                        )
                        if products_resp.status_code == 200:
                            products_data = products_resp.json()
                            products = products_data.get("products", [])
                            print(f"📦 Products shown: {len(products)}")
                            for product in products[:3]:
                                print(f"  - {product.get('name')} - {product.get('price', 0) // 100:,} ₸")
                            print()
                    except Exception as e:
                        print(f"⚠️ Could not fetch products: {e}")
                        print()

                # Parse for order creation indicators
                text = result.get("text", "").lower()
                if "заказ" in text and "номер" in text:
                    print("✅ ORDER LIKELY CREATED!")
                    print()
                if "самовывоз" in text or "pickup" in text or "забрать" in text:
                    print("✅ PICKUP RECOGNIZED!")
                    print()
                if "адрес" in text and "магазин" in text:
                    print("✅ PICKUP ADDRESS PROVIDED!")
                    print()

                # Small delay between messages
                await asyncio.sleep(2)

            except httpx.HTTPStatusError as e:
                print(f"❌ HTTP Error {e.response.status_code}")
                print(f"Response: {e.response.text}")
                return False
            except Exception as e:
                print(f"❌ Error: {e}")
                return False

    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_pickup_flow())
    exit(0 if success else 1)
