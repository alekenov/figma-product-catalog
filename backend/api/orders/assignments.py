"""
Orders Assignment Router - Team assignment management

Handles assignment of responsible persons and couriers to orders.
Includes role-based access control and validation.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Order, OrderRead, OrderHistory, User, UserRole
from services.order_service import OrderService
from auth_utils import get_current_user, get_current_user_shop_id

router = APIRouter()


class AssignRequest(BaseModel):
    """Request model for assignment"""
    user_id: int = Field(..., description="ID of user to assign")


@router.patch("/{order_id}/assign-responsible", response_model=OrderRead)
async def assign_responsible(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int = Path(..., description="Order ID"),
    assign_data: AssignRequest
):
    """
    Assign responsible person to order.

    Only DIRECTOR or MANAGER can assign.
    Responsible can be DIRECTOR, MANAGER, or FLORIST (not COURIER).
    """

    # Validate permissions - only DIRECTOR or MANAGER can assign
    if current_user.role not in [UserRole.DIRECTOR, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Only DIRECTOR or MANAGER can assign responsible person"
        )

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    # Get user to assign
    assignee = await session.get(User, assign_data.user_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify assignee belongs to same shop
    if assignee.shop_id != shop_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign user from different shop"
        )

    # Validate role - responsible cannot be COURIER
    if assignee.role == UserRole.COURIER:
        raise HTTPException(
            status_code=400,
            detail="COURIER cannot be assigned as responsible. Use assign-courier endpoint instead."
        )

    # Validate role - must be DIRECTOR, MANAGER, or FLORIST
    if assignee.role not in [UserRole.DIRECTOR, UserRole.MANAGER, UserRole.FLORIST]:
        raise HTTPException(
            status_code=400,
            detail="Responsible must be DIRECTOR, MANAGER, or FLORIST"
        )

    try:
        # Store old value for history
        old_value = None
        if order.assigned_to_id:
            old_user = await session.get(User, order.assigned_to_id)
            old_value = f"{old_user.name} (ID: {old_user.id})" if old_user else str(order.assigned_to_id)

        # Update order assignment
        order.assigned_to_id = assign_data.user_id
        order.assigned_by_id = current_user.id
        order.assigned_at = datetime.now()

        # Create history entry
        new_value = f"{assignee.name} (ID: {assignee.id})"
        history = OrderHistory(
            order_id=order_id,
            field_name="assigned_to",
            old_value=old_value,
            new_value=new_value,
            changed_by="admin"
        )
        session.add(history)

        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Return updated order with full relations
        return await OrderService.get_order_with_items(session, order_id, shop_id)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to assign responsible: {str(e)}")


@router.patch("/{order_id}/assign-courier", response_model=OrderRead)
async def assign_courier(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int = Path(..., description="Order ID"),
    assign_data: AssignRequest
):
    """
    Assign courier to order.

    Only DIRECTOR or MANAGER can assign.
    Courier must have COURIER role.
    """

    # Validate permissions - only DIRECTOR or MANAGER can assign
    if current_user.role not in [UserRole.DIRECTOR, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Only DIRECTOR or MANAGER can assign courier"
        )

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    # Get user to assign
    assignee = await session.get(User, assign_data.user_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify assignee belongs to same shop
    if assignee.shop_id != shop_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign user from different shop"
        )

    # Validate role - courier must have COURIER role
    if assignee.role != UserRole.COURIER:
        raise HTTPException(
            status_code=400,
            detail="Only users with COURIER role can be assigned as courier"
        )

    try:
        # Store old value for history
        old_value = None
        if order.courier_id:
            old_user = await session.get(User, order.courier_id)
            old_value = f"{old_user.name} (ID: {old_user.id})" if old_user else str(order.courier_id)

        # Update order courier assignment
        order.courier_id = assign_data.user_id
        order.assigned_by_id = current_user.id
        order.assigned_at = datetime.now()

        # Create history entry
        new_value = f"{assignee.name} (ID: {assignee.id})"
        history = OrderHistory(
            order_id=order_id,
            field_name="courier",
            old_value=old_value,
            new_value=new_value,
            changed_by="admin"
        )
        session.add(history)

        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Return updated order with full relations
        return await OrderService.get_order_with_items(session, order_id, shop_id)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to assign courier: {str(e)}")
