# Integration Test Suite

End-to-end integration tests for conversational AI flows in the flower shop system.

Tests critical user journeys through **AI Agent → MCP Server → Backend** chain, ensuring the entire system works together correctly.

---

## 🎯 Test Coverage

### TestConversationFlows (Requires AI Agent)
Full conversational flows using Claude AI:

1. **`test_list_products_flow`** - Product search with price filters
   - Customer: "Покажи мне цветы в районе 10000-15000 тенге"
   - Verifies AI calls `list_products` with correct parameters
   - Validates products are in requested price range

2. **`test_create_order_flow`** - Order creation
   - Customer provides order details in natural language
   - Verifies AI extracts all required fields
   - Validates tracking_id format (9 digits)

3. **`test_update_order_flow`** - Order modification
   - Customer requests to change delivery address
   - Verifies AI calls `update_order` with tracking_id
   - Validates update confirmation

4. **`test_track_order_flow`** - Order status tracking
   - Customer asks for order status
   - Verifies AI retrieves and presents order information
   - Validates response contains tracking_id and status

5. **`test_multi_turn_conversation`** - Context maintenance
   - Turn 1: "Какие у вас есть букеты роз?"
   - Turn 2: "А сколько стоит самый дорогой?"
   - Verifies AI remembers previous context (roses)

6. **`test_error_handling_invalid_tracking_id`** - Graceful errors
   - Customer provides invalid tracking_id
   - Verifies AI handles error without crashing
   - Validates user-friendly error message

### TestDirectMCPCalls (Standalone Tests)
Direct MCP tool invocation without AI:

7. **`test_mcp_list_products_direct`** - Direct product listing
   - Calls MCP `/call-tool` endpoint directly
   - Verifies tool execution and response structure
   - Tests MCP server independently

8. **`test_mcp_get_shop_settings_direct`** - Shop configuration
   - Retrieves shop settings via MCP
   - Validates settings structure
   - Tests public endpoint access

---

## 🚀 Quick Start

### Prerequisites

**Option 1: Docker Compose (Recommended)**
```bash
# Start all services with one command
./scripts/docker-start.sh
```

All services run on their default ports:
- **Backend API**: port 8014
- **MCP Server**: port 8001
- **AI Agent**: port 8000

**Option 2: Standalone Services**
```bash
cd backend && python3 main.py           # Port 8014
cd mcp-server && ./start.sh             # Port 8001
cd ai-agent-service && python3 main.py  # Port 8000 (or 8015 for dev)
```

For standalone mode with port 8015:
```bash
export AI_AGENT_URL=http://localhost:8000  # Docker default, use 8015 for standalone
cd ai-agent-service && PORT=8015 python3 main.py
```

### Install Dependencies

```bash
cd integration-tests
pip3 install -r requirements.txt
```

### Run Tests

**Option 1: Smart Runner (Recommended)**
```bash
./run_tests.sh
```

The runner:
- ✅ Checks which services are available
- ✅ Runs appropriate test suite automatically
- ✅ Provides helpful feedback for missing services

**Option 2: Manual pytest**
```bash
# Run all tests (requires AI Agent)
pytest test_conversation_flows.py -v

# Run only direct MCP tests (no AI Agent needed)
pytest test_conversation_flows.py::TestDirectMCPCalls -v

# Run specific test
pytest test_conversation_flows.py::TestDirectMCPCalls::test_mcp_list_products_direct -v
```

---

## 🔧 Configuration

### Environment Variables

Override service URLs if needed:

```bash
export BACKEND_URL=http://localhost:8014
export MCP_SERVER_URL=http://localhost:8001
export AI_AGENT_URL=http://localhost:8000  # Docker default, use 8015 for standalone
export TEST_SHOP_ID=8
```

Edit `config.py` for advanced configuration:
- Request timeouts
- Health check intervals
- Test customer data
- Verbose logging

### Test User Credentials

Tests use these credentials (configured in `config.py`):
- **Shop ID**: 8
- **Test phone**: 77777777777
- **Test customer**: "Integration Test Customer"
- **Test address**: "ул. Тестовая, дом 1, кв. 1"

---

## 📊 Test Results

### Current Status (2025-10-07)

**Direct MCP Tests**: ✅ 2/2 passing
- `test_mcp_list_products_direct` ✅
- `test_mcp_get_shop_settings_direct` ✅

**AI Conversation Tests**: ⏳ Requires AI Agent + CLAUDE_API_KEY
- 6 tests available
- Requires `CLAUDE_API_KEY` environment variable
- Start AI agent service to run full suite

### Running Full Test Suite

To run all 8 tests:

```bash
# 1. Set Claude API key
export CLAUDE_API_KEY=sk-ant-...

# 2. Start all services
cd backend && python3 main.py &
cd mcp-server && ./start.sh &
cd ai-agent-service && python3 main.py &

# 3. Run tests
cd integration-tests && ./run_tests.sh
```

---

## 🛠️ Troubleshooting

### "Services are not healthy"

**Problem**: Health check fails before running tests

**Solutions**:
1. Check if services are actually running:
   ```bash
   curl http://localhost:8014/health  # Backend
   curl http://localhost:8001/health  # MCP Server
   curl http://localhost:8000/health  # AI Agent (Docker port)
   ```

2. Wait 5-10 seconds after starting services for initialization

3. Skip health checks (not recommended):
   ```bash
   export SKIP_HEALTH_CHECKS=true
   pytest test_conversation_flows.py::TestDirectMCPCalls -v
   ```

### "Tracking ID format is invalid"

**Problem**: Test expects 9-digit tracking ID but gets different format

**Solution**: Check backend `Order` model generates correct tracking_id format:
```python
# backend/models/orders.py
# Should generate 9-digit random number
```

### "Test timeout"

**Problem**: Request takes too long

**Solutions**:
1. Increase timeout in `config.py`:
   ```python
   REQUEST_TIMEOUT: int = 60  # Increase from 30 to 60
   ```

2. Check AI Agent logs for slow Claude API calls

3. Verify backend database isn't overloaded

### "CLAUDE_API_KEY not found"

**Problem**: AI Agent tests fail with authentication error

**Solution**: Set your Claude API key:
```bash
export CLAUDE_API_KEY=sk-ant-api03-...
```

Get your API key at: https://console.anthropic.com/

---

## 📝 Writing New Tests

### Adding a Conversation Flow Test

```python
@pytest.mark.asyncio
async def test_my_new_flow(
    self,
    ai_client: AIAgentClient,
    test_user_id: str
):
    """Test description."""
    print("\n🧪 Test X: My New Flow")

    # Step 1: Customer interaction
    message = "Хочу заказать..."
    response = await ai_client.chat(
        message=message,
        user_id=test_user_id,
        request_id=f"test_my_{test_user_id}"
    )

    # Step 2: Assertions
    assert "text" in response
    assert response.get("tracking_id") is not None

    print(f"   ✅ Test completed")
```

### Adding a Direct MCP Test

```python
@pytest.mark.asyncio
async def test_mcp_new_tool(self, mcp_client: MCPServerClient):
    """Test direct MCP tool call."""
    print("\n🧪 Test: Direct MCP new_tool Call")

    result = await mcp_client.call_tool(
        tool_name="new_tool",
        arguments={"param": "value"},
        request_id="test_mcp_new_tool"
    )

    assert "result" in result
    assert result["result"] is not None

    print(f"   ✅ MCP tool executed successfully")
```

---

## 🏗️ Architecture

### Test Infrastructure

```
integration-tests/
├── config.py                      # Configuration (URLs, timeouts, shop_id)
├── test_utils.py                  # Helper classes and assertions
│   ├── ServiceHealthChecker       # Async health checks
│   ├── AIAgentClient             # /chat endpoint wrapper
│   ├── MCPServerClient           # /call-tool endpoint wrapper
│   ├── BackendAPIClient          # Direct backend API calls
│   └── Assertion helpers         # Validation utilities
├── test_conversation_flows.py     # 8 E2E tests
├── run_tests.sh                  # Smart test runner
├── requirements.txt              # pytest, pytest-asyncio, httpx
└── README.md                     # This file
```

### Test Fixtures

- **`event_loop`** - Async event loop for pytest-asyncio
- **`check_services_health`** - Session-scoped health check (runs once)
- **`ai_client`** - AI Agent client instance
- **`mcp_client`** - MCP Server client instance
- **`backend_client`** - Backend API client instance
- **`test_user_id`** - Unique user ID per test (with auto-cleanup)

### Request Flow

```
Customer Message
      ↓
AI Agent (/chat)
      ↓
MCP Server (/call-tool)
      ↓
Backend API (/api/v1/...)
      ↓
PostgreSQL Database
```

Tests verify each layer works correctly and data flows through entire chain.

---

## 🎓 Best Practices

### 1. Isolation
- Each test gets unique `test_user_id`
- Conversation history auto-cleared after test
- No shared state between tests

### 2. Realistic Data
- Use Russian language messages (actual customer language)
- Natural language inputs (not JSON)
- Test customer provides delivery details like real users

### 3. Clear Assertions
- Verify response structure (`"text" in response`)
- Validate business logic (price in range, tracking_id format)
- Check error handling (invalid inputs, missing data)

### 4. Helpful Output
- Print test name and description
- Show customer message and AI response (truncated)
- Display success indicators (✅ emojis)

---

## 🚦 CI Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r mcp-server/requirements.txt
          pip install -r integration-tests/requirements.txt

      - name: Start services
        run: |
          cd backend && python main.py &
          cd mcp-server && python http_wrapper.py &
          sleep 10  # Wait for services

      - name: Run integration tests
        env:
          SKIP_HEALTH_CHECKS: false
          BACKEND_URL: http://localhost:8014
          MCP_SERVER_URL: http://localhost:8001
        run: |
          cd integration-tests
          pytest test_conversation_flows.py::TestDirectMCPCalls -v
```

---

## 📚 Related Documentation

- **MCP Server**: `../mcp-server/README.md`
- **AI Agent**: `../ai-agent-service/README.md`
- **Backend API**: `../backend/API_TESTING_GUIDE.md`
- **Test Utils**: See docstrings in `test_utils.py`

---

**Generated**: 2025-10-07
**Status**: ✅ Task 3.2 Complete
**Test Coverage**: 8 tests (2 passing, 6 require AI Agent)
