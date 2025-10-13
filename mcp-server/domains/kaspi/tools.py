"""
Kaspi Pay tools for MCP server.

Provides AI assistants with payment management capabilities via Kaspi Pay.
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

from core.api_client import api_client
from core.registry import ToolRegistry

# Note: mcp instance is imported from server.py during registration
mcp = None  # Will be set during initialization


def init_mcp(mcp_instance: FastMCP):
    """Initialize MCP instance for this module."""
    global mcp
    mcp = mcp_instance


@ToolRegistry.register(domain="kaspi", requires_auth=False, is_public=True)
async def kaspi_create_payment(
    phone: str,
    amount: float,
    message: str
) -> Dict[str, Any]:
    """
    Create a new Kaspi Pay remote payment request.

    Creates a payment request that customer can pay via Kaspi mobile app.
    The customer will receive a push notification and can complete payment instantly.

    Args:
        phone: Customer phone number in Kazakhstan format (e.g., "77015211545")
        amount: Payment amount in tenge (KZT), must be > 0
        message: Payment description shown to customer (e.g., "Order #123")

    Returns:
        Dictionary with:
        - success: bool - whether payment was created
        - external_id: str - QrPaymentId for tracking
        - status: str - initial payment status (usually "Wait")
        - error: str (optional) - error message if failed

    Example:
        kaspi_create_payment(
            phone="77015211545",
            amount=100,
            message="Flower order #123"
        )

    Response:
        {
            "success": true,
            "external_id": "12345678901",
            "status": "Wait"
        }

    Note:
        Use kaspi_check_payment_status with returned external_id to monitor payment.
    """
    result = await api_client.post(
        endpoint="/kaspi/create",
        json_data={
            "phone": phone,
            "amount": amount,
            "message": message
        }
    )
    return result


@ToolRegistry.register(domain="kaspi", requires_auth=False, is_public=True)
async def kaspi_check_payment_status(external_id: str) -> Dict[str, Any]:
    """
    Check status of a Kaspi Pay payment.

    Query current payment status by external_id (QrPaymentId).
    Useful for polling until payment is completed.

    Args:
        external_id: QrPaymentId from kaspi_create_payment

    Returns:
        Dictionary with:
        - success: bool - whether check was successful
        - external_id: str - the queried payment ID
        - status: str - payment status:
            * "Wait" - waiting for customer to pay
            * "Processed" - payment completed successfully
            * "Error" - payment failed
        - error: str (optional) - error message if failed

    Example:
        kaspi_check_payment_status(external_id="12345678901")

    Response:
        {
            "success": true,
            "external_id": "12345678901",
            "status": "Processed"
        }

    Tip:
        Poll this endpoint every 5-10 seconds while status is "Wait".
    """
    result = await api_client.get(
        endpoint=f"/kaspi/status/{external_id}"
    )
    return result


@ToolRegistry.register(domain="kaspi", requires_auth=False, is_public=True)
async def kaspi_get_payment_details(external_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a Kaspi Pay payment.

    Retrieve payment details including total amount and available refund amount.
    IMPORTANT: Always call this before attempting a refund to check available_return_amount.

    Args:
        external_id: QrPaymentId from kaspi_create_payment

    Returns:
        Dictionary with:
        - success: bool - whether details were retrieved
        - total_amount: float - total payment amount in tenge
        - available_return_amount: float - amount available for refund
        - transaction_date: str - transaction timestamp
        - product_type: str - Kaspi product type
        - error: str (optional) - error message if failed

    Example:
        kaspi_get_payment_details(external_id="12345678901")

    Response:
        {
            "success": true,
            "total_amount": 100,
            "available_return_amount": 100,
            "transaction_date": "2025-01-12T10:30:00",
            "product_type": "RemotePayment"
        }

    Note:
        If available_return_amount is 0, the payment has been fully refunded.
        If it's less than total_amount, partial refunds have been made.
    """
    result = await api_client.get(
        endpoint=f"/kaspi/details/{external_id}"
    )
    return result


@ToolRegistry.register(domain="kaspi", requires_auth=False, is_public=True)
async def kaspi_refund_payment(
    external_id: str,
    amount: float
) -> Dict[str, Any]:
    """
    Refund a Kaspi Pay payment (full or partial).

    Return money to customer's Kaspi account. Supports partial refunds.

    IMPORTANT:
    - The system automatically checks available_return_amount before refunding
    - If insufficient funds, returns error 400 with detailed message
    - Duplicate refund attempts are prevented to avoid error -99000005

    Args:
        external_id: QrPaymentId from kaspi_create_payment
        amount: Amount to refund in tenge (must be ≤ available_return_amount)

    Returns:
        Dictionary with:
        - success: bool - whether refund was successful
        - external_id: str - the refunded payment ID
        - refunded_amount: float - amount successfully refunded
        - error: str (optional) - error message if failed

    Example:
        kaspi_refund_payment(
            external_id="12345678901",
            amount=50
        )

    Response (success):
        {
            "success": true,
            "external_id": "12345678901",
            "refunded_amount": 50
        }

    Response (insufficient funds):
        {
            "success": false,
            "error": "Insufficient funds for refund. Available: 0 тг, Requested: 50 тг"
        }

    Best Practice:
        1. Call kaspi_get_payment_details first to check available_return_amount
        2. Ensure amount ≤ available_return_amount
        3. Call kaspi_refund_payment
        4. Handle errors gracefully

    Note:
        Refunds typically process instantly but may take up to 24 hours to appear
        in customer's account depending on Kaspi's processing.
    """
    result = await api_client.post(
        endpoint="/kaspi/refund",
        json_data={
            "external_id": external_id,
            "amount": amount
        }
    )
    return result
