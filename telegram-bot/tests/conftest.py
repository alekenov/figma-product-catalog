"""pytest configuration and shared fixtures for bot tests."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock
from datetime import datetime
from telegram import Update, User, Chat, Message, Contact
from telegram.ext import ContextTypes


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing."""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_telegram_user():
    """Create mock Telegram user."""
    return User(
        id=626599,
        is_bot=False,
        first_name="John",
        last_name="Doe",
        username="johndoe",
        language_code="en"
    )


@pytest.fixture
def mock_chat():
    """Create mock Telegram chat."""
    return Chat(id=626599, type="private")


@pytest.fixture
def mock_message(mock_telegram_user, mock_chat):
    """Create mock Telegram message."""
    msg = Message(
        message_id=1,
        date=datetime.now(),
        chat=mock_chat,
        from_user=mock_telegram_user,
        text="test message"
    )
    return msg


@pytest.fixture
def mock_message_with_contact(mock_telegram_user, mock_chat):
    """Create mock message with contact."""
    contact = Contact(
        phone_number="+77015211545",
        first_name="John",
        last_name="Doe",
        user_id=626599
    )
    msg = Message(
        message_id=2,
        date=datetime.now(),
        chat=mock_chat,
        from_user=mock_telegram_user,
        contact=contact
    )
    return msg


@pytest.fixture
def mock_update(mock_message, mock_telegram_user, mock_chat):
    """Create mock Telegram update (text message)."""
    # Use MagicMock to avoid Telegram's frozen object restrictions
    update = MagicMock()
    update.update_id = 1
    update.message = mock_message
    update.effective_user = mock_telegram_user
    update.effective_chat = mock_chat
    return update


@pytest.fixture
def mock_update_with_contact(mock_message_with_contact, mock_telegram_user, mock_chat):
    """Create mock Telegram update (with contact)."""
    # Use MagicMock to avoid Telegram's frozen object restrictions
    update = MagicMock()
    update.update_id = 2
    update.message = mock_message_with_contact
    update.effective_user = mock_telegram_user
    update.effective_chat = mock_chat
    return update


@pytest.fixture
def mock_context():
    """Create mock Telegram context."""
    context = MagicMock()
    context.user_data = {}
    context.chat_data = {}
    context.bot_data = {}
    return context


@pytest.fixture
def mock_client_record():
    """Create mock client database record."""
    return {
        "id": 42,
        "phone": "+77015211545",
        "customerName": "John Doe",
        "telegram_user_id": "626599",
        "telegram_username": "johndoe",
        "telegram_first_name": "John",
        "shop_id": 8
    }


@pytest.fixture
def mock_order_record():
    """Create mock order database record."""
    return {
        "id": 1,
        "tracking_id": "ABC123DEF",
        "orderNumber": "ORD-001",
        "customerName": "John Doe",
        "phone": "+77015211545",
        "telegram_user_id": "626599",
        "status": "NEW",
        "delivery_date": "2025-10-20",
        "delivery_address": "ул. Макатаева 127",
        "shop_id": 8,
        "created_at": "2025-10-16T10:30:45Z"
    }
