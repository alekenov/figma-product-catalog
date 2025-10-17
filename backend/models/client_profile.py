"""
Client Profile models for storing aggregated client preferences and habits.

Stores budget preferences, frequent recipients, and personalization settings
to enable fast AI-powered recommendations and order suggestions.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, func, Column, Index, UniqueConstraint


# ===============================
# Client Profile Models
# ===============================

class ClientProfileBase(SQLModel):
    """Shared client profile fields"""
    client_id: int = Field(foreign_key="client.id", description="Client this profile belongs to")
    shop_id: int = Field(foreign_key="shop.id", description="Shop for multi-tenancy")

    # Budget preferences (aggregated from order history):
    avg_order_total: Optional[int] = Field(default=None, description="Average order total in kopecks")
    min_order_total: Optional[int] = Field(default=None, description="Minimum order total in kopecks")
    max_order_total: Optional[int] = Field(default=None, description="Maximum order total in kopecks")
    total_orders_count: int = Field(default=0, description="Total number of completed orders")

    # Frequent recipients (top-3 as JSON array):
    # Format: [{"name": "Maria", "phone": "+7...", "address": "...", "count": 8}, ...]
    frequent_recipients: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Top-3 recipients as JSON array with delivery data"
    )

    # Privacy & personalization:
    allow_personalization: bool = Field(
        default=True,
        description="Whether client allows AI personalization (GDPR compliance)"
    )

    # Metadata:
    last_order_at: Optional[datetime] = Field(
        default=None,
        description="When last order was placed (for staleness detection)"
    )


class ClientProfile(ClientProfileBase, table=True):
    """Client profile table model"""
    __tablename__ = "client_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    client: Optional["Client"] = Relationship()
    shop: Optional["Shop"] = Relationship()

    # Indexes and constraints:
    __table_args__ = (
        Index('idx_client_profile_client_id', 'client_id'),  # Fast lookup by client
        Index('idx_client_profile_shop_id', 'shop_id'),      # Fast filtering by shop
        UniqueConstraint('client_id', 'shop_id', name='uq_client_profile_client_shop'),  # One profile per client per shop
    )


class ClientProfileCreate(SQLModel):
    """Schema for creating a new client profile"""
    client_id: int = Field(description="Client ID")
    shop_id: int = Field(description="Shop ID")
    allow_personalization: bool = Field(default=True, description="Allow AI personalization")


class ClientProfileUpdate(SQLModel):
    """Schema for updating client profile"""
    avg_order_total: Optional[int] = Field(default=None, description="Average order total in kopecks")
    min_order_total: Optional[int] = Field(default=None, description="Minimum order total in kopecks")
    max_order_total: Optional[int] = Field(default=None, description="Maximum order total in kopecks")
    total_orders_count: Optional[int] = Field(default=None, description="Total orders count")
    frequent_recipients: Optional[str] = Field(default=None, description="Top-3 recipients JSON")
    allow_personalization: Optional[bool] = Field(default=None, description="Allow personalization")
    last_order_at: Optional[datetime] = Field(default=None, description="Last order timestamp")


class ClientProfileRead(ClientProfileBase):
    """Schema for reading client profile"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Response Schemas for AI Agent
# ===============================

class BudgetPreferences(SQLModel):
    """Budget preferences summary for AI"""
    avg: Optional[int] = Field(default=None, description="Average order total in kopecks")
    min: Optional[int] = Field(default=None, description="Minimum order total in kopecks")
    max: Optional[int] = Field(default=None, description="Maximum order total in kopecks")
    total_orders: int = Field(default=0, description="Number of completed orders")


class FrequentRecipient(SQLModel):
    """Frequent recipient data for AI"""
    name: str = Field(description="Recipient name")
    phone: str = Field(description="Recipient phone (normalized)")
    address: Optional[str] = Field(default=None, description="Most frequent delivery address")
    count: int = Field(description="Number of deliveries to this recipient")


class ClientProfileAIResponse(SQLModel):
    """AI-optimized client profile response"""
    client_id: int = Field(description="Client ID")
    allow_personalization: bool = Field(description="Whether personalization is allowed")
    budget: Optional[BudgetPreferences] = Field(default=None, description="Budget preferences")
    frequent_recipients: list[FrequentRecipient] = Field(default_factory=list, description="Top-3 recipients")
    last_order_at: Optional[datetime] = Field(default=None, description="Last order timestamp")
