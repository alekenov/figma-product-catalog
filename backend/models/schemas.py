"""
API response schemas that combine data from multiple models.

These schemas are used for complex API responses that aggregate data from multiple tables.
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field

from .enums import ProductType
from .products import ProductImageRead, ProductVariantRead, ProductAddonRead
from .reviews import ProductReviewRead


# ===============================
# Product Detail Response Models
# ===============================

class CompositionItemRead(SQLModel):
    """Schema for composition item in detail response"""
    id: int = Field(description="Warehouse item ID")
    name: str = Field(description="Ingredient name")
    quantity: int = Field(description="Quantity needed")


class ProductBundleItemRead(SQLModel):
    """Schema for frequently bought product in bundle"""
    id: int = Field(description="Product ID")
    name: str = Field(description="Product name")
    price: int = Field(description="Price in kopecks")
    image: Optional[str] = Field(default=None, description="Product image URL")


class ReviewsBreakdownRead(SQLModel):
    """Schema for rating breakdown"""
    five: int = Field(alias="5")
    four: int = Field(alias="4")
    three: int = Field(alias="3")
    two: int = Field(alias="2")
    one: int = Field(alias="1")

    class Config:
        populate_by_name = True


class ReviewsAggregateRead(SQLModel):
    """Schema for reviews aggregate data"""
    count: int = Field(description="Total number of reviews")
    average_rating: float = Field(description="Average rating")
    breakdown: ReviewsBreakdownRead = Field(description="Rating breakdown by stars")
    photos: List[str] = Field(default_factory=list, description="Review photo URLs")
    items: List[ProductReviewRead] = Field(default_factory=list, description="Review items")


class ProductDetailRead(SQLModel):
    """Schema for complete product detail response"""
    # Basic product info
    id: int
    name: str
    price: int = Field(description="Base price in kopecks")
    type: ProductType
    description: Optional[str] = None
    image: Optional[str] = None
    enabled: bool
    is_featured: bool

    # Product attributes
    colors: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    manufacturingTime: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    shelfLife: Optional[int] = None

    # Metadata
    rating: Optional[float] = Field(default=None, description="Average rating from product reviews")
    review_count: int = Field(default=0, description="Number of product reviews")
    rating_count: int = Field(default=0, description="Total ratings given (from review_count + additional ratings)")

    # Images
    images: List[ProductImageRead] = Field(default_factory=list)

    # Variants (sizes)
    variants: List[ProductVariantRead] = Field(default_factory=list)

    # Composition (ingredients)
    composition: List[CompositionItemRead] = Field(default_factory=list)

    # Additional options
    addons: List[ProductAddonRead] = Field(default_factory=list)

    # Frequently bought together
    frequently_bought: List[ProductBundleItemRead] = Field(default_factory=list)

    # Pickup locations
    pickup_locations: List[str] = Field(default_factory=list, description="Formatted pickup address strings")

    # Reviews
    reviews: dict = Field(default_factory=dict, description="Product and company reviews")
