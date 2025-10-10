#!/usr/bin/env python3
"""Quick test for VIP scenario 04 with improved prompt."""

import asyncio
import httpx
import time
from datetime import datetime

AI_AGENT_URL = "http://localhost:8002"
SHOP_ID = 8

async def test_vip_scenario():
    """Test VIP demanding customer scenario."""

    session_id = f"test_vip_{int(time.time())}"
    user_id = "vip_test_user"

    # VIP message from scenario 04
    vip_message = "Нужен шикарный букет белых роз на важную встречу. Бюджет не ограничен, но должно быть идеально. Доставка строго завтра в 15:00."

    print("=" * 70)
    print("🎯 TESTING VIP SCENARIO WITH IMPROVED PROMPT")
    print("=" * 70)
    print(f"📝 VIP Message: {vip_message}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print()

    start_time = time.time()
    turns = 0

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            # Turn 1: VIP request
            turns += 1
            print(f"🔄 Turn {turns}: Sending VIP request...")
            turn_start = time.time()

            response = await client.post(
                f"{AI_AGENT_URL}/chat",
                json={
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": vip_message,
                    "shop_id": SHOP_ID
                }
            )
            response.raise_for_status()
            data = response.json()

            turn_time = time.time() - turn_start
            print(f"⏱️  Turn {turns} time: {turn_time:.2f}s")

            # Extract response
            ai_response = data.get('text', '')
            print(f"💬 AI Response ({len(ai_response)} chars):")
            print(ai_response[:500])  # First 500 chars
            if len(ai_response) > 500:
                print(f"... (truncated, total {len(ai_response)} chars)")
            print()

            # Check for conversation_status tag
            if '<conversation_status>complete</conversation_status>' in ai_response:
                print("✅ AI marked conversation as COMPLETE")
            elif '<conversation_status>continue</conversation_status>' in ai_response:
                print("⚠️  AI marked conversation as CONTINUE")
            else:
                print("❓ No conversation_status tag found")

            # Check if products were shown
            if 'роз' in ai_response.lower() and '₸' in ai_response:
                print("✅ Products shown with prices")
            else:
                print("❌ No products shown")

            print()

            # Check if we should continue (AI wants more info)
            if 'телефон' in ai_response.lower() or 'адрес' in ai_response.lower():
                print("🔄 AI requesting contact info, sending follow-up...")

                # Turn 2: Provide contact info
                turns += 1
                turn_start = time.time()
                follow_up = "Выбираю второй букет. Телефон 77012345678, адрес ул. Абая 150"

                response = await client.post(
                    f"{AI_AGENT_URL}/chat",
                    json={
                        "session_id": session_id,
                        "user_id": user_id,
                        "message": follow_up,
                        "shop_id": SHOP_ID
                    }
                )
                response.raise_for_status()
                data = response.json()

                turn_time = time.time() - turn_start
                print(f"⏱️  Turn {turns} time: {turn_time:.2f}s")

                ai_response2 = data.get('text', '')
                print(f"💬 AI Response ({len(ai_response2)} chars):")
                print(ai_response2[:300])
                if len(ai_response2) > 300:
                    print(f"... (truncated)")
                print()

                # Check for order creation
                if 'заказ' in ai_response2.lower() and '#' in ai_response2:
                    print("✅ Order created successfully")
                else:
                    print("❌ No order created")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            total_time = time.time() - start_time
            print(f"⏱️  FAILED after {total_time:.2f}s and {turns} turn(s)")
            return False

    total_time = time.time() - start_time

    print()
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"🔄 Total turns: {turns}")

    # Success criteria
    success = True
    if total_time > 150:
        print(f"❌ TIMEOUT: {total_time:.2f}s > 150s limit")
        success = False
    else:
        print(f"✅ Within timeout: {total_time:.2f}s < 150s")

    if turns <= 2:
        print(f"✅ Efficient: {turns} turn(s)")
    else:
        print(f"⚠️  Many turns: {turns}")

    print()
    print("🎯 IMPROVEMENT vs OLD VERSION:")
    print(f"   Old v2: 179.4s (2 turns) - FAILED")
    print(f"   New v2: {total_time:.2f}s ({turns} turns) - {'✅ PASS' if success else '❌ FAIL'}")

    improvement = ((179.4 - total_time) / 179.4) * 100
    if success:
        print(f"   🚀 Speed improvement: {improvement:.1f}%")

    return success

if __name__ == "__main__":
    success = asyncio.run(test_vip_scenario())
    exit(0 if success else 1)
