"""
Client Profile API endpoints for AI Agent and privacy management.

Provides:
- GET /client_profile - Get profile for AI personalization
- PATCH /client_profile/privacy - Update privacy settings (GDPR)
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import json

from database import get_session
from auth_utils import get_current_user
from models import (
    User,
    Client,
    ClientProfile,
    ClientProfileAIResponse,
    BudgetPreferences,
    FrequentRecipient
)
from services.profile_builder_service import profile_builder_service

router = APIRouter(prefix="/client_profile", tags=["Client Profile"])


@router.get("", response_model=ClientProfileAIResponse)
async def get_client_profile(
    phone: str = Query(..., description="Client phone number (normalized)"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get client profile for AI Agent personalization.

    Returns aggregated budget preferences and top-3 frequent recipients.
    Only returns data if allow_personalization=True (GDPR compliance).

    Args:
        phone: Client phone number
        current_user: Authenticated user (ensures shop_id filtering)
        session: Database session

    Returns:
        ClientProfileAIResponse with budget stats and recipients
    """
    # Get client by phone and shop
    client_query = select(Client).where(
        Client.phone == phone,
        Client.shop_id == current_user.shop_id
    )
    result = await session.execute(client_query)
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client with phone {phone} not found in shop {current_user.shop_id}"
        )

    # Get or create profile
    profile = await profile_builder_service.get_or_create_profile(
        session,
        client.id,
        current_user.shop_id
    )

    # Build AI-optimized response
    budget = None
    if profile.avg_order_total is not None:
        budget = BudgetPreferences(
            avg=profile.avg_order_total,
            min=profile.min_order_total,
            max=profile.max_order_total,
            total_orders=profile.total_orders_count
        )

    recipients = []
    if profile.frequent_recipients:
        try:
            recipients_data = json.loads(profile.frequent_recipients)
            recipients = [
                FrequentRecipient(**recipient_data)
                for recipient_data in recipients_data
            ]
        except json.JSONDecodeError:
            # Malformed JSON - return empty list
            pass

    return ClientProfileAIResponse(
        client_id=client.id,
        allow_personalization=profile.allow_personalization,
        budget=budget,
        frequent_recipients=recipients,
        last_order_at=profile.last_order_at
    )


@router.patch("/privacy")
async def update_profile_privacy(
    phone: str = Query(..., description="Client phone number"),
    action: str = Query(
        ...,
        description="Privacy action: 'enable_personalization', 'disable_personalization', or 'delete_profile_data'"
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update client profile privacy settings (GDPR compliance).

    Actions:
    - enable_personalization: Allow AI to use profile data
    - disable_personalization: Block AI personalization
    - delete_profile_data: Clear all profile data (budget, recipients)

    Args:
        phone: Client phone number
        action: Privacy action to perform
        current_user: Authenticated user
        session: Database session

    Returns:
        Success message
    """
    # Validate action
    valid_actions = ["enable_personalization", "disable_personalization", "delete_profile_data"]
    if action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        )

    # Get client
    client_query = select(Client).where(
        Client.phone == phone,
        Client.shop_id == current_user.shop_id
    )
    result = await session.execute(client_query)
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Client with phone {phone} not found"
        )

    # Update privacy settings
    result = await profile_builder_service.update_profile_privacy(
        session,
        client.id,
        current_user.shop_id,
        action
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Failed to update privacy settings")
        )

    return {
        "success": True,
        "message": result.get("message"),
        "client_id": client.id,
        "action": action
    }
