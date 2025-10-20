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
from models import Product, ProductImage, ProductCreate, ProductType

logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me-in-production")
VISUAL_SEARCH_API = "https://visual-search.alekenov.workers.dev"
PRODUCTION_SHOP_ID = 17008
RAILWAY_SHOP_ID = 8


def parse_price(price_str: str) -> int:
    """
    Parse Production price string to kopecks.

    Examples:
        "4 950 ₸" -> 495000
        "27 325 ₸" -> 2732500
        "12000" -> 1200000
    """
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


def parse_dimension(dim_str: Optional[str]) -> Optional[int]:
    """
    Parse dimension string to integer.

    Examples:
        "70 см" -> 70
        "60см" -> 60
        "" -> None
    """
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

        # Trigger visual search reindex in background
        # Only if product is enabled (not deleted)
        should_reindex = event_type in ["product.created", "product.updated"]

        if should_reindex:
            background_tasks.add_task(trigger_visual_search_reindex, product_id)

        return {
            "status": "success",
            "action": action,
            "product_id": product_id,
            "reindex_triggered": should_reindex
        }

    except Exception as e:
        logger.error(f"❌ Webhook processing failed for product {product_id}: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")
