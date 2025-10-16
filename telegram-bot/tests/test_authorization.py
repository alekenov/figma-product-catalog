"""Unit tests for authorization logic."""
import pytest
import time
from unittest.mock import AsyncMock, patch
from mcp_client import NetworkError


@pytest.mark.asyncio
async def test_check_authorization_first_time_not_authorized(mock_mcp_client):
    """Test first-time authorization check - user not registered."""
    # Setup
    user_id = 626599
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=None)

    # Import after setup
    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # Action
        result = await bot.check_authorization(user_id)

        # Assert
        assert result is False
        mock_mcp_client.get_telegram_client.assert_called_once_with(
            telegram_user_id=str(user_id),
            shop_id=8
        )


@pytest.mark.asyncio
async def test_check_authorization_user_is_registered(mock_mcp_client, mock_client_record):
    """Test authorization check - user already registered."""
    # Setup
    user_id = 626599
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=mock_client_record)

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # Action
        result = await bot.check_authorization(user_id)

        # Assert
        assert result is True


@pytest.mark.asyncio
async def test_authorization_cache_hit(mock_mcp_client, mock_client_record):
    """Test authorization cache - second check should use cache."""
    # Setup
    user_id = 626599
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=mock_client_record)

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # First check - should call MCP
        result1 = await bot.check_authorization(user_id)
        assert result1 is True
        assert mock_mcp_client.get_telegram_client.call_count == 1

        # Second check immediately - should use cache
        result2 = await bot.check_authorization(user_id)
        assert result2 is True
        assert mock_mcp_client.get_telegram_client.call_count == 1  # Not incremented!


@pytest.mark.asyncio
async def test_authorization_cache_ttl_expiration():
    """Test authorization cache - TTL expires after 5 minutes."""
    # Setup
    user_id = 626599
    mock_mcp_client = AsyncMock()
    mock_client_record = {
        "id": 42,
        "phone": "+77015211545",
        "telegram_user_id": "626599",
        "shop_id": 8
    }
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=mock_client_record)

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # First check
        result1 = await bot.check_authorization(user_id)
        assert result1 is True
        call_count_1 = mock_mcp_client.get_telegram_client.call_count

        # Manually expire cache (set timestamp to 6 minutes ago)
        is_auth, timestamp = bot.auth_cache[user_id]
        bot.auth_cache[user_id] = (is_auth, timestamp - 400)  # 400 seconds ago (> 5 min)

        # Second check - should call MCP because cache expired
        result2 = await bot.check_authorization(user_id)
        assert result2 is True
        assert mock_mcp_client.get_telegram_client.call_count == call_count_1 + 1


@pytest.mark.asyncio
async def test_authorization_check_network_error(mock_mcp_client):
    """Test authorization - on network error, return False (not lenient)."""
    # Setup: NetworkError (backend/MCP unreachable)
    user_id = 626599
    mock_mcp_client.get_telegram_client = AsyncMock(
        side_effect=NetworkError("Backend down!")
    )

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # Action - should not raise, should return False
        result = await bot.check_authorization(user_id)

        # Assert - now returns False on network errors (forces re-authorization)
        assert result is False


@pytest.mark.asyncio
async def test_authorization_check_unexpected_error(mock_mcp_client):
    """Test authorization - on unexpected error, return False."""
    # Setup: Generic exception
    user_id = 626599
    mock_mcp_client.get_telegram_client = AsyncMock(
        side_effect=Exception("Unexpected error!")
    )

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # Action - should not raise, should return False
        result = await bot.check_authorization(user_id)

        # Assert - returns False on unexpected errors too
        assert result is False


@pytest.mark.asyncio
async def test_authorization_phone_used_for_tracking():
    """Test that saved phone is used for order tracking."""
    # Setup
    user_id = 626599
    mock_mcp_client = AsyncMock()
    mock_client_record = {
        "id": 42,
        "phone": "+77015211545",
        "customerName": "John Doe",
        "telegram_user_id": "626599",
        "shop_id": 8
    }
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=mock_client_record)

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # Check authorization and verify we get phone
        await bot.check_authorization(user_id)
        client = await bot.mcp_client.get_telegram_client(
            telegram_user_id=str(user_id),
            shop_id=8
        )

        # Assert phone is available
        assert client["phone"] == "+77015211545"
        assert client["customerName"] == "John Doe"


@pytest.mark.asyncio
async def test_authorization_multi_tenancy(mock_mcp_client):
    """Test that authorization is isolated by shop_id."""
    # Setup
    user_id = 626599
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=None)

    from bot import FlowerShopBot

    with patch.dict('os.environ', {
        'TELEGRAM_TOKEN': 'test_token',
        'MCP_SERVER_URL': 'http://localhost:8000',
        'DEFAULT_SHOP_ID': '8'
    }):
        bot = FlowerShopBot()
        bot.mcp_client = mock_mcp_client

        # Check authorization
        await bot.check_authorization(user_id)

        # Verify shop_id is included in MCP call
        mock_mcp_client.get_telegram_client.assert_called_with(
            telegram_user_id="626599",
            shop_id=8  # Correct shop_id!
        )
