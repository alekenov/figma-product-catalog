"""
MCP Client for calling Flower Shop API tools via MCP server.
Simplified version - only authentication methods (other API calls go through AI Agent).
"""
import os
import httpx
from typing import Dict, Any, Optional


# Custom exceptions for better error handling
class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class NetworkError(MCPClientError):
    """Network connectivity or server error (can't reach backend/MCP)."""
    pass


class ClientNotFoundError(MCPClientError):
    """Telegram client not found in database (404 response)."""
    pass


class MCPClient:
    """Client for interacting with MCP server over HTTP."""

    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url.rstrip('/') if mcp_server_url else None
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool by name with given arguments.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Dictionary of tool arguments

        Returns:
            Tool execution result

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.mcp_server_url:
            raise NetworkError("MCP server URL not configured")

        response = await self.client.post(
            f"{self.mcp_server_url}/call-tool",
            json={
                "name": tool_name,
                "arguments": arguments
            }
        )
        response.raise_for_status()
        return response.json()

    # Telegram Client Tools
    async def get_telegram_client(
        self,
        telegram_user_id: str,
        shop_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get telegram client by telegram_user_id.
        Returns client dict if found, None if not found (404).
        Raises NetworkError on connectivity/server issues.
        """
        try:
            import logging
            logger = logging.getLogger(__name__)

            # Use backend API directly instead of MCP server
            backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")
            if not backend_url:
                raise NetworkError("BACKEND_API_URL environment variable not configured")

            logger.info(f"get_telegram_client: Using backend_url={backend_url}")
            response = await self.client.get(
                f"{backend_url}/telegram/client",
                params={"telegram_user_id": telegram_user_id, "shop_id": shop_id}
            )

            if response.status_code == 404:
                logger.info(f"Telegram client not found: {telegram_user_id}")
                return None

            if response.status_code >= 500:
                raise NetworkError(f"Backend server error: HTTP {response.status_code}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Network error in get_telegram_client: {e}")
            raise NetworkError(f"Failed to connect to backend: {e}")
        except NetworkError:
            raise  # Re-raise our custom error
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in get_telegram_client: {e}")
            raise NetworkError(f"Unexpected error: {e}")

    async def register_telegram_client(
        self,
        telegram_user_id: str,
        phone: str,
        customer_name: str,
        shop_id: int,
        telegram_username: Optional[str] = None,
        telegram_first_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register or update telegram client with contact information.
        Returns client data dict on success (must contain 'id' field).
        Raises NetworkError if both backend and MCP registration fail.
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Use backend API directly
            backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")
            if not backend_url:
                raise NetworkError("BACKEND_API_URL environment variable not configured")

            logger.info(f"register_telegram_client: Using backend_url={backend_url}")
            logger.info(f"Registering telegram client: user_id={telegram_user_id}, phone={phone}")

            response = await self.client.post(
                f"{backend_url}/telegram/client/register",
                json={
                    "telegram_user_id": telegram_user_id,
                    "phone": phone,
                    "customer_name": customer_name,
                    "shop_id": shop_id,
                    "telegram_username": telegram_username,
                    "telegram_first_name": telegram_first_name,
                }
            )

            if response.status_code >= 500:
                raise NetworkError(f"Backend server error: HTTP {response.status_code}")

            response.raise_for_status()
            client_data = response.json()

            # Verify registration was successful (should have id field)
            if not client_data or "id" not in client_data:
                raise NetworkError("Backend registration returned invalid data (no 'id' field)")

            logger.info(f"Successfully registered telegram client: {telegram_user_id}, id={client_data.get('id')}")
            return client_data

        except httpx.HTTPError as e:
            logger.error(f"Backend registration failed: {e}. Trying MCP fallback...")

            # Fallback to MCP if available
            try:
                logger.info("Attempting MCP registration via fallback...")
                result = await self.call_tool("register_telegram_client", {
                    "telegram_user_id": telegram_user_id,
                    "phone": phone,
                    "customer_name": customer_name,
                    "shop_id": shop_id,
                    "telegram_username": telegram_username,
                    "telegram_first_name": telegram_first_name,
                })

                client_data = result.get("result", {})

                # Verify MCP registration was successful
                if not client_data or "id" not in client_data:
                    raise NetworkError("MCP registration returned invalid data (no 'id' field)")

                logger.info(f"MCP registration successful: {telegram_user_id}, id={client_data.get('id')}")
                return client_data

            except Exception as mcp_error:
                logger.error(f"MCP registration also failed: {mcp_error}")
                raise NetworkError(f"Registration failed (backend HTTP error: {e} / MCP error: {mcp_error})")

        except NetworkError:
            raise  # Re-raise our custom error
        except Exception as e:
            logger.error(f"Unexpected error in register_telegram_client: {e}")
            raise NetworkError(f"Unexpected registration error: {e}")


# Convenience function for creating client
def create_mcp_client(mcp_server_url: str) -> MCPClient:
    """Create and return MCP client instance."""
    return MCPClient(mcp_server_url)
