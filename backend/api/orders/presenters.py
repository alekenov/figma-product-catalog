"""
Order Presenters - Response formatting and data transformation

Consolidates response building logic to eliminate duplication.
Handles mapping between backend models and frontend expectations.
"""

from typing import List, Dict, Any
from datetime import datetime
from models import (
    Order, OrderStatus, OrderItem, OrderPhoto,
    OrderRead, OrderItemRead, OrderPhotoRead
)


def map_status_to_frontend(status: OrderStatus) -> str:
    """
    Map backend OrderStatus to frontend vocabulary.
    Frontend OrderProgressBar expects: 'confirmed', 'preparing', 'delivering'
    """
    mapping = {
        OrderStatus.NEW: "confirmed",
        OrderStatus.PAID: "confirmed",
        OrderStatus.ACCEPTED: "confirmed",
        OrderStatus.ASSEMBLED: "preparing",
        OrderStatus.IN_DELIVERY: "delivering",
        OrderStatus.DELIVERED: "delivering",
        OrderStatus.CANCELLED: "confirmed"  # Show as first stage for cancelled
    }
    return mapping.get(status, "confirmed")


def format_delivery_datetime(order: Order) -> str:
    """Format delivery date/time for public display"""
    if order.delivery_date:
        return order.delivery_date.strftime("%A %d %B, %H:%M")
    elif order.created_at:
        return order.created_at.strftime("%A %d %B, %H:%M")
    return "Not specified"


def format_delivery_type(order: Order) -> str:
    """Format delivery type for public display"""
    if order.delivery_type == "express":
        return "Express 30 min"
    elif order.delivery_type == "scheduled" and order.scheduled_time:
        return f"Scheduled: {order.scheduled_time}"
    elif order.delivery_type == "pickup":
        return "Self Pickup"
    return "Standard Delivery"


def build_order_read(order: Order, items: List[OrderItem], photos: List[OrderPhoto] = None) -> OrderRead:
    """
    Build OrderRead response from order and related entities.
    Centralized to ensure consistent response formatting.
    """
    return OrderRead(
        id=order.id,
        tracking_id=order.tracking_id,
        orderNumber=order.orderNumber,
        customerName=order.customerName,
        phone=order.phone,
        customer_email=order.customer_email,
        delivery_address=order.delivery_address,
        delivery_date=order.delivery_date,
        delivery_notes=order.delivery_notes,
        subtotal=order.subtotal,
        delivery_cost=order.delivery_cost,
        total=order.total,
        status=order.status,
        notes=order.notes,
        # Phase 3 fields
        recipient_name=order.recipient_name,
        recipient_phone=order.recipient_phone,
        sender_phone=order.sender_phone,
        pickup_address=order.pickup_address,
        delivery_type=order.delivery_type,
        scheduled_time=order.scheduled_time,
        payment_method=order.payment_method,
        order_comment=order.order_comment,
        bonus_points=order.bonus_points,
        # Metadata
        created_at=order.created_at,
        updated_at=order.updated_at,
        # Relations
        items=[OrderItemRead.model_validate(item) for item in items],
        photos=[OrderPhotoRead.model_validate(photo) for photo in photos] if photos else []
    )


def build_public_status_response(order: Order, items: List[OrderItem], photos: List[OrderPhoto]) -> Dict[str, Any]:
    """
    Build public order status response for customer-facing tracking page.
    Used by both /by-tracking/{tracking_id}/status and /by-number/{order_number}/status endpoints.
    """
    # Extract feedback from first photo (there's only one delivery photo per order)
    photo_feedback = None
    photo_feedback_comment = None
    if photos:
        first_photo = photos[0]
        photo_feedback = first_photo.client_feedback
        photo_feedback_comment = first_photo.client_comment

    return {
        "tracking_id": order.tracking_id,
        "order_number": order.orderNumber,
        "status": map_status_to_frontend(order.status),
        "recipient": {
            "name": order.recipient_name or order.customerName,
            "phone": order.recipient_phone or order.phone
        },
        "pickup_address": order.pickup_address or "Store address not specified",
        "delivery_address": order.delivery_address or "Not specified",
        "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
        "date_time": format_delivery_datetime(order),
        "sender": {
            "phone": order.sender_phone or order.phone
        },
        "photos": [
            {
                "url": photo.photo_url,
                "label": photo.label or photo.photo_type,
                "feedback": photo.client_feedback,
                "comment": photo.client_comment
            }
            for photo in photos
        ],
        "photo_feedback": photo_feedback,
        "photo_feedback_comment": photo_feedback_comment,
        "items": [
            {
                "name": item.product_name,
                "price": item.item_total
            }
            for item in items
        ],
        "delivery_cost": order.delivery_cost,
        "delivery_type": format_delivery_type(order),
        "total": order.total,
        "bonus_points": order.bonus_points or 0,
        # Kaspi Pay integration
        "payment_method": order.payment_method,
        "kaspi_payment_id": order.kaspi_payment_id,
        "kaspi_payment_status": order.kaspi_payment_status,
        "kaspi_payment_created_at": order.kaspi_payment_created_at.isoformat() if order.kaspi_payment_created_at else None
    }
