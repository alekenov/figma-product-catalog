"""
Orders Photo Router - Photo upload and management

Handles order photo uploads to Cloudflare R2, photo deletion,
customer feedback on photos, and test photo endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import httpx

from database import get_session
from models import Order, OrderRead, OrderPhoto, OrderPhotoRead, OrderStatus, OrderHistory
from services.order_service import OrderService
from auth_utils import get_current_user_shop_id
from .helpers import load_order_with_relations, get_order_by_tracking_id
from datetime import datetime

router = APIRouter()

# Cloudflare Worker URL for image uploads
IMAGE_WORKER_URL = "https://flower-shop-images.alekenov.workers.dev"


@router.post("/{order_id}/photo")
async def upload_order_photo(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int,
    file: UploadFile = File(...),
):
    """
    Upload photo for order (before delivery).

    - Uploads photo to Cloudflare R2
    - Saves photo URL in database
    - Automatically changes order status to ASSEMBLED
    - Only 1 photo per order (replaces existing)
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")

    await file.seek(0)  # Reset file pointer

    try:
        # Upload to Cloudflare Worker
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {
                'file': (file.filename, contents, file.content_type)
            }

            response = await client.post(
                f"{IMAGE_WORKER_URL}/upload",
                files=files
            )

            if response.status_code != 201:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload image to storage: {error_data.get('error', 'Unknown error')}"
                )

            result = response.json()
            photo_url = result.get('url')

            if not photo_url:
                raise HTTPException(status_code=500, detail="No URL returned from image storage")

        # Delete existing photo for this order (only 1 photo allowed)
        existing_photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == "delivery"
        )
        existing_photos_result = await session.execute(existing_photos_query)
        existing_photos = list(existing_photos_result.scalars().all())

        for existing_photo in existing_photos:
            await session.delete(existing_photo)

        # Create new photo record
        new_photo = OrderPhoto(
            order_id=order_id,
            photo_url=photo_url,
            photo_type="delivery",
            label="Фото до доставки"
        )
        session.add(new_photo)

        # Automatically change status to ASSEMBLED
        old_status = order.status
        if old_status != OrderStatus.ASSEMBLED:
            order.status = OrderStatus.ASSEMBLED

            # Create history record
            history = OrderHistory(
                order_id=order_id,
                field_name="status",
                old_value=old_status.value,
                new_value=OrderStatus.ASSEMBLED.value,
                changed_by="admin"
            )
            session.add(history)

        await session.commit()
        await session.refresh(new_photo)

        return {
            "success": True,
            "photo_url": photo_url,
            "photo_id": new_photo.id,
            "message": "Photo uploaded successfully and order status changed to ASSEMBLED"
        }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to image storage: {str(e)}")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@router.delete("/{order_id}/photo")
async def delete_order_photo(
    *,
    session: AsyncSession = Depends(get_session),
    order_id: int
):
    """
    Delete photo from order.

    - Removes photo record from database
    - Changes order status back to ACCEPTED
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        # Find and delete photo
        photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == "delivery"
        )
        photos_result = await session.execute(photos_query)
        photos = list(photos_result.scalars().all())

        if not photos:
            raise HTTPException(status_code=404, detail="No photo found for this order")

        # Delete photo record
        for photo in photos:
            await session.delete(photo)

        # Change status back to ACCEPTED
        old_status = order.status
        if old_status != OrderStatus.ACCEPTED:
            order.status = OrderStatus.ACCEPTED

            # Create history record
            history = OrderHistory(
                order_id=order_id,
                field_name="status",
                old_value=old_status.value,
                new_value=OrderStatus.ACCEPTED.value,
                changed_by="admin"
            )
            session.add(history)

        await session.commit()

        return {
            "success": True,
            "message": "Photo deleted successfully and order status changed to ACCEPTED"
        }

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete photo: {str(e)}")


class PhotoCreateRequest(BaseModel):
    """Request model for creating photo record directly (testing only)"""
    photo_url: str = Field(..., description="Photo URL")
    photo_type: str = Field(default="delivery", description="Photo type")
    label: Optional[str] = Field(None, description="Photo label")


@router.post("/{order_id}/photo/test")
async def create_order_photo_test(
    *,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Depends(get_current_user_shop_id),
    order_id: int,
    photo_data: PhotoCreateRequest
):
    """
    Create photo record directly without file upload (for testing).

    **Testing endpoint only** - creates OrderPhoto record with provided URL.
    Used by automated tests to create photo records before testing feedback.
    """

    # Get existing order
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to shop
    if order.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Order does not belong to your shop")

    try:
        # Delete existing photo for this order (only 1 photo allowed)
        existing_photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == photo_data.photo_type
        )
        existing_photos_result = await session.execute(existing_photos_query)
        existing_photos = list(existing_photos_result.scalars().all())

        for existing_photo in existing_photos:
            await session.delete(existing_photo)

        # Create new photo record
        new_photo = OrderPhoto(
            order_id=order_id,
            photo_url=photo_data.photo_url,
            photo_type=photo_data.photo_type,
            label=photo_data.label or "Test photo"
        )
        session.add(new_photo)

        await session.commit()
        await session.refresh(new_photo)

        return {
            "success": True,
            "photo_url": new_photo.photo_url,
            "photo_id": new_photo.id,
            "message": "Photo record created successfully"
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create photo record: {str(e)}")


class PhotoFeedbackRequest(BaseModel):
    """Request model for photo feedback"""
    feedback: str = Field(..., description="Client feedback: 'like' or 'dislike'")
    comment: Optional[str] = Field(None, description="Optional comment (required for dislike)")


@router.post("/by-tracking/{tracking_id}/photo/feedback")
async def submit_photo_feedback_by_tracking(
    *,
    session: AsyncSession = Depends(get_session),
    tracking_id: str,
    feedback_data: PhotoFeedbackRequest
):
    """
    Submit customer feedback for order photo by tracking ID.

    - Accepts like/dislike feedback
    - Optional comment (especially for dislikes)
    - Creates order history entry
    - Updates photo record with feedback
    """

    # Validate feedback type
    if feedback_data.feedback not in ["like", "dislike"]:
        raise HTTPException(
            status_code=400,
            detail="Feedback must be 'like' or 'dislike'"
        )

    # Find order by tracking ID
    order = await get_order_by_tracking_id(session, tracking_id)
    order_id = order.id

    try:
        # Find order photo
        photos_query = select(OrderPhoto).where(
            OrderPhoto.order_id == order_id,
            OrderPhoto.photo_type == "delivery"
        )
        photos_result = await session.execute(photos_query)
        photo = photos_result.scalar_one_or_none()

        if not photo:
            raise HTTPException(
                status_code=404,
                detail="No photo found for this order. Cannot submit feedback."
            )

        # Check if feedback already submitted
        if photo.client_feedback:
            raise HTTPException(
                status_code=400,
                detail="Feedback already submitted for this photo"
            )

        # Update photo with feedback
        photo.client_feedback = feedback_data.feedback
        photo.client_comment = feedback_data.comment
        photo.feedback_at = datetime.now()

        # Create history entry
        feedback_icon = "👍" if feedback_data.feedback == "like" else "👎"
        history_message = f"{feedback_icon} {feedback_data.feedback.capitalize()}"
        if feedback_data.comment:
            history_message += f": {feedback_data.comment}"

        history = OrderHistory(
            order_id=order_id,
            field_name="photo_feedback",
            old_value=None,
            new_value=history_message,
            changed_by="customer"
        )
        session.add(history)

        await session.commit()
        await session.refresh(photo)

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback": {
                "type": photo.client_feedback,
                "comment": photo.client_comment,
                "submitted_at": photo.feedback_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


# ===============================
