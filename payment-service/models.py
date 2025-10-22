"""
Database models for Payment Service

Stores payment configurations and audit logs.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, func


# ===============================
# Payment Config Models
# ===============================

class PaymentConfigBase(SQLModel):
    """Shared payment config fields"""
    shop_id: int = Field(unique=True, index=True, description="Shop ID from main backend")
    organization_bin: str = Field(max_length=12, description="Kaspi organization BIN")
    is_active: bool = Field(default=True, description="Whether this config is active")
    provider: str = Field(default="kaspi", max_length=20, description="Payment provider (kaspi, cloudpayments, etc)")


class PaymentConfig(PaymentConfigBase, table=True):
    """
    Payment configuration for each shop

    Maps shop_id → organization_bin for automatic routing
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    def __repr__(self):
        return f"<PaymentConfig(shop_id={self.shop_id}, bin={self.organization_bin})>"


class PaymentConfigCreate(PaymentConfigBase):
    """Schema for creating payment config"""
    pass


class PaymentConfigUpdate(SQLModel):
    """Schema for updating payment config"""
    organization_bin: Optional[str] = Field(default=None, max_length=12)
    is_active: Optional[bool] = None
    provider: Optional[str] = Field(default=None, max_length=20)


class PaymentConfigRead(PaymentConfigBase):
    """Schema for reading payment config"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Payment Log Models
# ===============================

class PaymentLogBase(SQLModel):
    """Shared payment log fields"""
    shop_id: int = Field(description="Shop ID")
    organization_bin: str = Field(max_length=12, description="БИН used for this payment")
    operation_type: str = Field(max_length=20, description="create, status, refund")
    external_id: Optional[str] = Field(default=None, max_length=50, index=True, description="Kaspi QrPaymentId")
    amount: Optional[int] = Field(default=None, description="Amount in kopecks")
    status: Optional[str] = Field(default=None, max_length=50, description="Wait, Processed, Error")
    error_message: Optional[str] = Field(default=None, max_length=500)
    provider: str = Field(default="kaspi", max_length=20)


class PaymentLog(PaymentLogBase, table=True):
    """
    Audit log for all payment operations

    Tracks which БИН was used for each transaction
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), index=True)
    )

    def __repr__(self):
        return f"<PaymentLog(op={self.operation_type}, ext_id={self.external_id}, bin={self.organization_bin})>"


class PaymentLogCreate(PaymentLogBase):
    """Schema for creating payment log"""
    pass


class PaymentLogRead(PaymentLogBase):
    """Schema for reading payment log"""
    id: int
    created_at: Optional[datetime] = None
