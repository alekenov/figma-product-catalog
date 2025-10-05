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

### 📊 Inventory
- `list_warehouse_items` - View warehouse inventory (admin)
- `add_warehouse_stock` - Add stock to warehouse (admin)

### ⚙️ Shop Settings
- `get_shop_settings` - Get shop configuration (admin)
- `update_shop_settings` - Update shop settings (admin)

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
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project configuration
└── README.md          # This file
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

## API Backend

This MCP server connects to the Figma Product Catalog backend:
- **Repository**: alekenov/figma-product-catalog
- **Backend Port**: 8014
- **API Docs**: http://localhost:8014/docs
- **Database**: PostgreSQL (Railway)

## License

MIT
