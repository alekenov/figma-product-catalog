# MCP Shared Library

Common schemas, validators, and utilities shared between `mcp-server` (Railway backend) and `mcp-production` (cvety.kz proxy).

## Structure

```
mcp-shared/
├── schemas/
│   ├── products.py    # ProductResponse, ProductCreate
│   ├── orders.py      # OrderResponse, OrderCreate
│   └── common.py      # BaseResponse, ErrorResponse
├── utils/
│   ├── retry.py       # Retry logic with exponential backoff
│   ├── logging.py     # Unified logging configuration
│   └── auth.py        # Token validation, phone normalization
└── enums.py           # OrderStatus, ProductType, DeliveryType
```

## Usage

### In mcp-production

```python
import sys
sys.path.append('../mcp-shared')

from mcp_shared.schemas.products import ProductResponse
from mcp_shared.utils.retry import retry_with_backoff
from mcp_shared.enums import OrderStatus

@retry_with_backoff(max_retries=3)
async def fetch_products():
    ...
```

### In mcp-server

```python
import sys
sys.path.append('../mcp-shared')

from mcp_shared.schemas.orders import OrderCreate
from mcp_shared.utils.logging import setup_logging

setup_logging(level="INFO")
```

## Key Features

### Retry Logic

```python
from mcp_shared.utils.retry import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=1.0)
async def call_api():
    # Will retry 3 times with delays: 1s, 2s, 4s
    pass
```

### Circuit Breaker

```python
from mcp_shared.utils.retry import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker
async def call_external_service():
    # If fails 5 times, circuit opens for 60 seconds
    pass
```

### Order Status Validation

```python
from mcp_shared.enums import OrderStatus

valid_next = OrderStatus.get_valid_transitions("assembled")
# Returns: ["in-transit", "cancelled"]
```

## Development

This is a local Python package (not published to PyPI). Both `mcp-server` and `mcp-production` import it via relative path:

```python
sys.path.append('../mcp-shared')
```

## Version

0.1.0 - Initial release with schemas, utils, and enums
