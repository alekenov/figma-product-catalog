"""
Kaspi Pay Configuration Model - Multi-BIN Support

Stores mapping of Organization BIN → TradePoint → DeviceToken
Essential for r3 "усиленная" scheme where each BIN needs its own device registration.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, func


class KaspiPayConfigBase(SQLModel):
    """Shared Kaspi Pay Config fields"""
    shop_id: int = Field(foreign_key="shop.id", index=True)
    organization_bin: str = Field(max_length=12, index=True, unique=True)
    trade_point_id: str = Field(max_length=36)
    device_token: str = Field(max_length=256)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    description: Optional[str] = Field(default=None, max_length=255)


class KaspiPayConfig(KaspiPayConfigBase, table=True):
    """
    Configuration for Kaspi Pay BIN (Organization Identification Number)

    Each BIN requires:
    - organization_bin: 12-digit BIN identifier
    - trade_point_id: TradePoint ID for this BIN
    - device_token: DeviceToken registered in r3/v01/device/register for this BIN+TradePoint
    - is_active: Whether this BIN is currently enabled
    - is_default: Whether this BIN should be used when no explicit BIN is specified
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
    last_verified_at: Optional[datetime] = Field(default=None)

    def __repr__(self):
        return f"<KaspiPayConfig(bin={self.organization_bin}, shop_id={self.shop_id}, active={self.is_active})>"


class KaspiPayLogBase(SQLModel):
    """Shared Kaspi Pay Log fields"""
    shop_id: int
    kaspi_config_id: Optional[int] = Field(default=None, foreign_key="kaspipayconfig.id")
    operation_type: str = Field(max_length=50)
    external_id: str = Field(max_length=20, index=True)
    organization_bin: str = Field(max_length=12)
    amount: int
    status: str = Field(max_length=50)
    error_message: Optional[str] = Field(default=None, max_length=500)


class KaspiPayLog(KaspiPayLogBase, table=True):
    """
    Audit log for all Kaspi Pay operations

    Tracks which BIN was used for each payment/refund for reconciliation
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), index=True)
    )

    def __repr__(self):
        return f"<KaspiPayLog(op={self.operation_type}, ext_id={self.external_id}, bin={self.organization_bin})>"
