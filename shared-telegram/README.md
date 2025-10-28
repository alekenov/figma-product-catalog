# Shared Telegram Bot Modules

This directory contains shared utility modules used by both customer-bot and admin-bot.

## Purpose

Eliminate code duplication between telegram bots by providing a single source of truth for common functionality.

## Modules

### `mcp_client.py`
MCP (Model Context Protocol) HTTP client for communicating with backend API.

**Key Features:**
- HTTP transport for MCP tools
- Error handling and retries
- Request/response logging
- Tool invocation interface

**Usage:**
```python
import sys
sys.path.append('../shared-telegram')
from mcp_client import MCPClient

client = MCPClient(base_url="http://localhost:8014")
result = await client.call_tool("list_products", {"shop_id": 8})
```

### `logging_config.py`
Centralized logging configuration with structured logging support.

**Key Features:**
- Structured JSON logging
- Context binding (request_id, user_id)
- Log level configuration
- File and console handlers

**Usage:**
```python
from logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
logger.info("Bot started", extra={"shop_id": 8})
```

### `formatters.py`
Utility functions for formatting data in telegram messages.

**Key Features:**
- Price formatting (kopecks → tenge)
- Product image extraction and formatting
- List chunking for pagination

**Usage:**
```python
from formatters import format_price, extract_product_images

price_str = format_price(150000)  # "1,500 ₸"
images = extract_product_images(product_data)
```

## Benefits

- **Single Source of Truth**: Bug fixes and improvements automatically benefit both bots
- **Easier Maintenance**: Update logic in one place
- **Consistent Behavior**: Both bots use identical implementations
- **Reduced Code Size**: 367 lines of duplication eliminated

## Adding New Shared Modules

When you find duplicated code between bots:

1. Create new module in `shared-telegram/`
2. Move shared functionality there
3. Update imports in both bots
4. Remove duplicated files
5. Update this README
6. Test both bots

## Testing

Verify both bots can import shared modules:

```bash
# Test customer-bot
python3 -c "import sys; sys.path.append('customer-bot'); import bot; print('✓ customer-bot OK')"

# Test admin-bot
python3 -c "import sys; sys.path.append('admin-bot'); import bot; print('✓ admin-bot OK')"
```

## History

**Created**: 2025-10-28
**Reason**: Eliminate 367 lines of duplicated code between customer-bot and admin-bot
**Initial Modules**: mcp_client.py, logging_config.py, formatters.py
