"""
Kaspi Pay HTTP Client

Communicates with production PHP API on cvety.kz (185.125.90.141).
The production server has IP whitelist and mTLS certificates for Kaspi API.
"""
import httpx
import time
from typing import Dict, Any, Optional
from config import settings


class KaspiClientError(Exception):
    """Base exception for Kaspi client errors"""
    pass


class KaspiClient:
    """HTTP client for Kaspi Pay via production API proxy"""

    def __init__(self):
        self.base_url = settings.production_api_url
        self.access_token = settings.kaspi_access_token
        self.timeout = settings.kaspi_api_timeout
        self.max_retries = settings.kaspi_max_retries
        self.retry_delay = settings.kaspi_retry_delay
        self.client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)

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
            endpoint: API endpoint (create, status, refund)
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            Response data dictionary

        Raises:
            KaspiClientError: On API errors or max retries exceeded
        """
        url = f"{self.base_url}/{endpoint}/"

        # Add access_token to params
        request_params = {"access_token": self.access_token}
        if params:
            request_params.update(params)

        try:
            response = await self.client.request(method, url, params=request_params)
            response.raise_for_status()

            # Handle empty responses (production refund returns empty body)
            if not response.content or len(response.content) == 0:
                return {"status": True, "data": {}}

            data = response.json()
            return data

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            # Retry on network errors
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay)
                return await self._make_request(method, endpoint, params, retry_count + 1)

            raise KaspiClientError(f"Max retries exceeded: {str(e)}")

    async def create_payment(
        self,
        phone: str,
        amount: float,
        message: str,
        organization_bin: str,
        device_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create remote payment request

        Args:
            phone: Customer phone number (e.g., "77015211545")
            amount: Payment amount in tenge
            message: Payment description
            organization_bin: Organization BIN (12 digits)
            device_token: Kaspi TradePointId (optional, required for multi-БИН setups)

        Returns:
            Response data with externalId (QrPaymentId)

        Raises:
            KaspiClientError: On API errors

        Example:
            >>> await client.create_payment("77015211545", 100, "Order #123", "891027350515", "1454711")
            {
                "status": True,
                "data": {
                    "externalId": "12345678901",
                    "status": "Wait"
                }
            }
        """
        params = {
            "phone": phone,
            "amount": str(amount),
            "message": message,
            "organizationBin": organization_bin
        }

        # Add device token if provided
        if device_token:
            params["deviceToken"] = device_token

        response = await self._make_request("GET", "create", params=params)

        # Check status
        if not response.get("status", response.get("success", False)):
            # Parse error
            errors_dict = response.get("data", {}).get("errors", {})
            if errors_dict:
                error_code = list(errors_dict.keys())[0]
                error_msg = errors_dict[error_code]
                error = f"{error_msg} (code: {error_code})"
            else:
                error = response.get("error", "Unknown error")

            raise KaspiClientError(f"Failed to create payment: {error}")

        return response

    async def check_status(self, external_id: str) -> Dict[str, Any]:
        """
        Check payment status

        Args:
            external_id: QrPaymentId from create_payment

        Returns:
            Response data with status (Wait/Processed/Error)

        Example:
            >>> await client.check_status("12345678901")
            {
                "status": True,
                "data": {
                    "status": "Processed",
                    "externalId": "12345678901"
                }
            }
        """
        response = await self._make_request("GET", "status", params={"externalId": external_id})

        if not response.get("status", response.get("success", False)):
            error = response.get("error", "Unknown error")
            raise KaspiClientError(f"Failed to check status: {error}")

        return response

    async def refund(self, external_id: str, amount: float, organization_bin: str) -> Dict[str, Any]:
        """
        Refund payment (full or partial)

        Args:
            external_id: QrPaymentId from create_payment
            amount: Amount to refund in tenge
            organization_bin: Organization BIN (must match payment's BIN)

        Returns:
            Response data with refund status

        Raises:
            KaspiClientError: On API errors

        Example:
            >>> await client.refund("12345678901", 50, "891027350515")
            {
                "status": True,
                "data": {
                    "status": "success"
                }
            }
        """
        params = {
            "externalId": external_id,
            "amount": str(amount),
            "organizationBin": organization_bin
        }

        response = await self._make_request("GET", "refund", params=params)

        if not response.get("status", response.get("success", False)):
            # Parse error
            errors_dict = response.get("data", {}).get("errors", {})
            if errors_dict:
                error_code = list(errors_dict.keys())[0]
                error_msg = errors_dict[error_code]
                error = f"{error_msg} (code: {error_code})"
            else:
                error = response.get("error", "Unknown error")

            raise KaspiClientError(f"Failed to refund: {error}")

        return response


# Global client instance
_kaspi_client: Optional[KaspiClient] = None


def get_kaspi_client() -> KaspiClient:
    """Get or create global Kaspi client instance"""
    global _kaspi_client
    if _kaspi_client is None:
        _kaspi_client = KaspiClient()
    return _kaspi_client
