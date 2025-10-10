"""
End-to-end integration tests for conversational AI flows.

Tests critical user journeys through AI Agent → MCP Server → Backend.
Run against live services (local or docker-compose).

Usage:
    python -m pytest test_conversation_flows.py -v
    python -m pytest test_conversation_flows.py::TestConversationFlows::test_list_products_flow -v
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from config import config
from test_utils import (
    ServiceHealthChecker,
    AIAgentClient,
    MCPServerClient,
    BackendAPIClient,
    assert_tracking_id_valid,
    assert_order_structure,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def check_services_health():
    """Ensure all services are healthy before running tests."""
    is_healthy = await ServiceHealthChecker.check_all_services()
    if not is_healthy:
        pytest.exit("Services are not healthy. Cannot run integration tests.")


@pytest.fixture
def ai_client():
    """AI Agent client instance."""
    return AIAgentClient()


@pytest.fixture
def mcp_client():
    """MCP Server client instance."""
    return MCPServerClient()


@pytest.fixture
def backend_client():
    """Backend API client instance."""
    return BackendAPIClient()


@pytest.fixture
def test_user_id():
    """Generate unique test user ID for each test."""
    import uuid
    user_id = f"test_{uuid.uuid4().hex[:8]}"
    return user_id
    # Note: cleanup removed to fix JSON serialization issue
    # Tests should clean up their own data if needed


class TestConversationFlows:
    """End-to-end conversation flow tests."""

    @pytest.mark.asyncio
    async def test_list_products_flow(
        self,
        ai_client: AIAgentClient,
        backend_client: BackendAPIClient,
        test_user_id: str
    ):
        """
        Test Flow 1: Customer asks for product recommendations.

        Steps:
        1. Customer: "Покажи мне цветы в районе 10000-15000 тенге"
        2. AI Agent calls list_products with price filters
        3. AI responds with product names and prices
        4. Verify products are within requested price range
        """
        print("\n🧪 Test 1: List Products Flow")

        # Step 1: Customer asks for products in price range
        message = "Покажи мне цветы в районе 10000-15000 тенге"
        print(f"   Customer: {message}")

        response = await ai_client.chat(
            message=message,
            user_id=test_user_id,
            request_id=f"test_list_{test_user_id}"
        )

        # Step 2: Verify AI responded
        assert "text" in response, "Response should contain text"
        response_text = response["text"]
        print(f"   AI: {response_text[:200]}...")

        # Step 3: Verify show_products flag is set
        assert response.get("show_products") == True, \
            "AI should indicate products were listed (show_products=True)"

        # Step 4: Get actual products from backend to verify price range
        products = await backend_client.get_products(
            shop_id=config.TEST_SHOP_ID,
            limit=20
        )

        # Verify products exist
        assert len(products) > 0, "Backend should return products"

        # Check that some products are in the requested range
        products_in_range = [
            p for p in products
            if 10000 <= p.get("price", 0) <= 15000
        ]
        assert len(products_in_range) > 0, \
            f"Should have products in 10000-15000 range. Found {len(products)} total products."

        print(f"   ✅ Found {len(products_in_range)} products in price range")

    @pytest.mark.asyncio
    async def test_create_order_flow(
        self,
        ai_client: AIAgentClient,
        test_user_id: str
    ):
        """
        Test Flow 2: Customer creates a flower delivery order.

        Steps:
        1. Customer provides order details in natural language
        2. AI Agent calls create_order with parsed data
        3. AI responds with tracking_id
        4. Verify tracking_id format
        """
        print("\n🧪 Test 2: Create Order Flow")

        # Step 1: Customer places order
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        message = f"""Хочу заказать букет роз.
        Имя: {config.TEST_CUSTOMER_NAME}
        Телефон: {config.TEST_CUSTOMER_PHONE}
        Адрес: {config.TEST_DELIVERY_ADDRESS}
        Доставка: завтра утром
        """
        print(f"   Customer: {message[:100]}...")

        response = await ai_client.chat(
            message=message,
            user_id=test_user_id,
            request_id=f"test_create_{test_user_id}"
        )

        # Step 2: Verify AI responded with order confirmation
        assert "text" in response, "Response should contain text"
        response_text = response["text"]
        print(f"   AI: {response_text[:200]}...")

        # Step 3: Verify tracking_id was returned
        tracking_id = response.get("tracking_id")
        assert tracking_id is not None, \
            "Response should contain tracking_id for created order"

        # Step 4: Validate tracking_id format
        assert_tracking_id_valid(tracking_id)
        print(f"   ✅ Order created with tracking_id: {tracking_id}")

        # Store for next test
        pytest.last_tracking_id = tracking_id

    @pytest.mark.asyncio
    async def test_update_order_flow(
        self,
        ai_client: AIAgentClient,
        test_user_id: str
    ):
        """
        Test Flow 3: Customer updates delivery details.

        Steps:
        1. Customer requests to change delivery address
        2. AI Agent calls update_order with tracking_id
        3. AI confirms update
        4. Verify response structure
        """
        print("\n🧪 Test 3: Update Order Flow")

        # Get tracking_id from previous test or create new order
        if not hasattr(pytest, "last_tracking_id"):
            # Create order first
            await self.test_create_order_flow(ai_client, test_user_id)

        tracking_id = pytest.last_tracking_id

        # Step 1: Customer requests to update order
        new_address = "ул. Новая, дом 5, кв. 10"
        message = f"""Хочу изменить адрес доставки для заказа {tracking_id}.
        Новый адрес: {new_address}
        """
        print(f"   Customer: {message}")

        response = await ai_client.chat(
            message=message,
            user_id=test_user_id,
            request_id=f"test_update_{test_user_id}"
        )

        # Step 2: Verify AI responded
        assert "text" in response, "Response should contain text"
        response_text = response["text"]
        print(f"   AI: {response_text[:200]}...")

        # Step 3: Verify response mentions update/изменение
        assert any(word in response_text.lower() for word in ["обновлен", "изменен", "updated", tracking_id]), \
            "Response should mention order update or tracking_id"

        print(f"   ✅ Order {tracking_id} update requested successfully")

    @pytest.mark.asyncio
    async def test_track_order_flow(
        self,
        ai_client: AIAgentClient,
        test_user_id: str
    ):
        """
        Test Flow 4: Customer tracks order by tracking_id.

        Steps:
        1. Customer asks for order status with tracking_id
        2. AI Agent calls track_order
        3. AI responds with order status and details
        4. Verify order information in response
        """
        print("\n🧪 Test 4: Track Order Flow")

        # Get tracking_id from previous test or create new order
        if not hasattr(pytest, "last_tracking_id"):
            await self.test_create_order_flow(ai_client, test_user_id)

        tracking_id = pytest.last_tracking_id

        # Step 1: Customer asks for order status
        message = f"Какой статус заказа {tracking_id}?"
        print(f"   Customer: {message}")

        response = await ai_client.chat(
            message=message,
            user_id=test_user_id,
            request_id=f"test_track_{test_user_id}"
        )

        # Step 2: Verify AI responded
        assert "text" in response, "Response should contain text"
        response_text = response["text"]
        print(f"   AI: {response_text[:200]}...")

        # Step 3: Verify response contains order information
        # Should mention tracking_id and status
        assert tracking_id in response_text, \
            f"Response should mention tracking_id {tracking_id}"

        # Check for common status words
        status_keywords = ["статус", "status", "новый", "new", "оплачен", "paid"]
        assert any(word in response_text.lower() for word in status_keywords), \
            "Response should mention order status"

        print(f"   ✅ Order {tracking_id} status retrieved successfully")

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(
        self,
        ai_client: AIAgentClient,
        backend_client: BackendAPIClient,
        test_user_id: str
    ):
        """
        Test Flow 5: Multi-turn conversation with context.

        Steps:
        1. Customer asks general question
        2. Customer asks follow-up without repeating context
        3. AI maintains conversation context
        4. Verify contextual understanding
        """
        print("\n🧪 Test 5: Multi-Turn Conversation Flow")

        # Turn 1: Ask about products
        message1 = "Какие у вас есть букеты роз?"
        print(f"   Customer (turn 1): {message1}")

        response1 = await ai_client.chat(
            message=message1,
            user_id=test_user_id,
            request_id=f"test_multi_1_{test_user_id}"
        )

        assert "text" in response1
        print(f"   AI (turn 1): {response1['text'][:150]}...")

        # Turn 2: Ask follow-up about price (context: roses)
        message2 = "А сколько стоит самый дорогой?"
        print(f"   Customer (turn 2): {message2}")

        response2 = await ai_client.chat(
            message=message2,
            user_id=test_user_id,
            request_id=f"test_multi_2_{test_user_id}"
        )

        assert "text" in response2
        response_text2 = response2["text"]
        print(f"   AI (turn 2): {response_text2[:150]}...")

        # Verify AI understood context (should mention price/cost)
        price_keywords = ["стоит", "цена", "тенге", "price", "cost"]
        assert any(word in response_text2.lower() for word in price_keywords), \
            "AI should understand 'самый дорогой' refers to price in context of roses"

        print("   ✅ Context maintained across conversation turns")

    @pytest.mark.asyncio
    async def test_error_handling_invalid_tracking_id(
        self,
        ai_client: AIAgentClient,
        test_user_id: str
    ):
        """
        Test Flow 6: Error handling for invalid tracking ID.

        Steps:
        1. Customer provides invalid tracking_id
        2. AI Agent attempts to track order
        3. AI gracefully handles error
        4. Verify error message is user-friendly
        """
        print("\n🧪 Test 6: Error Handling Flow (Invalid Tracking ID)")

        # Step 1: Customer provides invalid tracking_id
        invalid_tracking_id = "000000000"  # 9 zeros (unlikely to exist)
        message = f"Проверь заказ {invalid_tracking_id}"
        print(f"   Customer: {message}")

        response = await ai_client.chat(
            message=message,
            user_id=test_user_id,
            request_id=f"test_error_{test_user_id}"
        )

        # Step 2: Verify AI responded (should not crash)
        assert "text" in response, "Response should contain text even on error"
        response_text = response["text"]
        print(f"   AI: {response_text[:200]}...")

        # Step 3: Verify error message is user-friendly
        error_keywords = ["не найден", "не могу найти", "не существует", "not found", "проверьте"]
        assert any(word in response_text.lower() for word in error_keywords), \
            "AI should indicate order was not found in a user-friendly way"

        print("   ✅ Gracefully handled invalid tracking_id")


# Test that can run without Claude API (direct MCP calls)
class TestDirectMCPCalls:
    """Direct MCP tool invocation tests (bypass AI Agent)."""

    @pytest.mark.asyncio
    async def test_mcp_list_products_direct(self, mcp_client: MCPServerClient):
        """
        Test direct MCP tool call for list_products.

        Verifies MCP server works independently of AI Agent.
        """
        print("\n🧪 Test: Direct MCP list_products Call")

        result = await mcp_client.call_tool(
            tool_name="list_products",
            arguments={
                "shop_id": config.TEST_SHOP_ID,
                "limit": 5
            },
            request_id="test_mcp_direct_list"
        )

        # Verify result structure
        assert "result" in result, "MCP response should contain 'result' field"
        products = result["result"]

        assert isinstance(products, list), "Products should be a list"
        assert len(products) > 0, "Should return at least 1 product"

        # Verify product structure
        first_product = products[0]
        required_fields = ["id", "name", "price"]
        for field in required_fields:
            assert field in first_product, f"Product should contain '{field}' field"

        print(f"   ✅ MCP returned {len(products)} products directly")

    @pytest.mark.asyncio
    async def test_mcp_get_shop_settings_direct(self, mcp_client: MCPServerClient):
        """
        Test direct MCP tool call for get_shop_settings.

        Verifies shop configuration retrieval.
        """
        print("\n🧪 Test: Direct MCP get_shop_settings Call")

        result = await mcp_client.call_tool(
            tool_name="get_shop_settings",
            arguments={"shop_id": config.TEST_SHOP_ID},
            request_id="test_mcp_direct_settings"
        )

        # Verify result structure
        assert "result" in result, "MCP response should contain 'result' field"
        settings = result["result"]

        assert isinstance(settings, dict), "Settings should be a dict"

        # Verify settings structure
        expected_fields = ["shop_name", "phone", "address"]
        for field in expected_fields:
            assert field in settings, f"Settings should contain '{field}' field"

        print(f"   ✅ Shop settings retrieved: {settings.get('shop_name')}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
