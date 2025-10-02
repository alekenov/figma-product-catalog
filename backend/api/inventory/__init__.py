"""
Inventory API Module

Modular structure for inventory and warehouse management endpoints.
Replaces monolithic api/inventory.py with clean separation of concerns.
"""

from .router import router

__all__ = ["router"]
