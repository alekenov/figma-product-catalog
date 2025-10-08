"""
Product schemas with Pydantic validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class ProductType(str, Enum):
    """Valid product types."""

    FLOWERS = "flowers"
    SWEETS = "sweets"
    FRUITS = "fruits"
    GIFTS = "gifts"


class ProductFilters(BaseModel):
    """Filters for product listing."""

    shop_id: Optional[int] = Field(None, description="Filter by shop ID")
    search: Optional[str] = Field(None, max_length=100, description="Search in product names")
    product_type: Optional[ProductType] = Field(None, description="Filter by product type")
    enabled_only: bool = Field(True, description="Show only enabled products")
    min_price: Optional[int] = Field(None, ge=0, description="Minimum price in tenge")
    max_price: Optional[int] = Field(None, ge=0, description="Maximum price in tenge")
    skip: int = Field(0, ge=0, description="Number of products to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of products to return")


class ProductCreate(BaseModel):
    """Product creation payload."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., description="Product type (ready, custom, gift)")
    price: int = Field(..., gt=0, description="Price in tenge")
    description: Optional[str] = Field(None, max_length=2000)
    enabled: bool = Field(True)


class ProductUpdate(BaseModel):
    """Product update payload (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=2000)
    enabled: Optional[bool] = None


class AvailabilityCheck(BaseModel):
    """Product availability check parameters."""

    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, gt=0)
    shop_id: int = Field(..., gt=0)
