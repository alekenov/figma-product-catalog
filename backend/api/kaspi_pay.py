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

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "77015211545",
                "amount": 100,
                "message": "Order #123 payment"
            }
        }


class RefundRequest(BaseModel):
    """Request to refund a payment"""
    external_id: str = Field(..., description="QrPaymentId from create payment")
    amount: float = Field(..., gt=0, description="Amount to refund in tenge")

    class Config:
        json_schema_extra = {
            "example": {
                "external_id": "12345678901",
                "amount": 50
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


class PaymentDetailsResponse(BaseModel):
    """Response from get details"""
    success: bool
    total_amount: Optional[float] = Field(None, description="Total payment amount")
    available_return_amount: Optional[float] = Field(
        None,
        description="Amount available for refund"
    )
    transaction_date: Optional[str] = None
    product_type: Optional[str] = None
    error: Optional[str] = None


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

    **Returns:**
    - **external_id**: QrPaymentId for status tracking
    - **status**: Initial payment status (usually "Wait")

    **Example:**
    ```json
    {
        "phone": "77015211545",
        "amount": 100,
        "message": "Order #123"
    }
    ```
    """
    logger.info(
        "kaspi_api_create_payment",
        phone=request.phone,
        amount=request.amount,
        message=request.message
    )

    try:
        service = get_kaspi_service()
        response = await service.create_payment(
            phone=request.phone,
            amount=request.amount,
            message=request.message
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


@router.get("/details/{external_id}", response_model=PaymentDetailsResponse)
async def get_payment_details(external_id: str):
    """
    Get payment details

    Get detailed payment information including available refund amount.
    This is crucial before attempting refunds to avoid errors.

    **Args:**
    - **external_id**: QrPaymentId from create_payment

    **Returns:**
    - **total_amount**: Total payment amount
    - **available_return_amount**: Amount available for refund
    - **transaction_date**: Transaction timestamp
    - **product_type**: Kaspi product type

    **Example Response:**
    ```json
    {
        "success": true,
        "total_amount": 100,
        "available_return_amount": 100,
        "transaction_date": "2025-01-12T10:30:00",
        "product_type": "RemotePayment"
    }
    ```
    """
    logger.info("kaspi_api_get_details", external_id=external_id)

    try:
        service = get_kaspi_service()
        response = await service.get_details(external_id)

        data = response.get("data", {})

        return PaymentDetailsResponse(
            success=response.get("success", False),
            total_amount=data.get("TotalAmount"),
            available_return_amount=data.get("AvailableReturnAmount"),
            transaction_date=data.get("TransactionDate"),
            product_type=data.get("ProductType")
        )

    except KaspiPayServiceError as e:
        logger.error("kaspi_api_get_details_error", error=str(e), external_id=external_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(request: RefundRequest):
    """
    Refund payment (full or partial)

    Refund all or part of a processed payment.

    **IMPORTANT:** This endpoint automatically checks AvailableReturnAmount
    before attempting refund to prevent duplicate refund errors (-99000005).

    **Args:**
    - **external_id**: QrPaymentId from create_payment
    - **amount**: Amount to refund in tenge (must be ≤ available_return_amount)

    **Returns:**
    - **refunded_amount**: Amount successfully refunded

    **Errors:**
    - **400**: Insufficient funds for refund
    - **500**: API error or service unavailable

    **Example:**
    ```json
    {
        "external_id": "12345678901",
        "amount": 50
    }
    ```
    """
    logger.info(
        "kaspi_api_refund",
        external_id=request.external_id,
        amount=request.amount
    )

    try:
        service = get_kaspi_service()
        response = await service.refund(
            external_id=request.external_id,
            amount=request.amount
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
            amount=request.amount
        )

        # Return 400 for insufficient funds, 500 for other errors
        if "Insufficient funds" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)
