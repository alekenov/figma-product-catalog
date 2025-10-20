"""Order-related Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime


class OrderExecutor(BaseModel):
    """Order executor (florist, courier)."""
    id: str
    name: str
    avatar: str | None = None
    source: str


class OrderResponse(BaseModel):
    """Order response from Production API."""
    id: int
    status_id: str  # "CO", "DE", etc.
    status_key: str  # "assembled", "in-transit", etc.
    status_name: str  # "Собран", "В пути", etc.
    number: str
    status: str
    deliveryCity: str | None = None
    deliveryTime: str | None = None
    deliveryAddressShort: str | None = None
    recipientMasked: str | None = None
    recipientPhoneMasked: str | None = None
    paymentAmount: str  # "17 000 ₸"
    paymentStatus: str  # "Оплачен"
    mainImage: str
    executors: list[OrderExecutor] = Field(default_factory=list)
    createdAt: datetime


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., pattern=r"^\+?7\d{10}$")
    delivery_address: str | None = None
    recipient_name: str | None = None
    recipient_phone: str | None = None
    delivery_type: str = Field(default="delivery")  # "delivery" | "pickup"
    delivery_date: str  # ISO date
    delivery_time: str
    pickup_address: str | None = None
    shop_id: int = Field(default=17008)
    items: list[dict]  # [{"product_id": 1, "quantity": 2}]
    total_price: int  # in kopecks
    notes: str | None = None
    telegram_user_id: str | None = None
    sender_phone: str | None = None


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    id: int
    status: str = Field(..., description="New status key (assembled, in-transit, delivered)")
    notes: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123891,
                "status": "in-transit",
                "notes": "Курьер выехал"
            }
        }
