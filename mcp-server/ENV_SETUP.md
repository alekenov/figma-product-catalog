# Environment Variables Configuration

## Current Configuration

The MCP server is configured to work with:

```bash
API_BASE_URL="http://localhost:8014/api/v1"
DEFAULT_SHOP_ID="8"
```

## Changing Configuration

### Option 1: Edit Claude Code Config

Edit `~/.claude.json` (or project `.claude.json`):

```json
{
  "mcpServers": {
    "flower-shop": {
      "transport": "stdio",
      "command": "/Users/alekenov/figma-product-catalog/mcp-server/.venv/bin/python",
      "args": ["/Users/alekenov/figma-product-catalog/mcp-server/server.py"],
      "env": {
        "API_BASE_URL": "http://localhost:8014/api/v1",
        "DEFAULT_SHOP_ID": "8"
      }
    }
  }
}
```

### Option 2: Use .env File

Create `.env` in `mcp-server/` directory:

```bash
API_BASE_URL=http://localhost:8014/api/v1
DEFAULT_SHOP_ID=8
```

### Option 3: Export Variables

```bash
export API_BASE_URL="http://localhost:8014/api/v1"
export DEFAULT_SHOP_ID="8"
```

## Production Configuration

For production backend:

```bash
API_BASE_URL="https://your-backend.railway.app/api/v1"
DEFAULT_SHOP_ID="1"
```

## Verification

Test that environment is correct:

```bash
cd mcp-server
.venv/bin/python -c "
import os
print('API_BASE_URL:', os.getenv('API_BASE_URL', 'http://localhost:8014/api/v1'))
print('DEFAULT_SHOP_ID:', os.getenv('DEFAULT_SHOP_ID', '8'))
"
```
