"""
Webhooks API for receiving events from Production Bitrix system.

This module handles real-time synchronization of products from Production (cvety.kz)
to Railway backend, triggering visual search reindexing when products change.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select
import httpx
import logging
import os

from database import get_session
from models import (
    Product, ProductImage, ProductCreate, ProductType, ProductEmbedding,
    Order, OrderHistory, OrderStatus
)
from services.embedding_client import EmbeddingClient
from utils import get_logger

logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me-in-production")
VISUAL_SEARCH_API = "https://visual-search.alekenov.workers.dev"
PRODUCTION_SHOP_ID = 17008
RAILWAY_SHOP_ID = 8

# Status mapping: Bitrix → Railway
BX_TO_RAILWAY_STATUS = {
    'N': OrderStatus.NEW,           # Новый
    'PD': OrderStatus.PAID,         # Оплачен
    'AP': OrderStatus.ACCEPTED,     # Принят
    'CO': OrderStatus.IN_PRODUCTION,  # Собран
    'DE': OrderStatus.IN_DELIVERY,  # В пути
    'F': OrderStatus.DELIVERED,     # Доставлен
    'RF': OrderStatus.CANCELLED,    # Возврат
    'UN': OrderStatus.CANCELLED,    # Не реализован
}

# Initialize Embedding Client
embedding_client = EmbeddingClient()


def parse_price(price_str) -> int:
    """
    Parse Production price string to kopecks.

    Examples:
        "4 950 ₸" -> 495000
        "27 325 ₸" -> 2732500
        "12000" -> 1200000
        15000 -> 1500000 (int input)
    """
    # Handle numeric inputs (int or float)
    if isinstance(price_str, (int, float)):
        return int(price_str) * 100

    if not price_str:
        return 0

    # Remove spaces, ₸ symbol, and parse
    cleaned = price_str.replace(" ", "").replace("₸", "").replace(",", "")

    try:
        price_tenge = int(float(cleaned))
        return price_tenge * 100  # Convert to kopecks
    except ValueError:
        logger.warning(f"Failed to parse price: {price_str}")
        return 0


def parse_dimension(dim_str) -> Optional[int]:
    """
    Parse dimension string to integer.

    Examples:
        "70 см" -> 70
        "60см" -> 60
        "" -> None
        70 -> 70 (int input)
    """
    # Handle numeric inputs (int or float)
    if isinstance(dim_str, (int, float)):
        return int(dim_str)

    if not dim_str:
        return None

    # Remove "см", spaces
    cleaned = dim_str.lower().replace("см", "").replace(" ", "").strip()

    if not cleaned:
        return None

    try:
        return int(float(cleaned))
    except ValueError:
        logger.warning(f"Failed to parse dimension: {dim_str}")
        return None


def production_to_railway_product(production_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Production Bitrix product format to Railway backend format.

    Production format:
    {
        "id": 668826,
        "title": "Эустомы в пачках ФИОЛЕТОВЫЕ",
        "price": "4 950 ₸",
        "isAvailable": true,
        "image": "https://cvety.kz/upload/.../IMG_0254.jpeg",
        "images": ["url1", "url2", "url3"],
        "catalogHeight": "70 см",
        "catalogWidth": "",
        "type": "catalog",
        "colors": false,
        "createdAt": "2025-04-24T17:01:07+0500"
    }

    Railway format:
    {
        "id": 668826,
        "name": "Эустомы в пачках ФИОЛЕТОВЫЕ",
        "price": 495000,  # kopecks
        "enabled": true,
        "image": "https://cvety.kz/upload/.../IMG_0254.jpeg",
        "height": 70,
        "width": None,
        "type": "FLOWERS",
        "shop_id": 8
    }
    """
    return {
        "id": production_data.get("id"),
        "name": production_data.get("title", ""),
        "price": parse_price(production_data.get("price", "0")),
        "enabled": production_data.get("isAvailable", True),
        "image": production_data.get("image"),
        "height": parse_dimension(production_data.get("catalogHeight")),
        "width": parse_dimension(production_data.get("catalogWidth")),
        "type": ProductType.FLOWERS,  # Default to FLOWERS
        "shop_id": RAILWAY_SHOP_ID,
        "colors": [],  # Production has different color format
        "occasions": [],
        "tags": []
    }


async def generate_and_save_embedding(
    product_id: int,
    image_url: str
):
    """
    Generate embedding for product image and save to database.

    This function:
    1. Calls Embedding Service to generate 512D vector
    2. Saves ProductEmbedding to PostgreSQL with pgvector
    3. Enables vector similarity search for this product

    Args:
        product_id: Product ID
        image_url: URL of product image

    Note: This is a background task - errors are logged but don't fail the webhook.
    Creates its own database session to avoid using closed session from request handler.
    """
    try:
        logger.info(f"🔄 Generating embedding for product {product_id}")

        # Generate embedding via Embedding Service
        embedding = await embedding_client.generate_image_embedding(
            image_url=image_url,
            product_id=product_id
        )

        if not embedding:
            logger.error(f"❌ Failed to generate embedding for product {product_id}")
            return

        # Create new database session for background task
        from database import async_session
        async with async_session() as session:
            # Check if embedding already exists (update vs create)
            stmt = select(ProductEmbedding).where(
                ProductEmbedding.product_id == product_id,
                ProductEmbedding.embedding_type == "image"
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing embedding
                existing.embedding = embedding
                existing.model_version = "vertex-multimodal-001"
                existing.source_url = image_url
                logger.info(f"🔄 Updated embedding for product {product_id}")
            else:
                # Create new embedding
                product_embedding = ProductEmbedding(
                    product_id=product_id,
                    embedding=embedding,
                    embedding_type="image",
                    model_version="vertex-multimodal-001",
                    source_url=image_url
                )
                session.add(product_embedding)
                logger.info(f"✅ Created embedding for product {product_id}")

            await session.commit()

    except Exception as e:
        logger.error(f"❌ Failed to generate/save embedding for product {product_id}: {e}")


async def trigger_visual_search_reindex(product_id: int):
    """
    Trigger Visual Search Worker to reindex a single product.

    Calls POST /reindex-one endpoint on Visual Search Worker.
    Non-blocking operation - errors are logged but don't fail the webhook.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VISUAL_SEARCH_API}/reindex-one",
                json={"product_id": product_id, "shop_id": RAILWAY_SHOP_ID}
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Visual search reindexed product {product_id}: {result}")
            else:
                logger.warning(f"⚠️ Visual search reindex failed for product {product_id}: {response.status_code}")

    except Exception as e:
        logger.error(f"❌ Failed to trigger visual search reindex for product {product_id}: {e}")


class WebhookPayload(SQLModel):
    """Webhook payload from Production Bitrix"""
    event_type: str
    product_data: Dict[str, Any]


@router.post("/product-sync")
async def product_sync_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    x_webhook_secret: Optional[str] = Header(None)
):
    """
    Receive webhook from Production Bitrix system.

    Events:
    - "product.created": New product added in Production
    - "product.updated": Product modified in Production
    - "product.deleted": Product deleted or disabled in Production

    Request body:
    {
        "event_type": "product.created",
        "product_data": {
            "id": 668826,
            "title": "Эустомы",
            "price": "4 950 ₸",
            "isAvailable": true,
            "image": "https://cvety.kz/upload/.../IMG_0254.jpeg",
            "images": ["url1", "url2", "url3"],
            "catalogHeight": "70 см"
        }
    }

    Returns:
    {
        "status": "success",
        "action": "created|updated|deleted",
        "product_id": 668826,
        "reindex_triggered": true
    }
    """
    # Verify webhook secret (security)
    if x_webhook_secret != WEBHOOK_SECRET:
        logger.warning(f"❌ Webhook authentication failed: invalid secret")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    event_type = payload.event_type
    product_data = payload.product_data

    product_id = product_data.get("id")
    if not product_id:
        raise HTTPException(status_code=400, detail="Missing product_id in webhook data")

    logger.info(f"📨 Received webhook: {event_type} for product {product_id}")

    action = None

    try:
        if event_type == "product.created":
            # Create new product
            railway_data = production_to_railway_product(product_data)

            # Check if product already exists (idempotency)
            existing = await session.get(Product, product_id)
            if existing:
                logger.warning(f"⚠️ Product {product_id} already exists, updating instead")
                event_type = "product.updated"
            else:
                # Create product
                new_product = Product(**railway_data)
                session.add(new_product)
                await session.commit()
                await session.refresh(new_product)

                # Create product images
                images = product_data.get("images", [])
                for idx, img_url in enumerate(images):
                    product_image = ProductImage(
                        product_id=product_id,
                        url=img_url,
                        order=idx,
                        is_primary=(idx == 0)
                    )
                    session.add(product_image)

                await session.commit()
                logger.info(f"✅ Created product {product_id} with {len(images)} images")
                action = "created"

        if event_type == "product.updated":
            # Update existing product
            existing_product = await session.get(Product, product_id)

            if not existing_product:
                logger.warning(f"⚠️ Product {product_id} not found, creating instead")
                event_type = "product.created"
                # Retry as create
                railway_data = production_to_railway_product(product_data)
                new_product = Product(**railway_data)
                session.add(new_product)
                await session.commit()
                action = "created"
            else:
                # Update fields
                railway_data = production_to_railway_product(product_data)
                for key, value in railway_data.items():
                    if key != "id" and key != "shop_id":  # Don't update ID or shop_id
                        setattr(existing_product, key, value)

                await session.commit()

                # Update images (delete old, create new)
                # Delete existing images
                stmt = select(ProductImage).where(ProductImage.product_id == product_id)
                result = await session.execute(stmt)
                old_images = result.scalars().all()
                for img in old_images:
                    await session.delete(img)

                # Create new images
                images = product_data.get("images", [])
                for idx, img_url in enumerate(images):
                    product_image = ProductImage(
                        product_id=product_id,
                        url=img_url,
                        order=idx,
                        is_primary=(idx == 0)
                    )
                    session.add(product_image)

                await session.commit()
                logger.info(f"✅ Updated product {product_id} with {len(images)} images")
                action = "updated"

        elif event_type == "product.deleted":
            # Soft delete: set enabled=False
            existing_product = await session.get(Product, product_id)

            if not existing_product:
                logger.warning(f"⚠️ Product {product_id} not found for deletion")
                return {
                    "status": "success",
                    "action": "skipped",
                    "product_id": product_id,
                    "message": "Product not found"
                }

            existing_product.enabled = False
            await session.commit()
            logger.info(f"✅ Soft deleted product {product_id} (enabled=False)")
            action = "deleted"

        # Trigger background tasks for indexing
        # Only if product is enabled (not deleted)
        should_reindex = event_type in ["product.created", "product.updated"]

        if should_reindex:
            # 1. Generate and save embedding to PostgreSQL (pgvector)
            image_url = product_data.get("image")
            if image_url:
                background_tasks.add_task(
                    generate_and_save_embedding,
                    product_id,
                    image_url
                )

            # 2. Trigger visual search reindex (Cloudflare Worker)
            background_tasks.add_task(trigger_visual_search_reindex, product_id)

        return {
            "status": "success",
            "action": action,
            "product_id": product_id,
            "reindex_triggered": should_reindex,
            "embedding_generated": should_reindex and bool(product_data.get("image"))
        }

    except Exception as e:
        logger.error(f"❌ Webhook processing failed for product {product_id}: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")


# ===============================================
# Order Status Sync Webhook (Bitrix → Railway)
# ===============================================

class OrderStatusSyncPayload(SQLModel):
    """Order status sync payload from Bitrix"""
    order_id: int = Field(description="Bitrix order ID")
    status: str = Field(description="Bitrix order status (N, PD, AP, CO, DE, F, etc)")
    changed_by_id: Optional[int] = Field(default=None, description="Who changed the status (user ID in Bitrix)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the status change")


@router.post("/order-status-sync")
async def order_status_sync_webhook(
    payload: OrderStatusSyncPayload,
    session: AsyncSession = Depends(get_session),
    x_webhook_secret: Optional[str] = Header(None)
):
    """
    Bitrix → Railway: Sync order status changes

    Receives status updates from Production Bitrix and updates the corresponding
    order in Railway database.

    **Security:** Requires valid WEBHOOK_SECRET header

    **Request body:**
    ```json
    {
        "order_id": 123456,
        "status": "AP",
        "changed_by_id": 42,
        "notes": "Accepted by florist John"
    }
    ```

    **Returns:**
    ```json
    {
        "status": "success",
        "order_id": 123456,
        "railway_order_id": 789,
        "old_status": "new",
        "new_status": "accepted",
        "history_recorded": true
    }
    ```
    """
    # Verify webhook secret
    if x_webhook_secret != WEBHOOK_SECRET:
        logger.warning(f"❌ Order status webhook authentication failed: invalid secret")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    bitrix_order_id = payload.order_id
    bitrix_status = payload.status

    logger.info(f"📨 Received order status webhook: order_id={bitrix_order_id}, status={bitrix_status}")

    try:
        # Find order by bitrix_order_id
        stmt = select(Order).where(
            Order.bitrix_order_id == bitrix_order_id,
            Order.shop_id == PRODUCTION_SHOP_ID  # Only sync for production shop
        )
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            logger.warning(f"⚠️ Order with bitrix_order_id={bitrix_order_id} not found in Railway")
            return {
                "status": "skipped",
                "reason": "Order not found in Railway",
                "bitrix_order_id": bitrix_order_id
            }

        # Map Bitrix status to Railway status
        railway_status = BX_TO_RAILWAY_STATUS.get(bitrix_status)
        if not railway_status:
            logger.warning(f"⚠️ Unknown Bitrix status: {bitrix_status}")
            return {
                "status": "skipped",
                "reason": f"Unknown status: {bitrix_status}",
                "bitrix_order_id": bitrix_order_id
            }

        # Check if status is different
        old_status = order.status
        if old_status == railway_status:
            logger.info(f"ℹ️ Order status unchanged: {railway_status}")
            return {
                "status": "skipped",
                "reason": "Status unchanged",
                "bitrix_order_id": bitrix_order_id,
                "current_status": railway_status.value
            }

        # Update order status
        order.status = railway_status
        session.add(order)

        # Create history record
        history = OrderHistory(
            order_id=order.id,
            changed_by="bitrix",
            field_name="status",
            old_value=old_status.value if old_status else None,
            new_value=railway_status.value,
        )
        session.add(history)

        await session.commit()

        logger.info(
            f"✅ Updated order {order.id} (bitrix_id={bitrix_order_id}): "
            f"{old_status.value} → {railway_status.value}"
        )

        return {
            "status": "success",
            "railway_order_id": order.id,
            "bitrix_order_id": bitrix_order_id,
            "old_status": old_status.value if old_status else None,
            "new_status": railway_status.value,
            "history_recorded": True
        }

    except Exception as e:
        logger.error(f"❌ Order status sync failed for order {bitrix_order_id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync order status: {str(e)}"
        )
