"""
Order models including order items, photos, and history.

Includes Order, OrderItem, OrderPhoto, and OrderHistory models with their schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, func, Column
from pydantic import field_validator

from .enums import OrderStatus
from utils import normalize_phone_number


# ===============================
# Order Models
# ===============================

class OrderBase(SQLModel):
    """Shared order fields"""
    tracking_id: str = Field(unique=True, index=True, max_length=9, description="Public 9-digit tracking ID")
    orderNumber: str = Field(unique=True, max_length=20, description="Order number like #12345")
    customerName: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    subtotal: int = Field(description="Subtotal in tenge")
    delivery_cost: int = Field(default=0, description="Delivery cost in tenge")
    total: int = Field(description="Total amount in tenge")
    status: OrderStatus = Field(default=OrderStatus.NEW)
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Telegram integration
    telegram_user_id: Optional[str] = Field(default=None, max_length=50, description="Telegram user ID for bot orders")

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100, description="Recipient name (may differ from customer)")
    recipient_phone: Optional[str] = Field(default=None, max_length=20, description="Recipient contact")
    sender_phone: Optional[str] = Field(default=None, max_length=20, description="Sender/orderer contact")
    pickup_address: Optional[str] = Field(default=None, max_length=500, description="Store pickup location")
    delivery_type: Optional[str] = Field(default=None, max_length=50, description="express, scheduled, pickup")
    scheduled_time: Optional[str] = Field(default=None, max_length=100, description="Scheduled delivery time")
    payment_method: Optional[str] = Field(default=None, max_length=50, description="kaspi, card, cash")
    order_comment: Optional[str] = Field(default=None, max_length=1000, description="Customer wishes/comments")
    bonus_points: Optional[int] = Field(default=0, description="Loyalty points earned")

    @field_validator('phone', 'recipient_phone', 'sender_phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone numbers to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None


class Order(OrderBase, table=True):
    """Order table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this order")

    # Assignment fields
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="user.id", description="Assigned responsible person (DIRECTOR/MANAGER/FLORIST)")
    courier_id: Optional[int] = Field(default=None, foreign_key="user.id", description="Assigned courier")
    assigned_by_id: Optional[int] = Field(default=None, foreign_key="user.id", description="Who made the assignment")
    assigned_at: Optional[datetime] = Field(default=None, description="When assignment was made")

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    items: List["OrderItem"] = Relationship(back_populates="order")
    reservations: List["OrderReservation"] = Relationship(back_populates="order")
    photos: List["OrderPhoto"] = Relationship()


class OrderCreate(SQLModel):
    """Schema for creating orders"""
    customerName: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    delivery_cost: int = Field(default=0, description="Delivery cost in tenge")
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    sender_phone: Optional[str] = Field(default=None, max_length=20)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    delivery_type: Optional[str] = Field(default=None, max_length=50)
    scheduled_time: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_comment: Optional[str] = Field(default=None, max_length=1000)
    bonus_points: Optional[int] = Field(default=0)

    # Telegram integration

    @field_validator('phone', 'recipient_phone', 'sender_phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone numbers to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None
    telegram_user_id: Optional[str] = Field(default=None, max_length=50, description="Telegram user ID for bot orders")


class OrderItemRequest(SQLModel):
    """Schema for order item availability request"""
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, description="Requested quantity")
    special_requests: Optional[str] = Field(default=None, max_length=500)


class OrderCreateWithItems(SQLModel):
    """Schema for creating orders with items"""
    customerName: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    delivery_cost: int = Field(default=0, description="Delivery cost in tenge")
    notes: Optional[str] = Field(default=None, max_length=1000)
    items: List[OrderItemRequest] = Field(description="Items to include in the order")
    check_availability: bool = Field(default=True, description="Whether to check availability before creating")

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    sender_phone: Optional[str] = Field(default=None, max_length=20)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    delivery_type: Optional[str] = Field(default=None, max_length=50)
    scheduled_time: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_comment: Optional[str] = Field(default=None, max_length=1000)
    bonus_points: Optional[int] = Field(default=0)

    # Telegram integration
    telegram_user_id: Optional[str] = Field(default=None, max_length=50, description="Telegram user ID for bot orders")

    @field_validator('phone', 'recipient_phone', 'sender_phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone numbers to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None


class OrderUpdate(SQLModel):
    """Schema for updating orders"""
    customerName: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_date: Optional[datetime] = None
    delivery_notes: Optional[str] = Field(default=None, max_length=500)
    status: Optional[OrderStatus] = None
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Phase 3: Checkout flow fields
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    sender_phone: Optional[str] = Field(default=None, max_length=20)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    delivery_type: Optional[str] = Field(default=None, max_length=50)
    scheduled_time: Optional[str] = Field(default=None, max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_comment: Optional[str] = Field(default=None, max_length=1000)
    bonus_points: Optional[int] = Field(default=None)

    @field_validator('phone', 'recipient_phone', 'sender_phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone numbers to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None


class OrderRead(OrderBase):
    """Schema for reading orders"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List["OrderItemRead"] = []
    photos: List["OrderPhotoRead"] = []


# ===============================
# Order Item Models
# ===============================

class OrderItemBase(SQLModel):
    """Shared order item fields"""
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    product_name: str = Field(max_length=200)
    product_price: int = Field(description="Product price at time of order")
    quantity: int = Field(default=1, ge=1)
    item_total: int = Field(description="Total for this line item")
    special_requests: Optional[str] = Field(default=None, max_length=500)


class OrderItem(OrderItemBase, table=True):
    """Order item table model"""
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
    order: Optional["Order"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="order_items")


class OrderItemCreate(OrderItemBase):
    """Schema for creating order items"""
    pass


class OrderItemRead(OrderItemBase):
    """Schema for reading order items"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Order Photo Models
# ===============================

class OrderPhotoBase(SQLModel):
    """Shared order photo fields"""
    order_id: int = Field(foreign_key="order.id")
    photo_url: str = Field(max_length=500, description="URL to photo")
    photo_type: str = Field(max_length=50, description="assembly, delivery, etc.")
    label: Optional[str] = Field(default=None, max_length=200, description="Photo caption")
    client_feedback: Optional[str] = Field(default=None, max_length=20, description="like or dislike")
    client_comment: Optional[str] = Field(default=None, max_length=1000, description="Client feedback comment")
    feedback_at: Optional[datetime] = Field(default=None, description="When feedback was given")


class OrderPhoto(OrderPhotoBase, table=True):
    """Order photo table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    uploaded_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    feedback_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime)
    )

    # Relationships
    order: Optional["Order"] = Relationship()


class OrderPhotoCreate(SQLModel):
    """Schema for creating order photos"""
    order_id: int
    photo_url: str = Field(max_length=500)
    photo_type: str = Field(max_length=50)
    label: Optional[str] = Field(default=None, max_length=200)


class OrderPhotoRead(OrderPhotoBase):
    """Schema for reading order photos"""
    id: int
    uploaded_at: Optional[datetime] = None


# ===============================
# Order History Models
# ===============================

class OrderHistoryBase(SQLModel):
    """Shared order history fields"""
    order_id: int = Field(foreign_key="order.id")
    changed_by: str = Field(max_length=20, description="'customer' or 'admin'")
    field_name: str = Field(max_length=100, description="Name of changed field")
    old_value: Optional[str] = Field(default=None, max_length=1000)
    new_value: Optional[str] = Field(default=None, max_length=1000)


class OrderHistory(OrderHistoryBase, table=True):
    """Order change history for audit trail"""
    id: Optional[int] = Field(default=None, primary_key=True)
    changed_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class OrderHistoryRead(OrderHistoryBase):
    """Schema for reading order history"""
    id: int
    changed_at: datetime
