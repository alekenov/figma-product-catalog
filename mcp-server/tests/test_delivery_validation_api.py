"""
Regression tests for delivery validation API endpoints.

Tests that were added after fixing the missing json_data bug in:
- domains/orders/delivery.py:276 (DeliveryValidator.validate_exact_time)
- domains/shop/tools.py:149 (validate_delivery_time)

These tests ensure that the api_client.post() calls include the required
json_data parameter and don't raise TypeError.
"""
import pytest
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add parent directory to path (mcp-server/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domains.shop.tools import (
    validate_delivery_time,
    check_delivery_feasibility,
    get_delivery_slots
)
from domains.orders.delivery import DeliveryValidator
from core.api_client import api_client


class TestDeliveryValidationAPI:
    """Regression tests for delivery validation API calls."""

    @pytest.mark.asyncio
    async def test_validate_delivery_time_includes_json_data(self):
        """
        Test that validate_delivery_time() calls api_client.post() with json_data.

        Regression test for bug where json_data was omitted, causing:
        TypeError: APIClient.post() missing 1 required positional argument: 'json_data'
        """
        with patch.object(api_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "is_valid": True,
                "delivery_time": "2025-01-15T14:00:00"
            }

            # Call the fixed function
            result = await validate_delivery_time(
                shop_id=8,
                delivery_time="2025-01-15T14:00:00",
                product_ids="1,2,3"
            )

            # Verify api_client.post() was called with json_data argument
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Check that json_data was provided (not missing)
            assert 'json_data' in call_args.kwargs or len(call_args.args) >= 2

            # Verify the result
            assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_check_delivery_feasibility_includes_json_data(self):
        """
        Test that check_delivery_feasibility() calls api_client.get() correctly.
        Note: This endpoint uses GET, not POST.
        """
        with patch.object(api_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "is_feasible": True,
                "earliest_delivery": "2025-01-15T14:00:00"
            }

            # Call the function
            result = await check_delivery_feasibility(
                shop_id=8,
                delivery_date="2025-01-15",
                product_ids="1,2,3"
            )

            # Verify api_client.get() was called
            mock_get.assert_called_once()

            # Verify the result
            assert result["is_feasible"] is True

    @pytest.mark.asyncio
    async def test_get_delivery_slots_includes_json_data(self):
        """
        Test that get_delivery_slots() calls api_client.get() correctly.
        Note: This endpoint uses GET, not POST.
        """
        with patch.object(api_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                {"start_time": "14:00", "end_time": "16:00", "available": True}
            ]

            # Call the function
            result = await get_delivery_slots(
                shop_id=8,
                date="2025-01-15",
                product_ids="1,2,3"
            )

            # Verify api_client.get() was called
            mock_get.assert_called_once()

            # Verify the result
            assert len(result) > 0
            assert result[0]["available"] is True

    @pytest.mark.asyncio
    async def test_delivery_validator_validate_exact_time_includes_json_data(self):
        """
        Test that DeliveryValidator.validate_exact_time() calls api_client.post() with json_data.

        This was the original bug location: domains/orders/delivery.py:276
        """
        validator = DeliveryValidator(api_client)

        with patch.object(api_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "is_valid": True,
                "delivery_time": "2025-01-15T14:00:00"
            }

            # Call the fixed method
            result = await validator.validate_exact_time(
                shop_id=8,
                delivery_datetime="2025-01-15T14:00:00",
                product_ids="1,2,3"
            )

            # Verify api_client.post() was called with json_data
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # The key assertion: json_data must be present
            assert 'json_data' in call_args.kwargs or len(call_args.args) >= 2

            # Verify endpoint and params (handle both positional and keyword args)
            if len(call_args.args) > 0:
                assert call_args.args[0] == "/delivery/validate"
            else:
                assert call_args.kwargs.get("endpoint") == "/delivery/validate"

            assert "params" in call_args.kwargs
            assert call_args.kwargs["params"]["shop_id"] == 8

            # Verify the result
            assert result["is_valid"] is True
