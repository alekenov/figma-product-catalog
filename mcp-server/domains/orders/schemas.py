"""
Order schemas with Pydantic validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class OrderItem(BaseModel):
    """Order item with product and quantity."""

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    """Order creation payload."""

    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: str = Field(..., min_length=11, max_length=15)
    delivery_date: str = Field(..., description="Natural language or YYYY-MM-DD")
    delivery_time: str = Field(..., description="Natural language or HH:MM")
    shop_id: int = Field(..., gt=0)
    items: List[OrderItem] = Field(..., min_length=1)
    total_price: int = Field(..., gt=0, description="Price in tiyins (tenge * 100)")
    delivery_type: Literal["delivery", "pickup"] = Field("delivery")
    delivery_address: Optional[str] = Field(None, max_length=500)
    pickup_address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    telegram_user_id: Optional[str] = None
    recipient_name: Optional[str] = Field(None, max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=15)
    sender_phone: Optional[str] = Field(None, max_length=15)


class OrderUpdate(BaseModel):
    """Order update payload (customer-facing)."""

    delivery_address: Optional[str] = Field(None, max_length=500)
    delivery_date: Optional[str] = None
    delivery_time: Optional[str] = None
    delivery_notes: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    recipient_name: Optional[str] = Field(None, max_length=255)


class OrderStatusUpdate(BaseModel):
    """Order status update (admin only)."""

    status: Literal["new", "paid", "confirmed", "processing", "ready", "delivered", "cancelled"]
    notes: Optional[str] = Field(None, max_length=1000)


class OrderCostPreview(BaseModel):
    """Order cost preview request."""

    shop_id: int = Field(..., gt=0)
    items: List[OrderItem] = Field(..., min_length=1)
