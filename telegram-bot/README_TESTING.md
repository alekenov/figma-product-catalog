# Telegram Bot Testing Guide

Testing the Telegram bot **without using Telegram** - using pytest and mock objects!

## 🎯 Overview

This testing setup allows you to:
- ✅ Test bot logic without a real Telegram bot token
- ✅ Mock the MCP client to simulate backend calls
- ✅ Test authorization, registration, and caching
- ✅ Verify complete user journeys
- ✅ Run tests CI/CD without external dependencies

## 📦 Installation

### 1. Install Testing Dependencies

```bash
cd /Users/alekenov/figma-product-catalog/telegram-bot

# Install pytest and friends
pip install -r requirements-test.txt

# Or manually:
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### 2. Verify Installation

```bash
# Check pytest is installed
pytest --version
# Should output: pytest 7.4.0 (or newer)

# Check async support
python -c "import pytest_asyncio; print('✅ pytest-asyncio installed')"
```

## 🚀 Running Tests

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Expected output:
# tests/test_authorization.py::test_check_authorization_first_time_not_authorized PASSED
# tests/test_authorization.py::test_check_authorization_user_is_registered PASSED
# tests/test_registration.py::test_handle_contact_valid_contact PASSED
# ...
# ========================= 20 passed in 2.34s ==========================
```

### Run Specific Test File

```bash
# Test only authorization
pytest tests/test_authorization.py -v

# Test only registration
pytest tests/test_registration.py -v

# Test only integration
pytest tests/test_integration.py -v
```

### Run Specific Test Function

```bash
# Run one test
pytest tests/test_authorization.py::test_check_authorization_first_time_not_authorized -v

# Run with detailed output
pytest tests/test_authorization.py::test_check_authorization_first_time_not_authorized -vv
```

### Run with Coverage

```bash
# Show code coverage
pytest tests/ --cov=bot --cov=mcp_client --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 📝 Run Test Scenarios

Test scenarios **simulate real user journeys** without pytest:

```bash
# Run scenario simulations
python test_scenarios.py

# Expected output:
# ======================================================================
# TELEGRAM BOT TEST SCENARIOS
# Simulating real user journeys without Telegram
# ======================================================================
#
# ======================================================================
# SCENARIO 1: New User Journey
# ======================================================================
#
# 1️⃣  User sends /start
#    Authorization result: False
#    Expected: False (not registered yet)
#
# 2️⃣  User shares contact: +77015211545, John Doe
#    Registered: {'id': 1, 'phone': '+77015211545', ...}
#    ✅ Client saved to database
# ...
# ✅ ALL SCENARIOS PASSED!
```

## 📚 What Tests Cover

### Unit Tests - Authorization (`test_authorization.py`)

| Test | What It Tests |
|------|---------------|
| `test_check_authorization_first_time_not_authorized` | New user not in database |
| `test_check_authorization_user_is_registered` | User found in database |
| `test_authorization_cache_hit` | Cache returns result without MCP call |
| `test_authorization_cache_ttl_expiration` | Cache expires after 5 minutes |
| `test_authorization_check_error_fallback` | Error handling - returns True if backend fails |
| `test_authorization_phone_used_for_tracking` | Saved phone available after auth |
| `test_authorization_multi_tenancy` | Shop ID isolation in database |
| `test_cache_invalidation_after_registration` | Cache cleared after registering |

### Unit Tests - Registration (`test_registration.py`)

| Test | What It Tests |
|------|---------------|
| `test_handle_contact_valid_contact` | Valid contact triggers registration |
| `test_handle_contact_invalid_contact` | Contact from different user rejected |
| `test_handle_contact_phone_extraction` | Phone number extracted from contact |
| `test_handle_contact_customer_name_from_telegram_profile` | Name extracted from Telegram profile |
| `test_handle_contact_mcp_error_fallback` | Error message on registration failure |
| `test_handle_contact_cache_invalidation` | Cache cleared after registration |

### Integration Tests (`test_integration.py`)

| Test | What It Tests |
|------|---------------|
| `test_flow_new_user_start_to_authorization` | Complete /start → contact → auth flow |
| `test_flow_registered_user_authorization_cached` | Cached auth for registered users |
| `test_flow_myorders_uses_saved_phone` | /myorders uses stored phone number |
| `test_flow_complete_user_journey_cache_expiration` | Full journey with cache lifecycle |

### Scenarios (`test_scenarios.py`)

| Scenario | What It Simulates |
|----------|------------------|
| Scenario 1 | New user: /start → register → /myorders |
| Scenario 2 | Cache performance: fast repeated auth |
| Scenario 3 | Cache expiration: TTL after 5 minutes |
| Scenario 4 | Multi-tenancy: shop isolation |

## 🔍 Understanding the Test Structure

### Fixtures (conftest.py)

Fixtures provide mock objects for tests:

```python
@pytest.fixture
def mock_mcp_client():
    """Mock MCP client - simulates backend calls."""
    client = AsyncMock()
    return client

@pytest.fixture
def mock_update(mock_message, mock_telegram_user, mock_chat):
    """Mock Telegram Update - simulates incoming message."""
    update = Update(update_id=1)
    update.message = mock_message
    return update

@pytest.fixture
def mock_client_record():
    """Mock database Client record."""
    return {
        "id": 42,
        "phone": "+77015211545",
        "telegram_user_id": "626599",
        "shop_id": 8
    }
```

### Test Pattern

Each test follows this pattern:

```python
@pytest.mark.asyncio
async def test_something(mock_mcp_client):
    """Test docstring explains what we're testing."""
    # Setup - prepare mocks and test data
    mock_mcp_client.get_telegram_client = AsyncMock(return_value=None)

    # Action - call the function we're testing
    result = await bot.check_authorization(user_id=626599)

    # Assert - verify the result
    assert result is False
    mock_mcp_client.get_telegram_client.assert_called_once()
```

## 🐛 Debugging Tests

### Run with Detailed Output

```bash
# Show print statements and full tracebacks
pytest tests/ -v -s

# -v = verbose
# -s = show print output (don't capture)
```

### Run Single Test with Debugging

```bash
# Run one test with print output
pytest tests/test_authorization.py::test_check_authorization_first_time_not_authorized -v -s

# Add breakpoints in test code:
import pdb; pdb.set_trace()
```

### View Mock Call Details

```python
# In test code, check what MCP client was called with:
print(mock_mcp_client.get_telegram_client.call_args)
# Output: call(telegram_user_id='626599', shop_id=8)

print(mock_mcp_client.register_telegram_client.call_count)
# Output: 1 (or however many times it was called)
```

## 🚦 CI/CD Integration

### GitHub Actions Example

```yaml
name: Bot Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r telegram-bot/requirements-test.txt
      - run: pytest telegram-bot/tests/ -v
      - run: python telegram-bot/test_scenarios.py
```

### Railway CI Example

```bash
# In deployment logs:
- pip install -r requirements-test.txt
- pytest tests/ -v  # Run before starting bot
```

## ✨ Key Testing Concepts

### 1. **Mocking** - Fake External Dependencies

```python
# Instead of calling real MCP server:
mock_mcp_client.get_telegram_client = AsyncMock(return_value=None)

# Bot code calls mock_mcp_client.get_telegram_client()
# Mock returns the value we set up
```

### 2. **Async Testing** - Testing Async Functions

```python
@pytest.mark.asyncio  # Tell pytest this is async
async def test_something():
    result = await bot.check_authorization(123)  # Await async calls
    assert result is True
```

### 3. **Caching Simulation** - Testing TTL Logic

```python
# Populate cache
await bot.check_authorization(user_id)

# Simulate time passing (change timestamp in cache)
is_auth, timestamp = bot.auth_cache[user_id]
bot.auth_cache[user_id] = (is_auth, timestamp - 400)  # 400 seconds ago

# Next call should refresh cache
await bot.check_authorization(user_id)
```

## 📊 Test Coverage Goals

Current coverage targets:

- ✅ Authorization logic: 100% (8 tests)
- ✅ Registration logic: 100% (6 tests)
- ✅ Integration flows: 100% (4 tests)
- ✅ Caching mechanism: 100% (multiple tests)
- ✅ Error handling: 100% (multiple tests)

Run coverage report:

```bash
pytest tests/ --cov=bot --cov-report=term-missing
```

## 🎓 Learning Resources

### Understanding the Tests

1. **Start here**: Read `test_authorization.py` to understand test structure
2. **Then**: Read `test_registration.py` to see contact handling
3. **Then**: Read `test_integration.py` to see complete flows
4. **Finally**: Run `test_scenarios.py` to see simulated journeys

### Modifying Tests

1. Add a new test function in appropriate `test_*.py` file
2. Use fixtures from `conftest.py` as parameters
3. Add `@pytest.mark.asyncio` for async tests
4. Run: `pytest tests/ -v`

### Adding New Functionality

1. Write test first (TDD approach)
2. Make test fail (red)
3. Implement feature in `bot.py`
4. Make test pass (green)
5. Refactor if needed
6. Run all tests: `pytest tests/ -v`

## ⚡ Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_authorization.py::test_check_authorization_first_time_not_authorized -v

# Run with coverage
pytest tests/ --cov=bot

# Run scenarios
python test_scenarios.py

# Run all + coverage + scenarios
pytest tests/ --cov=bot && python test_scenarios.py
```

## 🤝 Contributing Tests

When adding new features:

1. Create test case first
2. Ensure test fails initially
3. Implement feature
4. Verify test passes
5. Check all other tests still pass: `pytest tests/ -v`
6. Commit both feature and test

## 📞 Troubleshooting

### "No module named 'telegram'"

```bash
pip install python-telegram-bot
```

### "pytest: command not found"

```bash
pip install pytest pytest-asyncio
```

### "No module named 'bot'"

```bash
# Run tests from telegram-bot directory
cd telegram-bot
pytest tests/ -v
```

### Test hangs/times out

```bash
# Add timeout to async tests
@pytest.mark.asyncio
@pytest.mark.timeout(5)  # 5 second timeout
async def test_something():
    ...
```

---

**Happy testing!** 🧪✅
