"""
Orders API Module - Modular router structure

This module provides order-related API endpoints organized by functionality:
- crud: Core CRUD operations and statistics
- status: Status updates and history
- tracking: Public order tracking
- availability: Availability checks and public marketplace
- photos: Photo upload and management
- assignments: Team member assignments

All routers are combined and exported as a single APIRouter for backward compatibility.
"""

from fastapi import APIRouter

# Import all sub-routers
from . import crud, status, tracking, availability, photos, assignments

# Create main router
router = APIRouter()

# Include all sub-routers with their endpoints
router.include_router(crud.router, tags=["Orders - CRUD"])
router.include_router(status.router, tags=["Orders - Status"])
router.include_router(tracking.router, tags=["Orders - Tracking"])
router.include_router(availability.router, tags=["Orders - Availability"])
router.include_router(photos.router, tags=["Orders - Photos"])
router.include_router(assignments.router, tags=["Orders - Assignments"])

# Export the combined router
__all__ = ["router"]
