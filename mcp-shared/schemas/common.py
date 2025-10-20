"""Common Pydantic schemas used across MCP servers."""

from pydantic import BaseModel, Field
from typing import TypeVar, Generic
from datetime import datetime

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response wrapper."""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str
    code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    success: bool = True
    data: list[T]
    total: int
    limit: int
    offset: int
    timestamp: datetime = Field(default_factory=datetime.now)
