"""
Embedding Client Service

This module provides a client for communicating with the Embedding Service
to generate vector embeddings for products.
"""
import os
import logging
from typing import List, Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Client for Embedding Service API.

    Handles communication with the standalone Embedding Service (Railway)
    to generate 512D vector embeddings for product images.

    Attributes:
        service_url: Base URL of Embedding Service
        timeout: HTTP timeout in seconds (default: 30)
    """

    def __init__(self, service_url: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize embedding client.

        Args:
            service_url: Embedding Service URL (defaults to env var)
            timeout: HTTP timeout in seconds
        """
        self.service_url = service_url or os.getenv(
            "EMBEDDING_SERVICE_URL",
            "http://localhost:8001"  # Default for local development
        )
        self.timeout = timeout

        # Remove trailing slash
        self.service_url = self.service_url.rstrip("/")

        logger.info(f"Embedding client initialized (service_url={self.service_url})")

    async def health_check(self) -> bool:
        """
        Check if Embedding Service is healthy.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/health")
                response.raise_for_status()
                data = response.json()
                return data.get("status") == "healthy"

        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}")
            return False

    async def generate_image_embedding(
        self,
        image_url: str,
        product_id: Optional[int] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for a single image.

        Args:
            image_url: URL of the image to process
            product_id: Optional product ID for logging

        Returns:
            List[float]: 512D embedding vector, or None if failed

        Raises:
            Exception: If service is unreachable or returns error
        """
        try:
            logger.info(f"Generating embedding for product {product_id}: {image_url[:80]}...")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.service_url}/embed/image",
                    json={
                        "image_url": image_url,
                        "product_id": product_id
                    }
                )
                response.raise_for_status()

            data = response.json()

            if not data.get("success"):
                logger.error(f"Embedding generation failed for product {product_id}")
                return None

            embedding = data.get("embedding")
            dimensions = data.get("dimensions", 0)
            duration_ms = data.get("duration_ms", 0)

            logger.info(
                f"✅ Generated embedding for product {product_id}: "
                f"{dimensions} dims, {duration_ms}ms"
            )

            return embedding

        except httpx.HTTPError as e:
            logger.error(f"HTTP error while generating embedding for product {product_id}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise

        except Exception as e:
            logger.error(f"Failed to generate embedding for product {product_id}: {e}")
            raise

    async def generate_batch_embeddings(
        self,
        image_urls: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple images in batch.

        This is more efficient than calling generate_image_embedding() multiple times,
        as the Embedding Service processes them in parallel.

        Args:
            image_urls: List of image URLs (max 50)

        Returns:
            List of dicts with results:
            [
                {
                    "image_url": str,
                    "success": bool,
                    "embedding": List[float] or None,
                    "error": str or None
                },
                ...
            ]

        Raises:
            Exception: If service is unreachable
        """
        if not image_urls:
            return []

        if len(image_urls) > 50:
            logger.warning(f"Batch size {len(image_urls)} exceeds maximum 50, truncating")
            image_urls = image_urls[:50]

        try:
            logger.info(f"Generating batch embeddings for {len(image_urls)} images")

            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:  # Double timeout for batch
                response = await client.post(
                    f"{self.service_url}/embed/batch",
                    json={"image_urls": image_urls}
                )
                response.raise_for_status()

            data = response.json()

            total = data.get("total", 0)
            successful = data.get("successful", 0)
            failed = data.get("failed", 0)
            duration_ms = data.get("duration_ms", 0)

            logger.info(
                f"✅ Batch embedding completed: {successful} success, {failed} failed "
                f"out of {total} total ({duration_ms}ms, {duration_ms / total if total > 0 else 0:.0f}ms avg)"
            )

            return data.get("results", [])

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during batch embedding generation: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    async def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get Embedding Service statistics.

        Returns:
            Dict with service stats:
            {
                "service": str,
                "status": str,
                "uptime_seconds": float,
                "total_requests": int,
                "successful_requests": int,
                "failed_requests": int,
                "average_duration_ms": float
            }

        Returns None if service is unreachable.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/stats")
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get embedding service stats: {e}")
            return None
