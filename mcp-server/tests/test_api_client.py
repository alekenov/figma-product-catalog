"""
Unit tests for APIClient.
Tests exception mapping, retry logic, and error handling.
"""
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.api_client import APIClient
from core.exceptions import (
    NotFoundError,
    ValidationError,
    AuthenticationError,
    PermissionError,
    RateLimitError,
    ServerError,
    APIError
)


class TestAPIClient:
    """Test suite for APIClient HTTP client."""

    @pytest.mark.asyncio
    async def test_exception_mapping_404(self):
        """Test that 404 status code maps to NotFoundError."""
        client = APIClient()

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Product not found"

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            with pytest.raises(NotFoundError):
                await client.get("/products/999")

    @pytest.mark.asyncio
    async def test_exception_mapping_422(self):
        """Test that 422 status code maps to ValidationError."""
        client = APIClient()

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.text = "Invalid input"

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            with pytest.raises(ValidationError):
                await client.post("/products/", json_data={"invalid": "data"})

    @pytest.mark.asyncio
    async def test_exception_mapping_401(self):
        """Test that 401 status code maps to AuthenticationError."""
        client = APIClient()

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            with pytest.raises(AuthenticationError):
                await client.get("/auth/me")

    @pytest.mark.asyncio
    async def test_exception_mapping_403(self):
        """Test that 403 status code maps to PermissionError."""
        client = APIClient()

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.text = "Forbidden"

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            with pytest.raises(PermissionError):
                await client.get("/admin/users")

    @pytest.mark.asyncio
    async def test_exception_mapping_500(self):
        """Test that 500 status code maps to ServerError."""
        client = APIClient()

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            with pytest.raises(ServerError):
                await client.get("/products/")

    @pytest.mark.asyncio
    async def test_successful_get_request(self):
        """Test successful GET request returns JSON."""
        client = APIClient()
        expected_data = {"id": 1, "name": "Test Product"}

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_data

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            result = await client.get("/products/1")
            assert result == expected_data

    @pytest.mark.asyncio
    async def test_successful_post_request(self):
        """Test successful POST request with JSON data."""
        client = APIClient()
        request_data = {"name": "New Product", "price": 1000}
        expected_data = {"id": 123, **request_data}

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = expected_data

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            result = await client.post("/products/", json_data=request_data)
            assert result == expected_data

    @pytest.mark.asyncio
    async def test_auth_token_header(self):
        """Test that auth token is added to headers."""
        client = APIClient()
        token = "test_token_123"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": "test"}

            mock_context = AsyncMock()
            mock_request = mock_context.__aenter__.return_value.request
            mock_request.return_value = mock_response
            mock_client.return_value = mock_context

            await client.get("/auth/me", token=token)

            # Verify Authorization header was set
            call_kwargs = mock_request.call_args[1]
            assert "Authorization" in call_kwargs.get("headers", {})
            assert call_kwargs["headers"]["Authorization"] == f"Bearer {token}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
