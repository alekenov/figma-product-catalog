"""
Product models including variants and images.

Includes Product, ProductVariant, and ProductImage models with their schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from sqlalchemy import DateTime, func
from pydantic import model_validator

from .enums import ProductType


# ===============================
# Product Models
# ===============================

class ProductBase(SQLModel):
    """Shared product fields"""
    name: str = Field(max_length=200)
    price: int = Field(description="Price in tenge (kopecks)")
    type: ProductType = Field(default=ProductType.FLOWERS)
    description: Optional[str] = Field(default=None, max_length=1000)
    manufacturingTime: Optional[int] = Field(default=None, description="Manufacturing time in minutes")
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    shelfLife: Optional[int] = Field(default=None)
    enabled: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    colors: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    occasions: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    cities: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="Filter tags like urgent, budget, discount")
    image: Optional[str] = Field(default=None, max_length=500)


class Product(ProductBase, table=True):
    """Product table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this product")
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    recipes: List["ProductRecipe"] = Relationship(back_populates="product")
    shop: Optional["Shop"] = Relationship()
    images: List["ProductImage"] = Relationship(back_populates="product")
    # embeddings relationship removed - ProductEmbedding uses application-level joins


class ProductCreate(ProductBase):
    """Schema for creating products"""
    pass


class ProductUpdate(SQLModel):
    """Schema for updating products"""
    name: Optional[str] = Field(default=None, max_length=200)
    price: Optional[int] = None
    type: Optional[ProductType] = None
    description: Optional[str] = Field(default=None, max_length=1000)
    manufacturingTime: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    shelfLife: Optional[int] = None
    enabled: Optional[bool] = None
    is_featured: Optional[bool] = None
    colors: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    image: Optional[str] = None


# ===============================
# Product Image Models (moved here to resolve forward reference)
# ===============================

class ProductImageBase(SQLModel):
    """Shared product image fields"""
    product_id: int = Field(foreign_key="product.id")
    url: str = Field(max_length=500, description="Image URL")
    order: int = Field(default=0, description="Display order")
    is_primary: bool = Field(default=False, description="Primary/main image")


class ProductImage(ProductImageBase, table=True):
    """Product image table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    product: Optional["Product"] = Relationship(back_populates="images")


class ProductImageCreate(ProductImageBase):
    """Schema for creating product images"""
    pass


class ProductImageRead(ProductImageBase):
    """Schema for reading product images"""
    id: int
    created_at: Optional[datetime] = None


class ProductRead(ProductBase):
    """Schema for reading products"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    images: List[ProductImageRead] = Field(default_factory=list, description="Product images")
    colors_detailed: Optional[List[dict]] = Field(
        default=None,
        description="Detailed color information with hex codes and descriptions for AI/MCP"
    )

    @model_validator(mode='after')
    def enrich_colors(self) -> 'ProductRead':
        """
        Automatically enrich colors with detailed information.

        This validator runs after model creation and populates colors_detailed
        with full color data (hex, description) for each color name.
        """
        # Import here to avoid circular dependency
        from api.colors import get_color_details

        if self.colors:
            self.colors_detailed = []
            for color_name in self.colors:
                color_detail = get_color_details(color_name)
                if color_detail:
                    self.colors_detailed.append(color_detail)

        return self


# ===============================
# Product Variant Models (Size/Price variations)
# ===============================

class ProductVariantBase(SQLModel):
    """Shared product variant fields"""
    product_id: int = Field(foreign_key="product.id")
    size: str = Field(max_length=10, description="S, M, L, XL, etc.")
    price: int = Field(description="Price in kopecks for this variant")
    enabled: bool = Field(default=True)


class ProductVariant(ProductVariantBase, table=True):
    """Product variant table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductVariantCreate(ProductVariantBase):
    """Schema for creating product variants"""
    pass


class ProductVariantRead(ProductVariantBase):
    """Schema for reading product variants"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Product Addon Models (Additional Options)
# ===============================

class ProductAddonBase(SQLModel):
    """Shared product addon fields"""
    product_id: int = Field(foreign_key="product.id")
    name: str = Field(max_length=200, description="Addon name (e.g., 'Упаковочная лента и бумага')")
    description: Optional[str] = Field(default=None, max_length=500)
    price: int = Field(default=0, description="Price in kopecks (0 for free options)")
    is_default: bool = Field(default=False, description="Whether this option is checked by default")
    enabled: bool = Field(default=True)


class ProductAddon(ProductAddonBase, table=True):
    """Product addon table model - additional options like packaging, greeting cards"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductAddonCreate(ProductAddonBase):
    """Schema for creating product addons"""
    pass


class ProductAddonRead(ProductAddonBase):
    """Schema for reading product addons"""
    id: int
    created_at: Optional[datetime] = None


# ===============================
# Product Bundle Models (Frequently Bought Together)
# ===============================

class ProductBundleBase(SQLModel):
    """Shared product bundle fields"""
    main_product_id: int = Field(foreign_key="product.id", description="Main product ID")
    bundled_product_id: int = Field(foreign_key="product.id", description="Related product ID")
    display_order: int = Field(default=0, description="Display order in list")
    enabled: bool = Field(default=True)


class ProductBundle(ProductBundleBase, table=True):
    """Product bundle table model - frequently bought together suggestions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class ProductBundleCreate(ProductBundleBase):
    """Schema for creating product bundles"""
    pass


class ProductBundleRead(ProductBundleBase):
    """Schema for reading product bundles"""
    id: int
    created_at: Optional[datetime] = None
