"""
Review models including product reviews, company reviews, FAQs, and static pages.

Includes ProductReview, CompanyReview, ReviewPhoto, FAQ, and StaticPage models with their schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Index
from sqlalchemy import DateTime, func, Column


# ===============================
# Product Review Models
# ===============================

class ProductReviewBase(SQLModel):
    """Shared product review fields"""
    product_id: int = Field(foreign_key="product.id")
    author_name: str = Field(max_length=100, description="Review author name")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    text: str = Field(max_length=2000, description="Review text")
    likes: int = Field(default=0, ge=0, description="Number of likes")
    dislikes: int = Field(default=0, ge=0, description="Number of dislikes")


class ProductReview(ProductReviewBase, table=True):
    """Product review table model - reviews for individual products"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    photos: List["ReviewPhoto"] = Relationship(back_populates="review")


class ProductReviewCreate(ProductReviewBase):
    """Schema for creating product reviews"""
    pass


class ProductReviewRead(ProductReviewBase):
    """Schema for reading product reviews"""
    id: int
    created_at: Optional[datetime] = None
    photos: List["ReviewPhotoRead"] = []


# ===============================
# Review Photo Models
# ===============================

class ReviewPhotoBase(SQLModel):
    """Shared review photo fields"""
    review_id: int = Field(foreign_key="productreview.id")
    url: str = Field(max_length=500, description="Photo URL")
    order: int = Field(default=0, description="Display order")


class ReviewPhoto(ReviewPhotoBase, table=True):
    """Review photo table model - photos attached to reviews"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    review: Optional["ProductReview"] = Relationship(back_populates="photos")


class ReviewPhotoCreate(ReviewPhotoBase):
    """Schema for creating review photos"""
    pass


class ReviewPhotoRead(ReviewPhotoBase):
    """Schema for reading review photos"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Company Review Models
# ===============================

class CompanyReviewBase(SQLModel):
    """Shared company review fields"""
    author_name: str = Field(max_length=100, description="Review author name")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    text: str = Field(max_length=2000, description="Review text")
    likes: int = Field(default=0, ge=0, description="Number of likes")
    dislikes: int = Field(default=0, ge=0, description="Number of dislikes")
    shop_id: int = Field(foreign_key="shop.id", description="Shop being reviewed")


class CompanyReview(CompanyReviewBase, table=True):
    """Company review table model - reviews for the entire shop/company"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    shop: Optional["Shop"] = Relationship()


class CompanyReviewCreate(CompanyReviewBase):
    """Schema for creating company reviews"""
    pass


class CompanyReviewRead(CompanyReviewBase):
    """Schema for reading company reviews"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# FAQ Models
# ===============================

class FAQBase(SQLModel):
    """Shared FAQ fields"""
    question: str = Field(max_length=500, description="FAQ question")
    answer: str = Field(max_length=2000, description="FAQ answer")
    category: Optional[str] = Field(default="general", max_length=50, description="FAQ category")
    display_order: int = Field(default=0, description="Display order for sorting")
    enabled: bool = Field(default=True, description="Whether FAQ is visible")
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this FAQ")


class FAQ(FAQBase, table=True):
    """FAQ table model"""
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


class FAQCreate(FAQBase):
    """Schema for creating FAQs"""
    pass


class FAQUpdate(SQLModel):
    """Schema for updating FAQs"""
    question: Optional[str] = Field(default=None, max_length=500)
    answer: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=50)
    display_order: Optional[int] = None
    enabled: Optional[bool] = None


class FAQRead(FAQBase):
    """Schema for reading FAQs"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# Static Page Models
# ===============================

class StaticPageBase(SQLModel):
    """Shared static page fields"""
    slug: str = Field(max_length=100, description="URL slug")
    title: str = Field(max_length=200, description="Page title")
    content: str = Field(description="HTML or Markdown content")
    meta_description: Optional[str] = Field(default=None, max_length=300, description="SEO meta description")
    enabled: bool = Field(default=True, description="Whether page is published")
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this page")


class StaticPage(StaticPageBase, table=True):
    """Static page table model"""
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

    # Composite index for slug+shop uniqueness
    __table_args__ = (
        Index('idx_staticpage_slug_shop', 'slug', 'shop_id', unique=True),
    )


class StaticPageCreate(StaticPageBase):
    """Schema for creating static pages"""
    pass


class StaticPageUpdate(SQLModel):
    """Schema for updating static pages"""
    slug: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = None
    meta_description: Optional[str] = Field(default=None, max_length=300)
    enabled: Optional[bool] = None


class StaticPageRead(StaticPageBase):
    """Schema for reading static pages"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
