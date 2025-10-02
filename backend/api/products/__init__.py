"""
Products API Module

Modular structure for product management endpoints.
Replaces monolithic api/products.py with clean separation of concerns.
"""

from .router import router

__all__ = ["router"]
