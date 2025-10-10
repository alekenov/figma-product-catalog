"""
Shop models including shop settings, pickup locations, and order counter.

Includes Shop, ShopSettings, PickupLocation, and OrderCounter models with their schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Index
from sqlalchemy import DateTime, func, Column, Enum as SAEnum
from pydantic import field_validator

from .enums import City
from utils import kopecks_to_tenge, tenge_to_kopecks, normalize_phone_number


# ===============================
# Shop Models (Multi-Tenancy)
# ===============================

class Shop(SQLModel, table=True):
    """Shop table model - each registered user creates their own shop"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, default="Мой магазин")
    owner_id: int = Field(unique=True, foreign_key="user.id", description="Shop owner (Director)")
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[City] = Field(
        default=None,
        sa_column=Column(SAEnum(City, values_callable=lambda x: [e.value for e in x]))
    )

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None

    # Working hours
    weekday_start: str = Field(default="09:00", description="Weekday opening time (HH:MM)")
    weekday_end: str = Field(default="18:00", description="Weekday closing time (HH:MM)")
    weekday_closed: bool = Field(default=False, description="Whether closed on weekdays")

    weekend_start: str = Field(default="10:00", description="Weekend opening time (HH:MM)")
    weekend_end: str = Field(default="17:00", description="Weekend closing time (HH:MM)")
    weekend_closed: bool = Field(default=False, description="Whether closed on weekends")

    # Delivery settings (prices in kopecks)
    delivery_cost: int = Field(default=150000, description="Delivery cost in kopecks (1500 tenge)")
    free_delivery_amount: int = Field(default=1000000, description="Free delivery threshold in kopecks (10000 tenge)")
    pickup_available: bool = Field(default=True)
    delivery_available: bool = Field(default=True)

    # Shop status
    is_active: bool = Field(default=True, description="Whether shop is active (can be blocked by superadmin)")

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    owner: Optional["User"] = Relationship(back_populates="owned_shop", sa_relationship_kwargs={"foreign_keys": "[Shop.owner_id]"})
    users: List["User"] = Relationship(back_populates="shop", sa_relationship_kwargs={"foreign_keys": "[User.shop_id]"})


class ShopCreate(SQLModel):
    """Schema for creating shops"""
    name: str = Field(max_length=200, default="Мой магазин")
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[City] = None

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None


class ShopUpdate(SQLModel):
    """Schema for updating shop settings"""
    name: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[City] = None

    weekday_start: Optional[str] = None
    weekday_end: Optional[str] = None
    weekday_closed: Optional[bool] = None

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None

    weekend_start: Optional[str] = None
    weekend_end: Optional[str] = None
    weekend_closed: Optional[bool] = None

    delivery_cost_tenge: Optional[int] = Field(default=None, description="Delivery cost in tenge")
    free_delivery_amount_tenge: Optional[int] = Field(default=None, description="Free delivery threshold in tenge")
    pickup_available: Optional[bool] = None
    delivery_available: Optional[bool] = None

    @property
    def delivery_cost(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.delivery_cost_tenge) if self.delivery_cost_tenge is not None else None

    @property
    def free_delivery_amount(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.free_delivery_amount_tenge) if self.free_delivery_amount_tenge is not None else None


class WorkingHoursUpdate(SQLModel):
    """Schema for updating working hours - accepts time strings"""
    weekday_start: Optional[str] = None
    weekday_end: Optional[str] = None
    weekday_closed: Optional[bool] = None
    weekend_start: Optional[str] = None
    weekend_end: Optional[str] = None
    weekend_closed: Optional[bool] = None


class DeliverySettingsUpdate(SQLModel):
    """Schema for updating delivery settings - accepts kopecks directly"""
    delivery_cost: Optional[int] = Field(default=None, description="Delivery cost in kopecks")
    free_delivery_amount: Optional[int] = Field(default=None, description="Free delivery threshold in kopecks")
    pickup_available: Optional[bool] = None
    delivery_available: Optional[bool] = None


class ShopRead(SQLModel):
    """Schema for reading shop information"""
    id: int
    name: str
    owner_id: int
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[City] = None

    weekday_start: str
    weekday_end: str
    weekday_closed: bool

    weekend_start: str
    weekend_end: str
    weekend_closed: bool

    delivery_cost: int
    free_delivery_amount: int
    pickup_available: bool
    delivery_available: bool
    is_active: Optional[bool] = True  # Made optional for backwards compatibility

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def delivery_cost_tenge(self) -> int:
        """Delivery cost in tenge for display"""
        return kopecks_to_tenge(self.delivery_cost)

    @property
    def free_delivery_amount_tenge(self) -> int:
        """Free delivery threshold in tenge for display"""
        return kopecks_to_tenge(self.free_delivery_amount)

    def model_dump(self, **kwargs):
        """Include tenge values in serialization"""
        data = super().model_dump(**kwargs)
        data['delivery_cost_tenge'] = self.delivery_cost_tenge
        data['free_delivery_amount_tenge'] = self.free_delivery_amount_tenge
        return data


# ===============================
# Shop Settings Models
# ===============================

class ShopSettingsBase(SQLModel):
    """Shared shop settings fields"""
    shop_name: str = Field(max_length=200)
    address: str = Field(max_length=500)
    city: City = Field(default=City.ALMATY)

    # Working hours
    weekday_start: str = Field(default="09:00", description="Weekday opening time (HH:MM)")
    weekday_end: str = Field(default="18:00", description="Weekday closing time (HH:MM)")
    weekday_closed: bool = Field(default=False, description="Whether closed on weekdays")

    weekend_start: str = Field(default="10:00", description="Weekend opening time (HH:MM)")
    weekend_end: str = Field(default="17:00", description="Weekend closing time (HH:MM)")
    weekend_closed: bool = Field(default=False, description="Whether closed on weekends")

    # Delivery settings (prices in kopecks)
    delivery_cost: int = Field(default=150000, description="Delivery cost in kopecks (1500 tenge)")
    free_delivery_amount: int = Field(default=1000000, description="Free delivery threshold in kopecks (10000 tenge)")
    pickup_available: bool = Field(default=True)
    delivery_available: bool = Field(default=True)


class ShopSettings(ShopSettingsBase, table=True):
    """Shop settings table model - singleton table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class ShopSettingsUpdate(SQLModel):
    """Schema for updating shop settings"""
    shop_name: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[City] = None

    weekday_start: Optional[str] = None
    weekday_end: Optional[str] = None
    weekday_closed: Optional[bool] = None

    weekend_start: Optional[str] = None
    weekend_end: Optional[str] = None
    weekend_closed: Optional[bool] = None

    delivery_cost_tenge: Optional[int] = Field(default=None, description="Delivery cost in tenge")
    free_delivery_amount_tenge: Optional[int] = Field(default=None, description="Free delivery threshold in tenge")
    pickup_available: Optional[bool] = None
    delivery_available: Optional[bool] = None

    @property
    def delivery_cost(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.delivery_cost_tenge) if self.delivery_cost_tenge is not None else None

    @property
    def free_delivery_amount(self) -> Optional[int]:
        """Convert tenge to kopecks for internal storage"""
        return tenge_to_kopecks(self.free_delivery_amount_tenge) if self.free_delivery_amount_tenge is not None else None


class ShopSettingsRead(ShopSettingsBase):
    """Schema for reading shop settings with tenge values"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def delivery_cost_tenge(self) -> int:
        """Delivery cost in tenge for display"""
        return kopecks_to_tenge(self.delivery_cost)

    @property
    def free_delivery_amount_tenge(self) -> int:
        """Free delivery threshold in tenge for display"""
        return kopecks_to_tenge(self.free_delivery_amount)

    def model_dump(self, **kwargs):
        """Include tenge values in serialization"""
        data = super().model_dump(**kwargs)
        data['delivery_cost_tenge'] = self.delivery_cost_tenge
        data['free_delivery_amount_tenge'] = self.free_delivery_amount_tenge
        return data


# ===============================
# Pickup Location Models
# ===============================

class PickupLocationBase(SQLModel):
    """Shared pickup location fields"""
    city: City = Field(description="City (Almaty/Astana)", sa_column=Column(SAEnum(City, values_callable=lambda x: [e.value for e in x])))
    address: str = Field(max_length=300, description="Full address")
    landmark: Optional[str] = Field(default=None, max_length=200, description="Landmark (e.g., 'ТЦ Dostyk Plaza')")
    enabled: bool = Field(default=True)
    display_order: int = Field(default=0, description="Display order in list")
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this pickup location")


class PickupLocation(PickupLocationBase, table=True):
    """Pickup location table model - shop pickup addresses"""
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
    shop: Optional["Shop"] = Relationship()


class PickupLocationCreate(PickupLocationBase):
    """Schema for creating pickup locations"""
    pass


class PickupLocationUpdate(SQLModel):
    """Schema for updating pickup locations"""
    city: Optional[City] = None
    address: Optional[str] = Field(default=None, max_length=300)
    landmark: Optional[str] = Field(default=None, max_length=200)
    enabled: Optional[bool] = None
    display_order: Optional[int] = None


class PickupLocationRead(PickupLocationBase):
    """Schema for reading pickup locations"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Order Counter Model for Atomic Number Generation
# ===============================

class OrderCounter(SQLModel, table=True):
    """Counter table for atomic order number generation"""
    id: int = Field(default=1, primary_key=True)
    counter: int = Field(default=0, description="Current order counter value")
    last_updated: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


# ===============================
# Public Shop Schemas (Marketplace)
# ===============================

class ShopPublicListItem(SQLModel):
    """
    Public schema for shop list items in marketplace.
    Contains minimal info for displaying shop cards.
    """
    id: int
    name: str
    city: Optional[City] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    # Delivery info
    delivery_cost_tenge: int
    delivery_available: bool
    pickup_available: bool

    # Computed fields (to be added dynamically)
    rating: Optional[float] = Field(default=None, description="Average rating from reviews")
    review_count: Optional[int] = Field(default=0, description="Total number of reviews")
    is_open: Optional[bool] = Field(default=None, description="Whether shop is currently open")

    @classmethod
    def from_shop(cls, shop: Shop, rating: Optional[float] = None, review_count: int = 0, is_open: Optional[bool] = None):
        """Create from Shop model with computed fields"""
        return cls(
            id=shop.id,
            name=shop.name,
            city=shop.city,
            phone=shop.phone,
            address=shop.address,
            delivery_cost_tenge=kopecks_to_tenge(shop.delivery_cost),
            delivery_available=shop.delivery_available,
            pickup_available=shop.pickup_available,
            rating=rating,
            review_count=review_count,
            is_open=is_open
        )


class ShopPublicDetail(SQLModel):
    """
    Public schema for shop details in marketplace.
    Contains full information including working hours.
    """
    id: int
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[City] = None

    # Working hours
    weekday_start: str
    weekday_end: str
    weekday_closed: bool
    weekend_start: str
    weekend_end: str
    weekend_closed: bool

    # Delivery settings
    delivery_cost_tenge: int
    free_delivery_amount_tenge: int
    pickup_available: bool
    delivery_available: bool

    # Computed fields
    rating: Optional[float] = Field(default=None, description="Average rating from reviews")
    review_count: Optional[int] = Field(default=0, description="Total number of reviews")
    is_open: Optional[bool] = Field(default=None, description="Whether shop is currently open")

    @classmethod
    def from_shop(cls, shop: Shop, rating: Optional[float] = None, review_count: int = 0, is_open: Optional[bool] = None):
        """Create from Shop model with computed fields"""
        return cls(
            id=shop.id,
            name=shop.name,
            phone=shop.phone,
            address=shop.address,
            city=shop.city,
            weekday_start=shop.weekday_start,
            weekday_end=shop.weekday_end,
            weekday_closed=shop.weekday_closed,
            weekend_start=shop.weekend_start,
            weekend_end=shop.weekend_end,
            weekend_closed=shop.weekend_closed,
            delivery_cost_tenge=kopecks_to_tenge(shop.delivery_cost),
            free_delivery_amount_tenge=kopecks_to_tenge(shop.free_delivery_amount),
            pickup_available=shop.pickup_available,
            delivery_available=shop.delivery_available,
            rating=rating,
            review_count=review_count,
            is_open=is_open
        )
