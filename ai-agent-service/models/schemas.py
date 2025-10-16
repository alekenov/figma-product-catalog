"""Pydantic schemas for API requests and responses."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for POST /chat endpoint."""

    message: str = Field(..., description="User message text")
    user_id: str = Field(..., description="Unique user identifier (telegram_id, phone, session_id)")
    channel: str = Field(default="telegram", description="Channel name (telegram, whatsapp, web, instagram)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context (user info, etc)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Покажи букеты до 10000 тенге",
                "user_id": "123456789",
                "channel": "telegram",
                "context": {"username": "johndoe", "first_name": "John"}
            }
        }


class RequestUsage(BaseModel):
    """Per-request usage metrics from Claude API."""

    input_tokens: int = Field(default=0, description="Input tokens (non-cached)")
    output_tokens: int = Field(default=0, description="Output tokens generated")
    cache_read_tokens: int = Field(default=0, description="Tokens read from cache")
    cache_creation_tokens: int = Field(default=0, description="Tokens written to cache")
    total_cost_usd: float = Field(default=0.0, description="Estimated cost for this request (USD)")
    cache_hit: bool = Field(default=False, description="Whether cache was used")

    class Config:
        json_schema_extra = {
            "example": {
                "input_tokens": 245,
                "output_tokens": 156,
                "cache_read_tokens": 1247,
                "cache_creation_tokens": 0,
                "total_cost_usd": 0.0023,
                "cache_hit": True
            }
        }


class ChatResponse(BaseModel):
    """Response model for POST /chat endpoint."""

    text: str = Field(..., description="AI response text")
    tracking_id: Optional[str] = Field(default=None, description="Order tracking ID if order was created")
    order_number: Optional[str] = Field(default=None, description="Order number if order was created")
    show_products: bool = Field(default=False, description="Whether to show product images")
    product_ids: Optional[List[int]] = Field(default=None, description="Product IDs to display (when filtered by AI)")
    usage: Optional[RequestUsage] = Field(default=None, description="Token usage metrics for this request")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Вот наши букеты до 10000 тенге...",
                "tracking_id": None,
                "order_number": None,
                "show_products": True,
                "product_ids": [3, 5, 8],
                "usage": {
                    "input_tokens": 245,
                    "output_tokens": 156,
                    "cache_read_tokens": 1247,
                    "total_cost_usd": 0.0023,
                    "cache_hit": True
                }
            }
        }


class ProductIdsRequest(BaseModel):
    """Request model for fetching products by specific IDs."""

    product_ids: List[int] = Field(..., description="List of product IDs to fetch")

    class Config:
        json_schema_extra = {
            "example": {
                "product_ids": [3, 5, 8]
            }
        }


class CacheStats(BaseModel):
    """Cache statistics model."""

    total_requests: int = Field(..., description="Total number of requests")
    cache_hits: int = Field(..., description="Number of cache hits")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage (0-100)")
    cached_input_tokens: int = Field(..., description="Total cached input tokens")
    regular_input_tokens: int = Field(..., description="Total regular input tokens")
    tokens_saved: int = Field(..., description="Total tokens saved by caching")
    cost_savings_usd: float = Field(..., description="Estimated cost savings in USD")
    last_cache_refresh: Optional[str] = Field(default=None, description="Last cache refresh timestamp")
