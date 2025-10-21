"""
Embedding Service - Business logic for embedding generation

This module provides high-level embedding generation functionality with:
- Batch processing with concurrency control
- Retry logic for failed requests
- Progress tracking and error handling
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx

from .vertex_ai import VertexAIClient

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    High-level service for generating embeddings.

    Provides batch processing, concurrency control, and error handling
    on top of the raw Vertex AI client.

    Attributes:
        vertex_client: VertexAIClient instance
        max_concurrent: Maximum concurrent API requests (default: 5)
        max_retries: Maximum retry attempts for failed requests (default: 2)
    """

    def __init__(
        self,
        vertex_client: VertexAIClient,
        max_concurrent: int = 5,
        max_retries: int = 2
    ):
        """
        Initialize embedding service.

        Args:
            vertex_client: Configured VertexAIClient
            max_concurrent: Max concurrent requests (default: 5)
            max_retries: Max retry attempts (default: 2)
        """
        self.vertex_client = vertex_client
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrent)

        logger.info(
            f"Embedding service initialized "
            f"(max_concurrent={max_concurrent}, max_retries={max_retries})"
        )

    async def generate_image_embedding(
        self,
        image_bytes: bytes,
        dimension: Optional[int] = None
    ) -> List[float]:
        """
        Generate embedding for a single image.

        Args:
            image_bytes: Image data as bytes
            dimension: Optional custom embedding dimension

        Returns:
            List[float]: Normalized embedding vector (512D by default)

        Raises:
            Exception: If embedding generation fails after retries
        """
        for attempt in range(self.max_retries + 1):
            try:
                embedding = await self.vertex_client.generate_image_embedding(
                    image_bytes=image_bytes,
                    dimension=dimension
                )
                return embedding

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Embedding generation failed after {self.max_retries + 1} attempts")
                    raise

    async def generate_text_embedding(
        self,
        text: str,
        dimension: Optional[int] = None
    ) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text
            dimension: Optional custom embedding dimension

        Returns:
            List[float]: Normalized embedding vector (512D by default)

        Raises:
            Exception: If embedding generation fails after retries
        """
        for attempt in range(self.max_retries + 1):
            try:
                embedding = await self.vertex_client.generate_text_embedding(
                    text=text,
                    dimension=dimension
                )
                return embedding

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Text embedding generation failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Text embedding generation failed after {self.max_retries + 1} attempts")
                    raise

    async def batch_generate_embeddings(
        self,
        image_urls: List[str],
        dimension: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Batch generate embeddings for multiple images.

        Processes images in parallel with concurrency control to avoid
        overwhelming the Vertex AI API.

        Args:
            image_urls: List of image URLs
            dimension: Optional custom embedding dimension

        Returns:
            List of dicts with results:
            [
                {
                    "image_url": "https://...",
                    "success": True,
                    "embedding": [0.1, 0.2, ...],
                    "error": None
                },
                ...
            ]
        """
        logger.info(f"Starting batch embedding generation for {len(image_urls)} images")

        # Create tasks for all images
        tasks = [
            self._process_single_image(url, dimension)
            for url in image_urls
        ]

        # Process with concurrency control
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes and failures
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful

        logger.info(
            f"Batch embedding completed: {successful} successful, {failed} failed "
            f"out of {len(image_urls)} total"
        )

        return results

    async def _process_single_image(
        self,
        image_url: str,
        dimension: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a single image with concurrency control.

        Args:
            image_url: Image URL
            dimension: Optional custom embedding dimension

        Returns:
            Dict with result:
            {
                "image_url": str,
                "success": bool,
                "embedding": List[float] or None,
                "error": str or None
            }
        """
        async with self.semaphore:  # Limit concurrency
            try:
                # Download image
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    image_bytes = response.content

                # Generate embedding
                embedding = await self.generate_image_embedding(
                    image_bytes=image_bytes,
                    dimension=dimension
                )

                return {
                    "image_url": image_url,
                    "success": True,
                    "embedding": embedding,
                    "error": None
                }

            except Exception as e:
                logger.error(f"Failed to process image {image_url}: {e}")
                return {
                    "image_url": image_url,
                    "success": False,
                    "embedding": None,
                    "error": str(e)
                }

    async def batch_generate_text_embeddings(
        self,
        texts: List[str],
        dimension: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Batch generate embeddings for multiple texts.

        Args:
            texts: List of text strings
            dimension: Optional custom embedding dimension

        Returns:
            List of dicts with results:
            [
                {
                    "text": "...",
                    "success": True,
                    "embedding": [0.1, 0.2, ...],
                    "error": None
                },
                ...
            ]
        """
        logger.info(f"Starting batch text embedding generation for {len(texts)} texts")

        # Create tasks for all texts
        tasks = [
            self._process_single_text(text, dimension)
            for text in texts
        ]

        # Process with concurrency control
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes and failures
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful

        logger.info(
            f"Batch text embedding completed: {successful} successful, {failed} failed "
            f"out of {len(texts)} total"
        )

        return results

    async def _process_single_text(
        self,
        text: str,
        dimension: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a single text with concurrency control.

        Args:
            text: Input text
            dimension: Optional custom embedding dimension

        Returns:
            Dict with result:
            {
                "text": str,
                "success": bool,
                "embedding": List[float] or None,
                "error": str or None
            }
        """
        async with self.semaphore:  # Limit concurrency
            try:
                # Generate embedding
                embedding = await self.generate_text_embedding(
                    text=text,
                    dimension=dimension
                )

                return {
                    "text": text[:50] + "..." if len(text) > 50 else text,  # Truncate for logging
                    "success": True,
                    "embedding": embedding,
                    "error": None
                }

            except Exception as e:
                logger.error(f"Failed to process text '{text[:50]}...': {e}")
                return {
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "success": False,
                    "embedding": None,
                    "error": str(e)
                }
