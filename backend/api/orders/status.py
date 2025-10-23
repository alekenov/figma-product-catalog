"""
Orders Status Router - Status and history management

Handles order status updates, cancellations, and change history tracking.
Includes inventory reservation logic for status transitions.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import get_session
from models import (
    Order, OrderStatus, OrderRead, OrderHistory, OrderHistoryRead
)
from services.order_service import OrderService
from services.inventory_service import InventoryService
from auth_utils import get_current_user_shop_id

router = APIRouter()


class CancelRequest(BaseModel):
    """Request model for order cancellation"""
    reason: str = Field(..., description="Reason for cancellation")


@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int,
    status: OrderStatus,
    notes: Optional[str] = None
):
    """Update order status with automatic warehouse deduction for assembled orders"""

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    old_status = order.status

    # Begin transaction
    try:
        # Handle status transitions with reservation logic
        if status == OrderStatus.ASSEMBLED and old_status != OrderStatus.ASSEMBLED:
            # Convert reservations to actual deductions (without committing - let router control transaction)
            await InventoryService.convert_reservations_to_deductions(session, order.id, commit=False)
        elif status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
            # Release reservations for cancelled orders
            await InventoryService.release_reservations(session, order.id)

        # Update status and notes
        order.status = status
        if notes:
            order.notes = notes

        # Commit changes (now includes both inventory operations and status update)
        await session.commit()

        # Clear session to avoid expired object issues
        session.expunge_all()

        # Use service method to properly load order with all relationships
        return await OrderService.get_order_with_items(session, order.id, shop_id)

    except Exception as e:
        # Rollback transaction on any error
        await session.rollback()
        if "insufficient stock" in str(e).lower():
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    cancel_data: CancelRequest
):
    """
    Cancel an order by customer or admin.

    - Changes status to CANCELLED
    - Releases inventory reservations
    - Creates order history entry
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if order can be cancelled (only new, accepted, assembled can be cancelled)
    if order.status not in [OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.ASSEMBLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status {order.status.value}"
        )

    try:
        # Release reservations (handle case when no reservations exist)
        try:
            await InventoryService.release_reservations(session, order.id)
        except Exception as reservation_error:
            from core.logging import get_logger
            logger = get_logger(__name__)
            logger.warning("reservation_release_failed", order_id=order.id, error=str(reservation_error))
            # Continue with cancellation even if reservation release fails

        # Update status
        old_status = order.status
        order.status = OrderStatus.CANCELLED
        if cancel_data.reason:
            order.notes = f"Cancelled: {cancel_data.reason}"

        # Create history entry
        history = OrderHistory(
            order_id=order_id,
            field_name="status",
            old_value=old_status.value,
            new_value=f"cancelled (Reason: {cancel_data.reason})" if cancel_data.reason else "cancelled",
            changed_by="customer"
        )
        session.add(history)

        await session.commit()
        session.expunge_all()

        # Return updated order (use order's shop_id for fetching)
        return await OrderService.get_order_with_items(session, order.id, order.shop_id)

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.error("order_cancellation_failed", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")


@router.get("/{order_id}/history", response_model=list[OrderHistoryRead])
async def get_order_history(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """Get change history for an order"""

    # Verify order exists
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Query history records
    statement = select(OrderHistory).where(
        OrderHistory.order_id == order_id
    ).order_by(OrderHistory.changed_at.desc())

    result = await session.execute(statement)
    history_records = result.scalars().all()

    return history_records
