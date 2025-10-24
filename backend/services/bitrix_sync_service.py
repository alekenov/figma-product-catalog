"""
Bitrix Sync Service

Handles synchronization of products and orders from Railway to Production Bitrix.
Provides HTTP client for updating products, orders, and statuses in Bitrix.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from core.logging import get_logger

logger = get_logger(__name__)

# Configuration
BITRIX_BASE_URL = "https://cvety.kz"
BITRIX_API_V2_BASE = f"{BITRIX_BASE_URL}/api/v2"
BITRIX_API_TOKEN = "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"  # Read from env in production


class BitrixSyncService:
    """Service for synchronizing data to Production Bitrix"""

    def __init__(self):
        self.base_url = BITRIX_API_V2_BASE
        self.token = BITRIX_API_TOKEN
        self.timeout = 30.0

    def _format_price(self, price_kopecks: int) -> str:
        """
        Convert price from kopecks to Bitrix format with symbol.

        Args:
            price_kopecks: Price in kopecks (e.g., 495000)

        Returns:
            Formatted price string (e.g., "4 950 ₸")
        """
        if not price_kopecks:
            return "0 ₸"

        # Convert kopecks to tenge (divide by 100)
        price_tenge = price_kopecks / 100
        # Format with space as thousands separator
        formatted = f"{price_tenge:,.0f}".replace(",", " ")
        return f"{formatted} ₸"

    async def sync_product_to_bitrix(
        self,
        product_id: int,
        name: str,
        price: int,  # kopecks
        image: str,
        enabled: bool,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync product to Production Bitrix via HTTP request.

        This method sends a PUT request to Bitrix API to update product details
        including name, price, image, enabled status, and description.

        Args:
            product_id: Product ID (must match Bitrix product ID)
            name: Product name/title
            price: Price in kopecks (e.g., 495000 = 4 950 ₸)
            image: Product image URL
            enabled: Whether product is available
            description: Optional product description

        Returns:
            Dict with keys:
            - success: bool
            - product_id: int
            - message: str
            - error: Optional[str]

        Example:
            ```python
            result = await bitrix_sync_service.sync_product_to_bitrix(
                product_id=668826,
                name="Эустомы в пачках ФИОЛЕТОВЫЕ",
                price=495000,
                image="https://example.com/image.jpg",
                enabled=True,
                description="Beautiful purple eustomas"
            )
            ```
        """
        try:
            # Format price for Bitrix
            formatted_price = self._format_price(price)

            # Prepare request payload
            payload = {
                "title": name,
                "price": formatted_price,
                "image": image,
                "isAvailable": enabled,
            }

            if description:
                payload["description"] = description

            logger.info(
                f"🔄 Syncing product {product_id} to Bitrix",
                product_id=product_id,
                price=formatted_price,
                enabled=enabled
            )

            # Make HTTP request to Bitrix
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/v2/products/update-from-railway"

                response = await client.put(
                    url,
                    json={
                        "id": product_id,
                        **payload
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.token}"
                    }
                )

                # Handle response
                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"✅ Product {product_id} synced to Bitrix",
                        product_id=product_id,
                        status_code=response.status_code
                    )
                    return {
                        "success": result.get("success", True),
                        "product_id": product_id,
                        "message": f"Product {product_id} updated in Bitrix",
                        "error": None
                    }

                elif response.status_code == 401:
                    logger.error(f"❌ Bitrix auth failed for product {product_id}")
                    return {
                        "success": False,
                        "product_id": product_id,
                        "message": "Authentication failed with Bitrix API",
                        "error": "Invalid API token"
                    }

                elif response.status_code == 404:
                    logger.warning(f"⚠️ Product {product_id} not found in Bitrix")
                    return {
                        "success": False,
                        "product_id": product_id,
                        "message": f"Product {product_id} not found in Bitrix",
                        "error": "Product not found"
                    }

                else:
                    logger.error(
                        f"❌ Bitrix API error for product {product_id}: {response.status_code}",
                        status_code=response.status_code,
                        response_text=response.text
                    )
                    return {
                        "success": False,
                        "product_id": product_id,
                        "message": f"Bitrix API error: {response.status_code}",
                        "error": response.text
                    }

        except httpx.TimeoutException:
            logger.error(f"❌ Bitrix sync timeout for product {product_id}")
            return {
                "success": False,
                "product_id": product_id,
                "message": "Timeout connecting to Bitrix",
                "error": "Request timeout"
            }

        except Exception as e:
            logger.error(f"❌ Bitrix sync error for product {product_id}: {e}")
            return {
                "success": False,
                "product_id": product_id,
                "message": "Failed to sync product to Bitrix",
                "error": str(e)
            }

    async def sync_order_status_to_bitrix(
        self,
        bitrix_order_id: int,
        railway_status: str
    ) -> Dict[str, Any]:
        """
        Sync order status back to Bitrix (if needed in future).

        Currently, status changes are one-way: Bitrix → Railway.
        This method is a placeholder for future bidirectional sync.

        Args:
            bitrix_order_id: Order ID in Bitrix
            railway_status: Order status in Railway (new, paid, accepted, etc.)

        Returns:
            Dict with sync result
        """
        logger.info(
            f"ℹ️ Order status sync to Bitrix not implemented",
            bitrix_order_id=bitrix_order_id,
            status=railway_status
        )
        return {
            "success": False,
            "message": "One-way sync: Bitrix → Railway only",
            "error": "Not implemented"
        }


# Singleton instance
_bitrix_sync_service = None


def get_bitrix_sync_service() -> BitrixSyncService:
    """Get or create BitrixSyncService singleton"""
    global _bitrix_sync_service
    if _bitrix_sync_service is None:
        _bitrix_sync_service = BitrixSyncService()
    return _bitrix_sync_service
