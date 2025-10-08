"""
Delivery validation logic for MCP server.

NOTE: Date/time parsing has been moved to backend API (POST /delivery/parse).
This module now only contains validation logic that wraps backend API calls.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DeliveryValidator:
    """
    Validates delivery feasibility against shop constraints.

    Checks:
    - Shop working hours
    - Preparation time requirements
    - Delivery time windows
    """

    def __init__(self, api_client):
        """
        Initialize validator with API client.

        Args:
            api_client: APIClient instance for checking feasibility
        """
        self.api_client = api_client

    async def validate_feasibility(
        self,
        shop_id: int,
        delivery_datetime: str,
        product_ids: str,
    ) -> Dict[str, Any]:
        """
        Check if delivery is feasible at requested time.

        Args:
            shop_id: Shop ID
            delivery_datetime: ISO 8601 datetime string
            product_ids: Comma-separated product IDs

        Returns:
            Dictionary with:
            - is_feasible: bool
            - earliest_delivery: str (if not feasible)
            - reason: str (if not feasible)
        """
        # Extract date from datetime for API call
        delivery_date = delivery_datetime.split("T")[0]

        try:
            result = await self.api_client.get(
                endpoint="/delivery/feasibility",
                params={
                    "shop_id": shop_id,
                    "delivery_date": delivery_date,
                    "product_ids": product_ids,
                },
            )
            return result
        except Exception as e:
            logger.error(f"Delivery feasibility check failed: {e}")
            # Return permissive result to not block orders on validation errors
            return {
                "is_feasible": True,
                "reason": "Could not validate (error)",
            }

    async def validate_exact_time(
        self,
        shop_id: int,
        delivery_datetime: str,
        product_ids: str,
    ) -> Dict[str, Any]:
        """
        Validate exact delivery time against all constraints.

        Args:
            shop_id: Shop ID
            delivery_datetime: ISO 8601 datetime string
            product_ids: Comma-separated product IDs

        Returns:
            Dictionary with:
            - is_valid: bool
            - delivery_time: str
            - reason: str (if not valid)
            - alternative_slots: List[Dict] (if not valid)
        """
        try:
            result = await self.api_client.post(
                endpoint="/delivery/validate",
                json_data={},  # Backend uses query params for this endpoint
                params={
                    "shop_id": shop_id,
                    "delivery_time": delivery_datetime,
                    "product_ids": product_ids,
                },
            )
            return result
        except Exception as e:
            logger.error(f"Delivery time validation failed: {e}")
            # Return permissive result
            return {
                "is_valid": True,
                "delivery_time": delivery_datetime,
                "reason": "Could not validate (error)",
            }


def format_delivery_error(
    feasibility: Dict[str, Any],
    requested_time: str,
) -> Dict[str, str]:
    """
    Format delivery validation error response.

    Args:
        feasibility: Result from validate_feasibility
        requested_time: Originally requested delivery time

    Returns:
        Structured error response for customer
    """
    earliest = feasibility.get("earliest_delivery", "")
    reason = feasibility.get("reason", "Доставка в указанное время невозможна")

    return {
        "error": "delivery_time_impossible",
        "message": f"{reason}. Ближайшее доступное время: {earliest}",
        "requested_time": requested_time,
        "earliest_available": earliest,
        "suggestion": "Пожалуйста, выберите другое время или используйте предложенное.",
    }
