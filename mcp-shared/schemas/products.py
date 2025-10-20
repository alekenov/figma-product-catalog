"""Product-related Pydantic schemas."""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class ProductResponse(BaseModel):
    """Product response from Production API (cvety.kz)."""
    id: int
    title: str
    price: str  # "15 000 ₸" (formatted string from Production)
    image: str | HttpUrl
    images: list[str | HttpUrl] = Field(default_factory=list)
    isAvailable: bool
    createdAt: datetime
    type: str  # "vitrina" | "catalog"
    width: str | None = None
    height: str | None = None
    video: str | None = None
    duration: int | None = None
    discount: str | None = None
    composition: str | None = None
    colors: bool = False
    catalogWidth: str | None = None
    catalogHeight: str | None = None
    productionTime: int | None = None


class ProductCreate(BaseModel):
    """Schema for creating a new product on Production."""
    id: str = Field(..., description="Unique XML_ID for the product")
    title: str = Field(..., min_length=3, max_length=200)
    price: int = Field(..., gt=0, description="Price in kopecks")
    images_urls: list[HttpUrl] = Field(..., min_items=1)
    owner: str = Field(default="cvetykz", description="Shop XML_ID")
    properties: dict = Field(..., description="Must contain 'section' and 'color'")
    description: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "mcp-12345",
                "title": "Букет роз 25 шт",
                "price": 1500000,  # 15,000₸ in kopecks
                "images_urls": ["https://example.com/image.jpg"],
                "owner": "cvetykz",
                "properties": {
                    "section": ["roses"],
                    "color": ["red", "pink"]
                },
                "description": "Красивый букет из 25 роз"
            }
        }


class ProductStatusUpdate(BaseModel):
    """Schema for updating product status."""
    id: int
    active: bool | None = None
    in_stock: bool | None = None
    is_ready: bool | None = None
