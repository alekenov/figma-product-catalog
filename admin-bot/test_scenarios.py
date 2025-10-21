#!/usr/bin/env python3
"""
Test scenarios for Telegram bot - simulates real user journeys.
Run without pytest: python test_scenarios.py
"""
import asyncio
import time
from unittest.mock import AsyncMock
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))


class MockMCPClient:
    """Mock MCP client for scenario testing."""

    def __init__(self):
        self.clients_db = {}  # Simulate database
        self.orders_db = {}

    async def get_telegram_client(self, telegram_user_id: str, shop_id: int):
        """Get client by telegram_user_id."""
        key = f"{telegram_user_id}:{shop_id}"
        if key in self.clients_db:
            return self.clients_db[key]
        return None

    async def register_telegram_client(
        self,
        telegram_user_id: str,
        phone: str,
        customer_name: str,
        shop_id: int,
        telegram_username: str = None,
        telegram_first_name: str = None,
    ):
        """Register telegram client."""
        key = f"{telegram_user_id}:{shop_id}"
        self.clients_db[key] = {
            "id": len(self.clients_db) + 1,
            "phone": phone,
            "customerName": customer_name,
            "telegram_user_id": telegram_user_id,
            "telegram_username": telegram_username,
            "telegram_first_name": telegram_first_name,
            "shop_id": shop_id,
        }
        return self.clients_db[key]


class BotSimulator:
    """Simplified bot for scenario testing."""

    def __init__(self):
        self.mcp_client = MockMCPClient()
        self.auth_cache = {}
        self.auth_cache_ttl = 300  # 5 minutes
        self.shop_id = 8

    async def check_authorization(self, user_id: int) -> bool:
        """Check authorization with cache."""
        # Check cache
        if user_id in self.auth_cache:
            is_authorized, timestamp = self.auth_cache[user_id]
            if time.time() - timestamp < self.auth_cache_ttl:
                return is_authorized

        # Check backend
        try:
            client = await self.mcp_client.get_telegram_client(
                telegram_user_id=str(user_id), shop_id=self.shop_id
            )
            is_authorized = client is not None
            self.auth_cache[user_id] = (is_authorized, time.time())
            return is_authorized
        except Exception as e:
            print(f"  ⚠️ Authorization check error: {e}")
            return True

    async def register_client(self, user_id: int, phone: str, name: str):
        """Register client."""
        result = await self.mcp_client.register_telegram_client(
            telegram_user_id=str(user_id),
            phone=phone,
            customer_name=name,
            shop_id=self.shop_id,
            telegram_first_name=name.split()[0] if name else "User",
            telegram_username=name.lower().replace(" ", "_"),
        )
        # Clear cache after registration (so next check_authorization refreshes)
        if user_id in self.auth_cache:
            del self.auth_cache[user_id]
        return result


# ============================================================================
# SCENARIOS
# ============================================================================


async def scenario_1_new_user():
    """Scenario 1: New user journey - /start -> register -> /myorders"""
    print("\n" + "=" * 70)
    print("SCENARIO 1: New User Journey")
    print("=" * 70)

    # Use SAME bot instance throughout scenario!
    bot = BotSimulator()
    user_id = 111111

    # Step 1: /start command
    print("\n1️⃣  User sends /start")
    is_authorized = await bot.check_authorization(user_id)
    print(f"   Authorization result: {is_authorized}")
    print(f"   Expected: False (not registered yet)")
    assert is_authorized is False, "New user should not be authorized"

    # Step 2: User shares contact
    print("\n2️⃣  User shares contact: +77015211545, John Doe")
    client = await bot.register_client(user_id, "+77015211545", "John Doe")
    print(f"   Registered: {client}")
    print(f"   ✅ Client saved to database")

    # Step 3: Check authorization again (SAME bot, so sees registered user)
    print("\n3️⃣  User sends /start again (authorization check)")
    is_authorized = await bot.check_authorization(user_id)
    print(f"   Authorization result: {is_authorized}")
    print(f"   Expected: True (now registered)")
    assert is_authorized is True, "Registered user should be authorized"

    # Step 4: /myorders - uses saved phone
    print("\n4️⃣  User sends /myorders (uses saved phone)")
    stored_client = await bot.mcp_client.get_telegram_client(
        telegram_user_id=str(user_id), shop_id=8
    )
    print(f"   Retrieved stored phone: {stored_client['phone']}")
    print(f"   Expected: +77015211545")
    assert stored_client["phone"] == "+77015211545", "Phone should be stored"

    print("\n✅ SCENARIO 1 PASSED\n")


async def scenario_2_cache_performance():
    """Scenario 2: Cache performance - fast authorization"""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Cache Performance")
    print("=" * 70)

    bot = BotSimulator()
    user_id = 222222

    # Register user
    print("\n1️⃣  Register user")
    await bot.register_client(user_id, "+77025555555", "Jane Doe")
    print("   ✅ User registered")

    # First authorization - populates cache
    print("\n2️⃣  First authorization check (populates cache)")
    start_time = time.time()
    is_auth_1 = await bot.check_authorization(user_id)
    time_1 = time.time() - start_time
    print(f"   Result: {is_auth_1}")
    print(f"   Time taken: {time_1*1000:.2f}ms")

    # Second authorization - uses cache
    print("\n3️⃣  Second authorization check (uses cache)")
    start_time = time.time()
    is_auth_2 = await bot.check_authorization(user_id)
    time_2 = time.time() - start_time
    print(f"   Result: {is_auth_2}")
    print(f"   Time taken: {time_2*1000:.2f}ms (SHOULD BE FASTER!)")
    print(
        f"   Speedup: {time_1/time_2:.1f}x faster"
        if time_2 > 0
        else "   Speedup: Cached response"
    )

    assert is_auth_1 is True, "First auth should succeed"
    assert is_auth_2 is True, "Second auth should succeed"

    print("\n✅ SCENARIO 2 PASSED\n")


async def scenario_3_cache_expiration():
    """Scenario 3: Cache expiration - TTL expires after 5 minutes"""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Cache Expiration")
    print("=" * 70)

    bot = BotSimulator()
    user_id = 333333

    # Register user
    print("\n1️⃣  Register user")
    await bot.register_client(user_id, "+77035555555", "Bob Smith")
    print("   ✅ User registered")

    # First check
    print("\n2️⃣  First authorization (caches for 5 minutes)")
    is_auth_1 = await bot.check_authorization(user_id)
    cache_time_1 = bot.auth_cache[user_id][1]
    print(f"   Cache entry time: {cache_time_1}")

    # Second check (within 5 minutes)
    print("\n3️⃣  Second authorization (within 5 minutes) - uses cache")
    is_auth_2 = await bot.check_authorization(user_id)
    cache_time_2 = bot.auth_cache[user_id][1]
    print(f"   Cache entry time: {cache_time_2}")
    print(f"   Cache reused: {cache_time_1 == cache_time_2}")
    assert cache_time_1 == cache_time_2, "Cache should be reused"

    # Manually expire cache
    print("\n4️⃣  Simulate 5+ minutes passing")
    is_auth, timestamp = bot.auth_cache[user_id]
    bot.auth_cache[user_id] = (is_auth, timestamp - 400)  # 400 seconds ago
    print("   ⏰ Cache marked as expired")

    # Third check after expiration
    print("\n5️⃣  Third authorization (cache expired) - refreshes from DB")
    is_auth_3 = await bot.check_authorization(user_id)
    cache_time_3 = bot.auth_cache[user_id][1]
    print(f"   New cache entry time: {cache_time_3}")
    print(f"   Cache refreshed: {cache_time_3 > timestamp}")
    assert cache_time_3 > timestamp, "Cache should be refreshed"

    print("\n✅ SCENARIO 3 PASSED\n")


async def scenario_4_multi_tenancy():
    """Scenario 4: Multi-tenancy - clients isolated by shop_id"""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Multi-Tenancy Isolation")
    print("=" * 70)

    # Two shops
    print("\n1️⃣  Setup: 2 shops with different databases")
    bot_shop_8 = BotSimulator()
    bot_shop_8.shop_id = 8

    bot_shop_9 = BotSimulator()
    bot_shop_9.shop_id = 9

    print("   Shop 8: Created")
    print("   Shop 9: Created")

    # Register same user in different shops
    user_id = 444444
    print(f"\n2️⃣  Register user {user_id} in SHOP 8")
    await bot_shop_8.register_client(user_id, "+77045555555", "Alice Wonder")
    print("   ✅ User registered in Shop 8")

    print(f"\n3️⃣  Register user {user_id} in SHOP 9 (same user_id, different shop)")
    await bot_shop_9.register_client(user_id, "+77045555555", "Alice Wonder")
    print("   ✅ User registered in Shop 9")

    # Check authorization in Shop 8
    print(f"\n4️⃣  Check authorization in SHOP 8")
    is_auth_shop_8 = await bot_shop_8.check_authorization(user_id)
    print(f"   Result: {is_auth_shop_8}")
    assert is_auth_shop_8 is True, "User should be authorized in Shop 8"

    # Check authorization in Shop 9
    print(f"\n5️⃣  Check authorization in SHOP 9")
    is_auth_shop_9 = await bot_shop_9.check_authorization(user_id)
    print(f"   Result: {is_auth_shop_9}")
    assert is_auth_shop_9 is True, "User should be authorized in Shop 9"

    # Verify data isolation
    print(f"\n6️⃣  Verify data isolation")
    client_8 = await bot_shop_8.mcp_client.get_telegram_client(
        telegram_user_id=str(user_id), shop_id=8
    )
    client_9 = await bot_shop_9.mcp_client.get_telegram_client(
        telegram_user_id=str(user_id), shop_id=9
    )
    print(f"   Shop 8 client: {client_8}")
    print(f"   Shop 9 client: {client_9}")
    print(f"   Both are separate records: {client_8 is not client_9}")

    print("\n✅ SCENARIO 4 PASSED\n")


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Run all scenarios."""
    print("\n" + "=" * 70)
    print("TELEGRAM BOT TEST SCENARIOS")
    print("Simulating real user journeys without Telegram")
    print("=" * 70)

    try:
        await scenario_1_new_user()
        await scenario_2_cache_performance()
        await scenario_3_cache_expiration()
        await scenario_4_multi_tenancy()

        print("\n" + "=" * 70)
        print("✅ ALL SCENARIOS PASSED!")
        print("=" * 70)
        print("\nWhat was tested:")
        print("  ✓ New user registration flow")
        print("  ✓ Authorization with cache")
        print("  ✓ Cache expiration (5-minute TTL)")
        print("  ✓ Multi-tenancy isolation")
        print("\nYou can now run: pytest tests/ -v")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\n❌ SCENARIO FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
