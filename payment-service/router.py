"""
Payment Service API Router

Public endpoints for payment operations and admin endpoints for config management.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlmodel import Session, select

from models import (
    PaymentConfig, PaymentConfigCreate, PaymentConfigUpdate, PaymentConfigRead,
    PaymentLog, PaymentLogCreate, PaymentLogRead
)
from database import get_session
from kaspi_client import get_kaspi_client, KaspiClientError


# ==================== Routers ====================

payment_router = APIRouter(prefix="/payments/kaspi", tags=["Kaspi Payments"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== Request/Response Models ====================

class CreatePaymentRequest(BaseModel):
    """Request to create a new payment"""
    shop_id: int = Field(..., description="Shop ID")
    amount: float = Field(..., gt=0, description="Payment amount in tenge")
    phone: str = Field(..., description="Customer phone number (e.g., 77015211545)")
    message: str = Field(..., description="Payment description")


class CreatePaymentResponse(BaseModel):
    """Response from create payment"""
    success: bool
    external_id: Optional[str] = Field(None, description="QrPaymentId for tracking")
    status: Optional[str] = Field(None, description="Initial payment status")
    organization_bin: str = Field(..., description="БИН used for this payment")
    error: Optional[str] = None


class CreatePaymentLinkRequest(BaseModel):
    """Request to create a payment link"""
    shop_id: int = Field(..., description="Shop ID")
    amount: float = Field(..., gt=0, description="Payment amount in tenge")
    message: str = Field(..., description="Payment description")


class CreatePaymentLinkResponse(BaseModel):
    """Response from create payment link"""
    success: bool
    payment_link: Optional[str] = Field(None, description="Payment URL")
    payment_id: Optional[str] = Field(None, description="PaymentId for tracking")
    expire_date: Optional[str] = Field(None, description="Link expiration date")
    organization_bin: str = Field(..., description="БИН used for this payment")
    error: Optional[str] = None


class CheckStatusResponse(BaseModel):
    """Response from check status"""
    success: bool
    external_id: str
    status: Optional[str] = Field(None, description="Wait / Processed / Error")
    error: Optional[str] = None


class RefundRequest(BaseModel):
    """Request to refund a payment"""
    shop_id: int = Field(..., description="Shop ID (must match payment's shop_id)")
    external_id: str = Field(..., description="QrPaymentId from create payment")
    amount: float = Field(..., gt=0, description="Amount to refund in tenge")


class RefundResponse(BaseModel):
    """Response from refund"""
    success: bool
    external_id: str
    refunded_amount: float
    organization_bin: str = Field(..., description="БИН used for refund")
    error: Optional[str] = None


# ==================== Helper Functions ====================

async def get_payment_config(shop_id: int, session: Session) -> PaymentConfig:
    """
    Get payment config for shop_id

    Raises HTTPException if not found or inactive
    """
    config = session.exec(
        select(PaymentConfig).where(PaymentConfig.shop_id == shop_id)
    ).first()

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Payment config not found for shop_id={shop_id}. Please configure payment settings in admin panel."
        )

    if not config.is_active:
        raise HTTPException(
            status_code=403,
            detail=f"Payment config for shop_id={shop_id} is inactive"
        )

    return config


async def create_payment_log(
    shop_id: int,
    organization_bin: str,
    operation_type: str,
    external_id: Optional[str],
    amount: Optional[int],
    status: Optional[str],
    error_message: Optional[str],
    session: Session
):
    """Create payment log entry"""
    log = PaymentLog(
        shop_id=shop_id,
        organization_bin=organization_bin,
        operation_type=operation_type,
        external_id=external_id,
        amount=amount,
        status=status,
        error_message=error_message
    )
    session.add(log)
    session.commit()


# ==================== Payment Endpoints ====================

@payment_router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    session: Session = Depends(get_session)
):
    """
    Create a new Kaspi Pay remote payment

    **Automatically routes to correct БИН based on shop_id**

    Args:
    - **shop_id**: Shop ID from main backend
    - **amount**: Payment amount in tenge (must be > 0)
    - **phone**: Customer phone number (e.g., 77015211545)
    - **message**: Payment description for customer

    Returns:
    - **external_id**: QrPaymentId for status tracking
    - **organization_bin**: БИН used for this payment
    - **status**: Initial payment status (usually "Wait")
    """
    try:
        # 1. Get БИН for this shop
        config = await get_payment_config(request.shop_id, session)
        organization_bin = config.organization_bin

        # 2. Create payment via production API
        kaspi_client = get_kaspi_client()
        response = await kaspi_client.create_payment(
            phone=request.phone,
            amount=request.amount,
            message=request.message,
            organization_bin=organization_bin,
            device_token=config.device_token  # Pass device token if configured
        )

        external_id = response.get("data", {}).get("externalId")
        status = response.get("data", {}).get("status")

        # 3. Log operation
        await create_payment_log(
            shop_id=request.shop_id,
            organization_bin=organization_bin,
            operation_type="create",
            external_id=str(external_id) if external_id else None,
            amount=int(request.amount * 100),  # Convert to kopecks
            status=status,
            error_message=None,
            session=session
        )

        return CreatePaymentResponse(
            success=True,
            external_id=str(external_id) if external_id else None,
            status=status,
            organization_bin=organization_bin
        )

    except KaspiClientError as e:
        # Log error
        await create_payment_log(
            shop_id=request.shop_id,
            organization_bin=config.organization_bin if config else "unknown",
            operation_type="create",
            external_id=None,
            amount=int(request.amount * 100),
            status="error",
            error_message=str(e),
            session=session
        )
        raise HTTPException(status_code=500, detail=str(e))


@payment_router.post("/create-link", response_model=CreatePaymentLinkResponse)
async def create_payment_link(
    request: CreatePaymentLinkRequest,
    session: Session = Depends(get_session)
):
    """
    Create a payment link (no phone required)

    **Automatically routes to correct БИН based on shop_id**

    Args:
    - **shop_id**: Shop ID from main backend
    - **amount**: Payment amount in tenge (must be > 0)
    - **message**: Payment description for customer

    Returns:
    - **payment_link**: URL for customer to pay
    - **payment_id**: PaymentId for status tracking
    - **expire_date**: Link expiration time (3 minutes after activation)
    - **organization_bin**: БИН used for this payment

    Note: Payment link can be shared via WhatsApp, Telegram, Email, or QR code
    """
    try:
        # 1. Get БИН and device token for this shop
        config = await get_payment_config(request.shop_id, session)
        organization_bin = config.organization_bin

        if not config.device_token:
            raise HTTPException(
                status_code=400,
                detail=f"Device token not configured for shop_id={request.shop_id}. Payment links require device token."
            )

        # 2. Create payment link via production API
        kaspi_client = get_kaspi_client()
        response = await kaspi_client.create_payment_link(
            amount=request.amount,
            message=request.message,
            organization_bin=organization_bin,
            device_token=config.device_token
        )

        payment_link = response.get("data", {}).get("paymentLink")
        payment_id = response.get("data", {}).get("paymentId")
        expire_date = response.get("data", {}).get("expireDate")

        # 3. Log operation
        await create_payment_log(
            shop_id=request.shop_id,
            organization_bin=organization_bin,
            operation_type="create-link",
            external_id=str(payment_id) if payment_id else None,
            amount=int(request.amount * 100),  # Convert to kopecks
            status="QrTokenCreated",
            error_message=None,
            session=session
        )

        return CreatePaymentLinkResponse(
            success=True,
            payment_link=payment_link,
            payment_id=str(payment_id) if payment_id else None,
            expire_date=expire_date,
            organization_bin=organization_bin
        )

    except KaspiClientError as e:
        # Log error
        await create_payment_log(
            shop_id=request.shop_id,
            organization_bin=config.organization_bin if config else "unknown",
            operation_type="create-link",
            external_id=None,
            amount=int(request.amount * 100),
            status="error",
            error_message=str(e),
            session=session
        )
        raise HTTPException(status_code=500, detail=str(e))


@payment_router.get("/status/{external_id}", response_model=CheckStatusResponse)
async def check_payment_status(
    external_id: str,
    session: Session = Depends(get_session)
):
    """
    Check payment status

    **No БИН required - just check by externalId**

    Args:
    - **external_id**: QrPaymentId from create_payment

    Returns:
    - **status**: Wait / Processed / Error
    """
    try:
        kaspi_client = get_kaspi_client()
        response = await kaspi_client.check_status(external_id)

        status = response.get("data", {}).get("status")

        return CheckStatusResponse(
            success=True,
            external_id=external_id,
            status=status
        )

    except KaspiClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


@payment_router.post("/refund", response_model=RefundResponse)
async def refund_payment(
    request: RefundRequest,
    session: Session = Depends(get_session)
):
    """
    Refund payment (full or partial)

    **Automatically uses correct БИН based on shop_id**

    Args:
    - **shop_id**: Shop ID (must match original payment's shop_id)
    - **external_id**: QrPaymentId from create_payment
    - **amount**: Amount to refund in tenge

    Returns:
    - **refunded_amount**: Amount successfully refunded
    - **organization_bin**: БИН used for refund
    """
    try:
        # 1. Get БИН for this shop
        config = await get_payment_config(request.shop_id, session)
        organization_bin = config.organization_bin

        # 2. Refund via production API
        kaspi_client = get_kaspi_client()
        response = await kaspi_client.refund(
            external_id=request.external_id,
            amount=request.amount,
            organization_bin=organization_bin,
            device_token=config.device_token  # Pass device token for refunds
        )

        # 3. Log operation
        await create_payment_log(
            shop_id=request.shop_id,
            organization_bin=organization_bin,
            operation_type="refund",
            external_id=request.external_id,
            amount=int(request.amount * 100),
            status="success",
            error_message=None,
            session=session
        )

        return RefundResponse(
            success=True,
            external_id=request.external_id,
            refunded_amount=request.amount,
            organization_bin=organization_bin
        )

    except KaspiClientError as e:
        # Log error
        await create_payment_log(
            shop_id=request.shop_id,
            organization_bin=config.organization_bin if config else "unknown",
            operation_type="refund",
            external_id=request.external_id,
            amount=int(request.amount * 100),
            status="error",
            error_message=str(e),
            session=session
        )

        # Return 400 for insufficient funds, 500 for other errors
        if "Insufficient funds" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Endpoints ====================

@admin_router.get("/configs", response_model=List[PaymentConfigRead])
async def list_payment_configs(session: Session = Depends(get_session)):
    """
    List all payment configurations

    Returns list of shop_id → organization_bin mappings
    """
    configs = session.exec(select(PaymentConfig)).all()
    return configs


@admin_router.get("/configs/{shop_id}", response_model=PaymentConfigRead)
async def get_payment_config_by_id(shop_id: int, session: Session = Depends(get_session)):
    """Get payment config for specific shop_id"""
    config = session.exec(
        select(PaymentConfig).where(PaymentConfig.shop_id == shop_id)
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config not found for shop_id={shop_id}")

    return config


@admin_router.get("/configs/by-bin/{organization_bin}", response_model=PaymentConfigRead)
async def get_payment_config_by_bin(
    organization_bin: str,
    session: Session = Depends(get_session)
):
    """
    Get payment config by organization БИН

    This endpoint allows Production Bitrix ApiClient to lookup device_token
    by БИН without needing to know payment-service shop_id.

    Args:
    - **organization_bin**: Kaspi organization БИН (e.g., 920317450731)

    Returns:
    - Payment configuration with device_token

    Raises:
    - 404: Config not found for this БИН
    - 403: Config exists but is inactive
    """
    config = session.exec(
        select(PaymentConfig).where(PaymentConfig.organization_bin == organization_bin)
    ).first()

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Config not found for БИН={organization_bin}"
        )

    if not config.is_active:
        raise HTTPException(
            status_code=403,
            detail=f"Config for БИН={organization_bin} is inactive"
        )

    return config


@admin_router.post("/configs", response_model=PaymentConfigRead)
async def create_payment_config(
    config: PaymentConfigCreate,
    session: Session = Depends(get_session)
):
    """
    Create payment configuration for a shop

    Maps shop_id → organization_bin
    """
    # Check if already exists
    existing = session.exec(
        select(PaymentConfig).where(PaymentConfig.shop_id == config.shop_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"Config already exists for shop_id={config.shop_id}")

    db_config = PaymentConfig.model_validate(config)
    session.add(db_config)
    session.commit()
    session.refresh(db_config)

    return db_config


@admin_router.put("/configs/{shop_id}", response_model=PaymentConfigRead)
async def update_payment_config(
    shop_id: int,
    config_update: PaymentConfigUpdate,
    session: Session = Depends(get_session)
):
    """Update payment configuration"""
    config = session.exec(
        select(PaymentConfig).where(PaymentConfig.shop_id == shop_id)
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config not found for shop_id={shop_id}")

    # Update fields
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    session.add(config)
    session.commit()
    session.refresh(config)

    return config


@admin_router.delete("/configs/{shop_id}")
async def delete_payment_config(shop_id: int, session: Session = Depends(get_session)):
    """Deactivate payment configuration (soft delete)"""
    config = session.exec(
        select(PaymentConfig).where(PaymentConfig.shop_id == shop_id)
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config not found for shop_id={shop_id}")

    config.is_active = False
    session.add(config)
    session.commit()

    return {"message": f"Config deactivated for shop_id={shop_id}"}


@admin_router.get("/logs", response_model=List[PaymentLogRead])
async def list_payment_logs(
    shop_id: Optional[int] = None,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List payment logs (audit trail)

    Filter by shop_id if provided
    """
    query = select(PaymentLog)

    if shop_id:
        query = query.where(PaymentLog.shop_id == shop_id)

    query = query.order_by(PaymentLog.created_at.desc()).limit(limit)

    logs = session.exec(query).all()
    return logs


@admin_router.post("/migrate")
async def run_migrations():
    """
    Manually run database migrations

    USE WITH CAUTION! This endpoint executes schema changes.
    """
    try:
        from database import create_db_and_tables
        create_db_and_tables()
        return {"message": "Migrations executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
