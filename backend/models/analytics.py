"""
Analytics models for tracking shop milestones and events.

Tracks first-time events for product management analytics.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime, func, Column


class ShopMilestone(SQLModel, table=True):
    """
    Track shop milestone achievements for analytics and notifications.

    Each shop has one row tracking which milestones have been reached.
    Used to send one-time notifications (e.g., "first product added").
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    shop_id: int = Field(unique=True, foreign_key="shop.id", description="Shop ID")

    # Onboarding milestones
    name_customized: bool = Field(default=False, description="Changed from 'Мой магазин'")
    city_added: bool = Field(default=False, description="Added city to shop settings")
    address_added: bool = Field(default=False, description="Added physical address")
    first_product_added: bool = Field(default=False, description="Added at least one product")
    shop_opened: bool = Field(default=False, description="Opened shop (is_open=true)")
    onboarding_completed: bool = Field(default=False, description="All onboarding steps done")

    # Operational milestones
    first_order_received: bool = Field(default=False, description="Received first order")

    # Timestamps for tracking
    name_customized_at: Optional[datetime] = None
    city_added_at: Optional[datetime] = None
    address_added_at: Optional[datetime] = None
    first_product_added_at: Optional[datetime] = None
    shop_opened_at: Optional[datetime] = None
    onboarding_completed_at: Optional[datetime] = None
    first_order_received_at: Optional[datetime] = None

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )
