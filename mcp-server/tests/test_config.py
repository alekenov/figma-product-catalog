"""
Unit tests for Config module.
Tests environment variable loading and validation.
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestConfig:
    """Test suite for Config module."""

    def test_config_has_api_base_url(self):
        """Test that Config has API_BASE_URL attribute."""
        from core.config import Config

        assert hasattr(Config, 'API_BASE_URL')
        assert isinstance(Config.API_BASE_URL, str)
        assert len(Config.API_BASE_URL) > 0

    def test_config_has_default_shop_id(self):
        """Test that Config has DEFAULT_SHOP_ID attribute."""
        from core.config import Config

        assert hasattr(Config, 'DEFAULT_SHOP_ID')
        assert isinstance(Config.DEFAULT_SHOP_ID, int)
        assert Config.DEFAULT_SHOP_ID > 0

    def test_config_has_timeout_settings(self):
        """Test that Config has timeout settings."""
        from core.config import Config

        assert hasattr(Config, 'REQUEST_TIMEOUT')
        assert isinstance(Config.REQUEST_TIMEOUT, float)
        assert Config.REQUEST_TIMEOUT > 0

    def test_config_has_retry_settings(self):
        """Test that Config has retry settings."""
        from core.config import Config

        assert hasattr(Config, 'MAX_RETRIES')
        assert isinstance(Config.MAX_RETRIES, int)
        assert Config.MAX_RETRIES >= 0

        assert hasattr(Config, 'RETRY_BACKOFF')
        assert isinstance(Config.RETRY_BACKOFF, float)

    def test_get_api_url_constructs_correctly(self):
        """Test that get_api_url constructs full URLs correctly."""
        from core.config import Config

        # Test with leading slash
        url = Config.get_api_url("/products")
        assert url.endswith("/products")
        assert Config.API_BASE_URL in url

        # Test without leading slash (should add it)
        url = Config.get_api_url("orders")
        assert url.endswith("/orders")

    def test_config_api_base_url_format(self):
        """Test that API_BASE_URL has correct format."""
        from core.config import Config

        # Should not end with slash (for consistent URL construction)
        assert not Config.API_BASE_URL.endswith("/")

        # Should start with http:// or https://
        assert Config.API_BASE_URL.startswith("http://") or \
               Config.API_BASE_URL.startswith("https://")

    def test_config_shop_id_positive(self):
        """Test that DEFAULT_SHOP_ID is positive."""
        from core.config import Config

        assert Config.DEFAULT_SHOP_ID > 0

    def test_config_log_level_valid(self):
        """Test that LOG_LEVEL is valid."""
        from core.config import Config

        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert Config.LOG_LEVEL.upper() in valid_levels


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
