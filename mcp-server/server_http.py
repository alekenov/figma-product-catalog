"""
HTTP wrapper for MCP Server - for local Telegram bot testing.
"""
import os
os.environ["API_BASE_URL"] = "http://localhost:8014/api/v1"
os.environ["DEFAULT_SHOP_ID"] = "8"

# Import the main MCP server
from server import mcp

if __name__ == "__main__":
    print("🌸 Starting MCP Server in HTTP mode")
    print("📡 Port: 8000")
    print("🏪 Shop ID: 8")
    print("🔗 Backend: http://localhost:8014/api/v1\n")

    # Run with streamable-http transport
    mcp.run(transport="streamable-http")
