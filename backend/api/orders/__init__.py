"""
Orders API Module

Modular structure for order management endpoints.
Replaces monolithic api/orders.py with clean separation of concerns.
"""

from .router import router

__all__ = ["router"]
