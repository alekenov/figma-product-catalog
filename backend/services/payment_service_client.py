"""
Payment Service Client - HTTP client for payment-service microservice

This client communicates with payment-service for automatic БИН routing.
Includes retry logic and fallback to kaspi_pay_service for resilience.
"""
import httpx
import asyncio
import os
from typing import Dict, Any, Optional
from core.logging import get_logger

# Import settings
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings

logger = get_logger(__name__)


class PaymentServiceError(Exception):
    """Base exception for payment service errors"""
    pass


class PaymentServiceClient:
    """
    HTTP client for payment-service microservice

    Features:
    - Automatic БИН routing by shop_id
    - Retry with exponential backoff
    - Fallback to kaspi_pay_service on failure
    """

    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1  # seconds
    TIMEOUT = 30  # seconds

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize payment service client

        Args:
            base_url: Payment service base URL (defaults to settings)
        """
        self.base_url = base_url or settings.payment_service_url
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT, follow_redirects=True)
        self._fallback_service = None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def _get_fallback_service(self):
        """Get kaspi_pay_service for fallback (lazy initialization)"""
        if self._fallback_service is None:
            from services.kaspi_pay_service import get_kaspi_service
            self._fallback_service = get_kaspi_service()
        return self._fallback_service

    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry

        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint path
            json_data: JSON body for POST requests
            params: Query parameters for GET requests
            retry_count: Current retry attempt

        Returns:
            Response data dictionary

        Raises:
            PaymentServiceError: On API errors after max retries
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.info(
                "payment_service_request",
                method=method,
                endpoint=endpoint,
                attempt=retry_count + 1
            )

            if method == "POST":
                response = await self.client.post(url, json=json_data)
            else:
                response = await self.client.get(url, params=params)

            response.raise_for_status()
            data = response.json()

            logger.info(
                "payment_service_response",
                endpoint=endpoint,
                success=data.get("success", False),
                status_code=response.status_code
            )

            return data

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            logger.warning(
                "payment_service_request_error",
                endpoint=endpoint,
                error=str(e),
                attempt=retry_count + 1
            )

            # Retry with exponential backoff
            if retry_count < self.MAX_RETRIES:
                delay = self.INITIAL_RETRY_DELAY * (2 ** retry_count)
                logger.info(
                    "payment_service_retry",
                    endpoint=endpoint,
                    attempt=retry_count + 2,
                    delay=delay
                )
                await asyncio.sleep(delay)
                return await self._make_request_with_retry(
                    method, endpoint, json_data, params, retry_count + 1
                )

            # Max retries exceeded
            raise PaymentServiceError(f"Payment service unavailable after {self.MAX_RETRIES} retries: {str(e)}")

    async def create_payment(
        self,
        shop_id: int,
        phone: str,
        amount: float,
        message: str,
        use_fallback_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Create payment with automatic БИН routing

        Args:
            shop_id: Shop ID for БИН routing
            phone: Customer phone number (e.g., "77015211545")
            amount: Payment amount in tenge
            message: Payment description
            use_fallback_on_error: Fallback to kaspi_pay_service on failure

        Returns:
            Response data with external_id and organization_bin

        Example:
            >>> await client.create_payment(8, "77015211545", 100, "Order #123")
            {
                "success": True,
                "external_id": "12345678901",
                "status": "Wait",
                "organization_bin": "891027350515"
            }
        """
        logger.info(
            "payment_service_create_payment",
            shop_id=shop_id,
            phone=phone,
            amount=amount,
            message=message
        )

        try:
            response = await self._make_request_with_retry(
                "POST",
                "/payments/kaspi/create",
                json_data={
                    "shop_id": shop_id,
                    "phone": phone,
                    "amount": amount,
                    "message": message
                }
            )

            if not response.get("success"):
                error = response.get("error", "Unknown error")
                raise PaymentServiceError(f"Payment creation failed: {error}")

            external_id = response.get("external_id")
            organization_bin = response.get("organization_bin")

            logger.info(
                "payment_created_via_service",
                shop_id=shop_id,
                external_id=external_id,
                organization_bin=organization_bin
            )

            return response

        except PaymentServiceError as e:
            logger.error(
                "payment_service_failed",
                shop_id=shop_id,
                error=str(e),
                fallback_enabled=use_fallback_on_error
            )

            # Try fallback to kaspi_pay_service
            if use_fallback_on_error:
                logger.warning(
                    "payment_service_fallback_triggered",
                    shop_id=shop_id
                )

                try:
                    fallback_service = self._get_fallback_service()
                    fallback_response = await fallback_service.create_payment(
                        phone=phone,
                        amount=amount,
                        message=message
                    )

                    logger.info(
                        "payment_created_via_fallback",
                        shop_id=shop_id,
                        external_id=fallback_response.get("data", {}).get("externalId")
                    )

                    # Transform fallback response to match payment-service format
                    return {
                        "success": fallback_response.get("status", fallback_response.get("success", False)),
                        "external_id": str(fallback_response.get("data", {}).get("externalId")),
                        "status": fallback_response.get("data", {}).get("status"),
                        "organization_bin": None,  # Fallback doesn't return БИН
                        "fallback_used": True
                    }

                except Exception as fallback_error:
                    logger.error(
                        "payment_fallback_also_failed",
                        shop_id=shop_id,
                        error=str(fallback_error)
                    )
                    raise PaymentServiceError(f"Both payment-service and fallback failed: {str(e)}, {str(fallback_error)}")

            raise

    async def check_status(self, external_id: str) -> Dict[str, Any]:
        """
        Check payment status

        Args:
            external_id: Payment ID from create_payment

        Returns:
            Response data with status (Wait/Processed/Error)

        Example:
            >>> await client.check_status("12345678901")
            {
                "success": True,
                "external_id": "12345678901",
                "status": "Processed"
            }
        """
        logger.info("payment_service_check_status", external_id=external_id)

        try:
            response = await self._make_request_with_retry(
                "GET",
                f"/payments/kaspi/status",
                params={"external_id": external_id}
            )

            if not response.get("success"):
                error = response.get("error", "Unknown error")
                raise PaymentServiceError(f"Status check failed: {error}")

            status = response.get("status")
            logger.info("payment_status_checked", external_id=external_id, status=status)

            return response

        except PaymentServiceError as e:
            logger.error("payment_service_status_failed", external_id=external_id, error=str(e))
            raise

    async def refund(
        self,
        shop_id: int,
        external_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Refund payment (full or partial)

        Args:
            shop_id: Shop ID (for БИН routing)
            external_id: Payment ID from create_payment
            amount: Amount to refund in tenge

        Returns:
            Response data with refund status

        Example:
            >>> await client.refund(8, "12345678901", 50)
            {
                "success": True,
                "external_id": "12345678901",
                "refunded_amount": 50
            }
        """
        logger.info(
            "payment_service_refund",
            shop_id=shop_id,
            external_id=external_id,
            amount=amount
        )

        try:
            response = await self._make_request_with_retry(
                "POST",
                "/payments/kaspi/refund",
                json_data={
                    "shop_id": shop_id,
                    "external_id": external_id,
                    "amount": amount
                }
            )

            if not response.get("success"):
                error = response.get("error", "Unknown error")
                raise PaymentServiceError(f"Refund failed: {error}")

            logger.info("payment_refunded", external_id=external_id, amount=amount)

            return response

        except PaymentServiceError as e:
            logger.error(
                "payment_service_refund_failed",
                external_id=external_id,
                error=str(e)
            )
            raise


# Global service instance
_payment_service_client: Optional[PaymentServiceClient] = None


def get_payment_service_client() -> PaymentServiceClient:
    """Get or create global payment service client instance"""
    global _payment_service_client
    if _payment_service_client is None:
        _payment_service_client = PaymentServiceClient()
    return _payment_service_client
