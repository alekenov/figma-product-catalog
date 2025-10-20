"""
Kaspi Pay API Endpoints

REST API for Kaspi Pay payment operations.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError
from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/kaspi", tags=["Kaspi Pay"])


# ==================== Request Models ====================

class CreatePaymentRequest(BaseModel):
    """Request to create a new payment"""
    phone: str = Field(..., description="Customer phone number (e.g., 77015211545)")
    amount: float = Field(..., gt=0, description="Payment amount in tenge")
    message: str = Field(..., description="Payment description")
    organization_bin: Optional[str] = Field(None, description="Organization BIN (defaults to configured BIN if not provided)")

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "77015211545",
                "amount": 100,
                "message": "Order #123 payment",
                "organization_bin": "210440028324"
            }
        }


class RefundRequest(BaseModel):
    """Request to refund a payment"""
    external_id: str = Field(..., description="QrPaymentId from create payment")
    amount: float = Field(..., gt=0, description="Amount to refund in tenge")
    organization_bin: Optional[str] = Field(None, description="Organization BIN (must match payment's BIN)")

    class Config:
        json_schema_extra = {
            "example": {
                "external_id": "12345678901",
                "amount": 50,
                "organization_bin": "210440028324"
            }
        }


# ==================== Response Models ====================

class CreatePaymentResponse(BaseModel):
    """Response from create payment"""
    success: bool
    external_id: Optional[str] = Field(None, description="QrPaymentId for tracking")
    status: Optional[str] = Field(None, description="Initial payment status")
    error: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    """Response from check status"""
    success: bool
    external_id: str
    status: Optional[str] = Field(None, description="Wait / Processed / Error")
    error: Optional[str] = None


# PaymentDetailsResponse removed - /details/ endpoint doesn't exist on production


class RefundResponse(BaseModel):
    """Response from refund"""
    success: bool
    external_id: str
    refunded_amount: float
    error: Optional[str] = None


# ==================== Endpoints ====================

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(request: CreatePaymentRequest):
    """
    Create a new Kaspi Pay remote payment

    Creates a payment request that customer can pay via Kaspi mobile app.
    Returns externalId (QrPaymentId) for tracking payment status.

    **Args:**
    - **phone**: Customer phone number (e.g., 77015211545)
    - **amount**: Payment amount in tenge (must be > 0)
    - **message**: Payment description for customer
    - **organization_bin**: Optional BIN to override default (e.g., 210440028324)

    **Returns:**
    - **external_id**: QrPaymentId for status tracking
    - **status**: Initial payment status (usually "Wait")

    **Example:**
    ```json
    {
        "phone": "77015211545",
        "amount": 100,
        "message": "Order #123",
        "organization_bin": "210440028324"
    }
    ```
    """
    logger.info(
        "kaspi_api_create_payment",
        phone=request.phone,
        amount=request.amount,
        message=request.message,
        organization_bin=request.organization_bin
    )

    try:
        service = get_kaspi_service()
        response = await service.create_payment(
            phone=request.phone,
            amount=request.amount,
            message=request.message,
            organization_bin=request.organization_bin
        )

        external_id_raw = response.get("data", {}).get("externalId")
        return CreatePaymentResponse(
            success=response.get("status", response.get("success", False)),
            external_id=str(external_id_raw) if external_id_raw else None,
            status=response.get("data", {}).get("status")
        )

    except KaspiPayServiceError as e:
        logger.error("kaspi_api_create_payment_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{external_id}", response_model=PaymentStatusResponse)
async def check_payment_status(external_id: str):
    """
    Check payment status

    Check current status of a payment by externalId (QrPaymentId).

    **Statuses:**
    - **Wait**: Waiting for customer to pay
    - **Processed**: Payment completed successfully
    - **Error**: Payment failed

    **Args:**
    - **external_id**: QrPaymentId from create_payment

    **Example Response:**
    ```json
    {
        "success": true,
        "external_id": "12345678901",
        "status": "Processed"
    }
    ```
    """
    logger.info("kaspi_api_check_status", external_id=external_id)

    try:
        service = get_kaspi_service()
        response = await service.check_status(external_id)

        return PaymentStatusResponse(
            success=response.get("success", False),
            external_id=external_id,
            status=response.get("data", {}).get("status")
        )

    except KaspiPayServiceError as e:
        logger.error("kaspi_api_check_status_error", error=str(e), external_id=external_id)
        raise HTTPException(status_code=500, detail=str(e))


# NOTE: /details/ endpoint removed because it doesn't exist on production API
# Production API (cvety.kz/api/v2/paymentkaspi/) only has: create, status, refund
# The details endpoint returns 404, so it has been removed from our API


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(request: RefundRequest):
    """
    Refund payment (full or partial)

    Refund all or part of a processed payment.

    **NOTE:** This endpoint does NOT pre-check available refund amount because
    the /details/ endpoint doesn't exist on production API. Kaspi will return
    error if refund amount exceeds available amount.

    **Args:**
    - **external_id**: QrPaymentId from create_payment
    - **amount**: Amount to refund in tenge
    - **organization_bin**: Optional BIN (must match payment's BIN)

    **Returns:**
    - **refunded_amount**: Amount successfully refunded

    **Errors:**
    - **400**: Insufficient funds for refund
    - **500**: API error or service unavailable

    **Example:**
    ```json
    {
        "external_id": "12345678901",
        "amount": 50,
        "organization_bin": "210440028324"
    }
    ```
    """
    logger.info(
        "kaspi_api_refund",
        external_id=request.external_id,
        amount=request.amount,
        organization_bin=request.organization_bin
    )

    try:
        service = get_kaspi_service()
        response = await service.refund(
            external_id=request.external_id,
            amount=request.amount,
            organization_bin=request.organization_bin
        )

        return RefundResponse(
            success=response.get("status", response.get("success", False)),
            external_id=request.external_id,
            refunded_amount=request.amount
        )

    except KaspiPayServiceError as e:
        error_msg = str(e)
        logger.error(
            "kaspi_api_refund_error",
            error=error_msg,
            external_id=request.external_id,
            amount=request.amount,
            organization_bin=request.organization_bin
        )

        # Return 400 for insufficient funds, 500 for other errors
        if "Insufficient funds" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)
