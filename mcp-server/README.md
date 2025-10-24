# Flower Shop MCP Server

Model Context Protocol server for the Figma Product Catalog (Flower Shop) backend API.

## Features

This MCP server provides tools for:

### 🔐 Authentication
- `login` - Authenticate and get access token
- `get_current_user` - Get current user information

### 🌸 Products
- `list_products` - Browse products with filtering and search
- `get_product` - Get detailed product information
- `create_product` - Create new products (admin)
- `update_product` - Update existing products (admin)

### 📦 Orders
- `list_orders` - View orders with filtering (admin)
- `get_order` - Get order details (admin)
- `create_order` - Create new order (public)
- `update_order_status` - Update order status (admin)
- `track_order` - Track order by tracking ID (public)

### 📊 Inventory & Warehouse
- `list_warehouse_items` - View warehouse inventory (admin)
- `add_warehouse_stock` - Add stock to warehouse (admin)
- `record_warehouse_operation` - Record stock movements (IN/OUT/WRITE_OFF) - routes to backend delivery/sale/writeoff endpoints
- `get_warehouse_history` - Movement history for specific item (admin)
- `create_inventory_check` - Create complete inventory audit with all items at once (admin)
- `list_inventory_checks` - View audit sessions (admin)

### 🔍 AI Visual Search
- `search_similar_bouquets` - Find similar products by image (pgvector PostgreSQL)

### ⚙️ Shop Settings
- `get_shop_settings` - Get shop configuration (admin)
- `update_shop_settings` - Update shop settings (admin)

### 💳 Kaspi Pay (Kazakhstan Payments)
- `kaspi_create_payment` - Create remote payment request
- `kaspi_check_payment_status` - Check payment status
- `kaspi_get_payment_details` - Get payment details and available refund amount
- `kaspi_refund_payment` - Refund payment (full or partial)

## Installation

### Using uv (recommended)

```bash
cd mcp-server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip

```bash
cd mcp-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
# Backend API URL (default: http://localhost:8014/api/v1)
export API_BASE_URL="http://localhost:8014/api/v1"

# Default shop ID for testing (default: 8)
export DEFAULT_SHOP_ID="8"
```

## Usage

### Testing with MCP Inspector

```bash
# From mcp-server directory
uv run mcp dev server.py
```

This will open the MCP Inspector in your browser for interactive testing.

### Direct Execution

```bash
python server.py
```

### Adding to Claude Code

Add to your Claude Code MCP configuration:

```bash
# Local stdio server
claude mcp add flower-shop --transport stdio "uv run /Users/alekenov/figma-product-catalog/mcp-server/server.py"
```

Or edit `~/.config/claude/mcp_config.json`:

```json
{
  "mcpServers": {
    "flower-shop": {
      "transport": "stdio",
      "command": "uv",
      "args": ["run", "/Users/alekenov/figma-product-catalog/mcp-server/server.py"],
      "env": {
        "API_BASE_URL": "http://localhost:8014/api/v1",
        "DEFAULT_SHOP_ID": "8"
      }
    }
  }
}
```

## Example Usage in Claude Code

Once installed, you can interact with the API through Claude Code:

```
User: Login with phone 77015211545 and password securepass123

Claude: <calls login tool>

User: List all products in shop 8

Claude: <calls list_products with shop_id=8>

User: Create a new order for customer Ivan

Claude: <calls create_order with provided details>

User: Запиши списание 5 роз из-за повреждения

Claude: <calls record_warehouse_operation with warehouse_item_id=5, quantity=-5, operation_type="WRITE_OFF", notes="Повреждены">

User: Начни инвентаризацию для роз и тюльпанов

Claude: <calls create_inventory_check with conducted_by="Admin", items=[{warehouse_item_id: 5, actual_quantity: 48}, {warehouse_item_id: 8, actual_quantity: 30}], comment="Ежемесячная инвентаризация">
```

## Authentication Flow

1. **Login**: Call `login(phone, password)` to get JWT token
2. **Use Token**: Pass the token to authenticated endpoints (admin operations)
3. **Public Endpoints**: Some endpoints (like `list_products`, `create_order`) don't require tokens when shop_id is provided

## Multi-Tenancy

The backend enforces multi-tenancy:
- **Authenticated requests**: shop_id is extracted from JWT token
- **Public requests**: shop_id must be provided as query parameter
- Each shop can only access its own data

## Development

### Project Structure

```
mcp-server/
├── server.py               # Slim orchestrator, registers tools
├── core/                   # Shared infrastructure
│   ├── config.py           # Configuration
│   ├── api_client.py       # HTTP client with retry logic
│   ├── registry.py         # Tool metadata registry
│   ├── exceptions.py       # Typed exceptions
│   └── logging.py          # Structured logging
├── domains/                # Domain-driven tool organization
│   ├── auth/               # Authentication (2 tools)
│   ├── products/           # Products (8 tools)
│   ├── orders/             # Orders (10 tools)
│   ├── inventory/          # Warehouse (7 tools)
│   ├── telegram/           # Telegram clients (2 tools)
│   ├── shop/               # Shop settings (10 tools)
│   ├── kaspi/              # Kaspi Pay (4 tools)
│   └── visual_search/      # AI search (1 tool)
├── tests/                  # Pytest test suite
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Adding New Tools

To add a new tool, define a function with the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """
    Description of what the tool does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    result = await make_request(
        method="GET",
        endpoint="/my-endpoint",
        params={"param1": param1, "param2": param2}
    )
    return result
```

## Troubleshooting

### Connection Issues

If MCP server can't connect to backend:
1. Ensure backend is running on `http://localhost:8014`
2. Check `API_BASE_URL` environment variable
3. Verify backend is accepting connections

### Authentication Errors

If getting 401 errors:
1. Verify credentials are correct
2. Check that token is being passed correctly
3. Ensure token hasn't expired (default: 7 days)

### Shop ID Issues

If getting empty results:
1. Verify `shop_id` parameter is correct
2. Ensure shop exists in database
3. Check that shop is active

## API Coverage

MCP server provides **43 tools** across **8 domains**, covering critical backend functionality:

| Domain | Backend Endpoints | MCP Tools | Coverage |
|--------|-------------------|-----------|----------|
| **auth** | 3 | 2 | 67% |
| **products** | 15 | 8 | 53% |
| **orders** | 18 | 10 | 56% |
| **inventory** | 8 | 6 | 75% |
| **shop** | 12 | 10 | 83% |
| **kaspi** | 4 | 4 | **100%** ✅ |
| **visual_search** | 2 | 1 | 50% (pgvector only) |
| **telegram** | 2 | 2 | **100%** ✅ |

**Key Improvements:**
- ✅ Warehouse operations adapted to backend architecture (6 tools, 75% coverage)
- ✅ Visual search simplified (removed Cloudflare Vectorize, kept pgvector)
- ✅ Full Kaspi Pay integration for Kazakhstan market

**Total:** 43 MCP tools covering most critical backend operations

## API Backend

This MCP server connects to the Figma Product Catalog backend:
- **Repository**: alekenov/figma-product-catalog
- **Backend Port**: 8014
- **API Docs**: http://localhost:8014/docs
- **Database**: PostgreSQL (Railway)

## License

MIT
