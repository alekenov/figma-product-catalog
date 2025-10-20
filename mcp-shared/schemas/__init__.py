"""Shared Pydantic schemas for Products, Orders, Customers, etc."""

from .products import ProductResponse, ProductCreate
from .orders import OrderResponse, OrderCreate, OrderStatusUpdate
from .common import BaseResponse, ErrorResponse, PaginatedResponse

__all__ = [
    "ProductResponse",
    "ProductCreate",
    "OrderResponse",
    "OrderCreate",
    "OrderStatusUpdate",
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
]
