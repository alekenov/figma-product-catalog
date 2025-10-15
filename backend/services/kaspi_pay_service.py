"""
Kaspi Pay Service - HTTP client for production PHP endpoints

This service wraps calls to cvety.kz production Kaspi Pay API endpoints.
The production server has IP whitelist access to Kaspi API with mTLS certificates.
"""
import httpx
import time
import os
from typing import Dict, Any, Optional
from core.logging import get_logger

# Import settings (works with both Render and SQLite configs)
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings

logger = get_logger(__name__)


class KaspiPayServiceError(Exception):
    """Base exception for Kaspi Pay service errors"""
    pass


class KaspiPayService:
    """Service for interacting with Kaspi Pay via production PHP endpoints"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self, timeout: int = 30):
        """
        Initialize Kaspi Pay service

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint path
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            Response data dictionary

        Raises:
            KaspiPayServiceError: On API errors or max retries exceeded
        """
        url = f"{settings.kaspi_api_base_url}/{endpoint}/"

        # Add access_token to params
        request_params = {"access_token": settings.kaspi_access_token}
        if params:
            request_params.update(params)

        try:
            logger.info(
                "kaspi_request",
                method=method,
                endpoint=endpoint,
                params={k: v for k, v in request_params.items() if k != "access_token"},
                attempt=retry_count + 1
            )

            response = await self.client.request(method, url, params=request_params)
            response.raise_for_status()

            # Handle empty responses (production refund returns empty body)
            if not response.content or len(response.content) == 0:
                logger.warning(
                    "kaspi_empty_response",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type")
                )
                # Return success for empty response (refund case)
                return {"status": True, "data": {}}

            data = response.json()

            # Production API returns "status" not "success"
            success_status = data.get("status", data.get("success", False))

            logger.info(
                "kaspi_response",
                endpoint=endpoint,
                success=success_status,
                status_code=response.status_code
            )

            return data

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            logger.error(
                "kaspi_request_error",
                endpoint=endpoint,
                error=str(e),
                attempt=retry_count + 1
            )

            # Retry on network errors
            if retry_count < self.MAX_RETRIES:
                logger.info(
                    "kaspi_retry",
                    endpoint=endpoint,
                    attempt=retry_count + 2,
                    delay=self.RETRY_DELAY
                )
                time.sleep(self.RETRY_DELAY)
                return await self._make_request(method, endpoint, params, retry_count + 1)

            raise KaspiPayServiceError(f"Max retries exceeded: {str(e)}")

    async def create_payment(
        self,
        phone: str,
        amount: float,
        message: str
    ) -> Dict[str, Any]:
        """
        Create remote payment request

        Args:
            phone: Customer phone number (e.g., "77015211545")
            amount: Payment amount in tenge
            message: Payment description

        Returns:
            Response data with externalId (QrPaymentId)

        Example:
            >>> await service.create_payment("77015211545", 100, "Order #123")
            {
                "success": True,
                "data": {
                    "externalId": "12345678901",
                    "status": "Wait"
                }
            }
        """
        logger.info(
            "kaspi_create_payment",
            phone=phone,
            amount=amount,
            message=message
        )

        response = await self._make_request(
            "GET",
            "create",
            params={
                "phone": phone,
                "amount": str(amount),
                "message": message
            }
        )

        # Check status (production API returns "status": true/false)
        if not response.get("status", response.get("success", False)):
            # Parse error from data.errors dict or fall back to error field
            errors_dict = response.get("data", {}).get("errors", {})
            if errors_dict:
                # Get first error message from errors dict
                error_code = list(errors_dict.keys())[0]
                error_msg = errors_dict[error_code]
                error = f"{error_msg} (code: {error_code})"
            else:
                error = response.get("error", "Unknown error")

            logger.error("kaspi_create_payment_failed", error=error, response=response)
            raise KaspiPayServiceError(f"Failed to create payment: {error}")

        external_id = response.get("data", {}).get("externalId")
        logger.info("kaspi_payment_created", external_id=external_id)

        return response

    async def check_status(self, external_id: str) -> Dict[str, Any]:
        """
        Check payment status

        Args:
            external_id: QrPaymentId from create_payment

        Returns:
            Response data with status (Wait/Processed/Error)

        Example:
            >>> await service.check_status("12345678901")
            {
                "success": True,
                "data": {
                    "status": "Processed",
                    "externalId": "12345678901"
                }
            }
        """
        logger.info("kaspi_check_status", external_id=external_id)

        response = await self._make_request(
            "GET",
            "status",
            params={"externalId": external_id}
        )

        # Check status (production API returns "status": true/false)
        if not response.get("status", response.get("success", False)):
            error = response.get("error", "Unknown error")
            logger.error("kaspi_check_status_failed", error=error, external_id=external_id)
            raise KaspiPayServiceError(f"Failed to check status: {error}")

        status = response.get("data", {}).get("status")
        logger.info("kaspi_status_checked", external_id=external_id, status=status)

        return response

    # NOTE: get_details() method removed because /details/ endpoint doesn't exist
    # on production API (cvety.kz/api/v2/paymentkaspi/ returns 404 for /details/)
    # Production API only supports: create, status, refund

    async def refund(self, external_id: str, amount: float) -> Dict[str, Any]:
        """
        Refund payment (full or partial)

        NOTE: Does NOT pre-check AvailableReturnAmount (matching production PHP behavior).
        Kaspi API will return error if refund amount exceeds available amount.

        Args:
            external_id: QrPaymentId from create_payment
            amount: Amount to refund in tenge

        Returns:
            Response data with refund status

        Raises:
            KaspiPayServiceError: On API errors (including insufficient funds)

        Example:
            >>> await service.refund("12345678901", 50)
            {
                "success": True,
                "data": {
                    "status": "success",
                    "refunded_amount": 50
                }
            }
        """
        logger.info("kaspi_refund_start", external_id=external_id, amount=amount)

        response = await self._make_request(
            "GET",
            "refund",
            params={
                "externalId": external_id,
                "amount": str(amount)
            }
        )

        # Check status (production API returns "status": true/false)
        if not response.get("status", response.get("success", False)):
            # Parse error from data.errors dict or fall back to error field
            errors_dict = response.get("data", {}).get("errors", {})
            if errors_dict:
                # Get first error message from errors dict
                error_code = list(errors_dict.keys())[0]
                error_msg = errors_dict[error_code]
                error = f"{error_msg} (code: {error_code})"
            else:
                error = response.get("error", "Unknown error")

            logger.error(
                "kaspi_refund_failed",
                external_id=external_id,
                amount=amount,
                error=error
            )
            raise KaspiPayServiceError(f"Failed to refund: {error}")

        logger.info(
            "kaspi_refund_success",
            external_id=external_id,
            amount=amount
        )

        return response


# Global service instance
_kaspi_service: Optional[KaspiPayService] = None


def get_kaspi_service() -> KaspiPayService:
    """Get or create global Kaspi Pay service instance"""
    global _kaspi_service
    if _kaspi_service is None:
        _kaspi_service = KaspiPayService()
    return _kaspi_service
