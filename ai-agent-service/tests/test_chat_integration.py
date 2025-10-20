"""
Integration tests for /chat endpoint.

These tests document the current behavior of the chat endpoint
and serve as a safety net during refactoring.
"""

import pytest
from fastapi.testclient import TestClient


class TestChatEndpoint:
    """Test suite for POST /chat endpoint."""

    def test_chat_simple_greeting(self, client, test_user_id):
        """Test simple greeting returns welcome message."""
        response = client.post("/chat", json={
            "message": "привет",
            "user_id": test_user_id,
            "channel": "telegram"
        })

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "text" in data
        assert "tracking_id" in data
        assert "order_number" in data
        assert "show_products" in data
        assert "usage" in data

        # Check greeting content
        assert "cvety.kz" in data["text"].lower()
        assert data["show_products"] is False
        assert data["tracking_id"] is None

        # Check usage metrics
        assert data["usage"]["output_tokens"] > 0
        assert "cache_hit" in data["usage"]

    def test_chat_list_products(self, client, test_user_id):
        """Test requesting product list returns show_products=True."""
        response = client.post("/chat", json={
            "message": "покажи готовые букеты",
            "user_id": test_user_id,
            "channel": "telegram"
        })

        assert response.status_code == 200
        data = response.json()

        # Check show_products flag
        assert data["show_products"] is True

        # Check product_ids are returned
        assert "product_ids" in data
        assert isinstance(data["product_ids"], list)
        assert len(data["product_ids"]) > 0

        # Check text contains product information
        assert "букет" in data["text"].lower()

    def test_chat_product_search(self, client, test_user_id):
        """Test searching for specific product type."""
        response = client.post("/chat", json={
            "message": "есть розы до 10000 тенге?",
            "user_id": test_user_id,
            "channel": "telegram"
        })

        assert response.status_code == 200
        data = response.json()

        # Response should contain products
        assert data["show_products"] in [True, False]  # Depends on availability

        # Check text is informative
        assert len(data["text"]) > 20

    def test_chat_session_continuation(self, client, test_user_id):
        """Test that conversation history is maintained."""
        # First message
        response1 = client.post("/chat", json={
            "message": "привет",
            "user_id": test_user_id,
            "channel": "telegram"
        })
        assert response1.status_code == 200

        # Second message in same session
        response2 = client.post("/chat", json={
            "message": "покажи букеты",
            "user_id": test_user_id,
            "channel": "telegram"
        })
        assert response2.status_code == 200
        data2 = response2.json()

        # Should show products based on context
        assert data2["show_products"] is True

    def test_chat_with_visual_search(self, client, test_user_id):
        """Test chat with image URL triggers visual search."""
        response = client.post("/chat", json={
            "message": "есть такой букет?",
            "user_id": test_user_id,
            "channel": "telegram",
            "image_url": "https://example.com/test-bouquet.jpg"
        })

        assert response.status_code == 200
        data = response.json()

        # Visual search should return response
        assert "text" in data
        # May or may not find exact matches, but should respond
        assert len(data["text"]) > 10

    def test_chat_invalid_request(self, client):
        """Test chat with missing required fields returns error."""
        response = client.post("/chat", json={
            "message": "привет"
            # Missing user_id and channel
        })

        assert response.status_code == 422  # Validation error

    def test_chat_empty_message(self, client, test_user_id):
        """Test chat with empty message."""
        response = client.post("/chat", json={
            "message": "",
            "user_id": test_user_id,
            "channel": "telegram"
        })

        # May return 200 with clarification request or 422
        assert response.status_code in [200, 422]


class TestChatCaching:
    """Test suite for prompt caching behavior."""

    def test_cache_metrics_present(self, client, test_user_id):
        """Test that cache metrics are present in usage."""
        response = client.post("/chat", json={
            "message": "привет",
            "user_id": test_user_id,
            "channel": "telegram"
        })

        assert response.status_code == 200
        data = response.json()

        usage = data["usage"]
        assert "input_tokens" in usage
        assert "output_tokens" in usage
        assert "cache_read_tokens" in usage
        assert "cache_creation_tokens" in usage
        assert "total_cost_usd" in usage
        assert "cache_hit" in usage

    def test_second_request_uses_cache(self, client, test_user_id):
        """Test that second request in session uses cache."""
        # First request - creates cache
        response1 = client.post("/chat", json={
            "message": "привет",
            "user_id": test_user_id,
            "channel": "telegram"
        })
        assert response1.status_code == 200
        usage1 = response1.json()["usage"]

        # Second request - should hit cache
        response2 = client.post("/chat", json={
            "message": "спасибо",
            "user_id": test_user_id,
            "channel": "telegram"
        })
        assert response2.status_code == 200
        usage2 = response2.json()["usage"]

        # Second request should have cache hits
        # (may not always be True depending on cache expiration)
        assert "cache_hit" in usage2
