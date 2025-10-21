"""
Visual Search API - Find similar products using image embeddings

This module provides endpoints for visual similarity search using pgvector
and Vertex AI embeddings. It enables users to find visually similar products
by uploading an image or providing an image URL.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, text
from pydantic import BaseModel, Field
import logging

from database import get_session
from models import Product, ProductEmbedding
from services.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Embedding Client
embedding_client = EmbeddingClient()


class VisualSearchRequest(BaseModel):
    """Request for visual similarity search."""
    image_url: Optional[str] = Field(None, description="URL of the query image")
    image_base64: Optional[str] = Field(None, description="Base64-encoded image (data URI or raw base64)")
    shop_id: int = Field(..., description="Shop ID to search within")
    limit: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    topK: Optional[int] = Field(None, ge=1, le=50, description="Alias for limit (Cloudflare compatibility)")
    min_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score (0-1)")


class SimilarProduct(BaseModel):
    """Similar product result with similarity score."""
    id: int
    name: str
    price: int
    image: Optional[str]
    type: str
    enabled: bool
    similarity: float = Field(..., description="Similarity score (0-1, higher is more similar)")


class VisualSearchResponse(BaseModel):
    """Response with similar products."""
    success: bool
    query_image_url: Optional[str] = None
    exact: List[SimilarProduct] = Field([], description="Products with >85% similarity")
    similar: List[SimilarProduct] = Field([], description="Products with 70-85% similarity")
    total_results: int
    results: List[SimilarProduct]  # All results (deprecated, use exact+similar)
    search_duration_ms: int
    search_time_ms: int  # Alias for Cloudflare compatibility
    total_indexed: int
    method: str = "pgvector"


@router.post("/products/search/similar", response_model=VisualSearchResponse)
async def search_similar_products(
    request: VisualSearchRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Find visually similar products using image embeddings.

    Process:
    1. Generate embedding for query image (via Embedding Service)
    2. Use pgvector cosine distance to find similar products
    3. Return top N products sorted by similarity

    Args:
        request: Query image URL, shop_id, limit, min_similarity
        session: Database session

    Returns:
        VisualSearchResponse with similar products and similarity scores

    Example:
        ```bash
        curl -X POST "http://localhost:8014/api/v1/products/search/similar" \\
          -H "Content-Type: application/json" \\
          -d '{
            "image_url": "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png",
            "shop_id": 8,
            "limit": 5,
            "min_similarity": 0.5
          }'
        ```

    SQL Query (using pgvector):
        ```sql
        SELECT
          p.id,
          p.name,
          p.price,
          p.image,
          p.type,
          p.enabled,
          1 - (pe.embedding <=> :query_vector) AS similarity
        FROM products p
        JOIN product_embeddings pe ON p.id = pe.product_id
        WHERE p.shop_id = :shop_id
          AND p.enabled = true
          AND pe.embedding_type = 'image'
          AND (1 - (pe.embedding <=> :query_vector)) >= :min_similarity
        ORDER BY pe.embedding <=> :query_vector ASC
        LIMIT :limit;
        ```
    """
    import time
    import base64
    start_time = time.time()

    try:
        # Handle topK alias for Cloudflare compatibility
        limit = request.topK if request.topK is not None else request.limit

        # Validate that at least one image source is provided
        if not request.image_url and not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="Either image_url or image_base64 must be provided"
            )

        # Step 1: Get image for embedding generation
        if request.image_url:
            logger.info(f"Visual search: generating embedding for {request.image_url[:80]}...")
            query_embedding = await embedding_client.generate_image_embedding(
                image_url=request.image_url,
                product_id=None  # Not associated with a product
            )
        else:
            # Handle base64 image
            logger.info("Visual search: generating embedding from base64 image...")
            # Remove data URI prefix if present
            image_data = request.image_base64
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]

            # Decode base64 and save temporarily or use embedding service directly
            # For now, we need to pass as URL to embedding_client
            # Create data URI for embedding client
            data_uri = f"data:image/jpeg;base64,{image_data}"
            query_embedding = await embedding_client.generate_image_embedding(
                image_url=data_uri,
                product_id=None
            )

        if not query_embedding:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate embedding for query image"
            )

        logger.info(f"Query embedding generated: {len(query_embedding)} dimensions")

        # Step 2: Search for similar products using pgvector
        # Convert list to PostgreSQL array literal format
        embedding_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Use direct string interpolation for ALL parameters
        # SQLAlchemy text() with asyncpg has issues with bind parameters when vectors are involved
        # This is safe: embedding is validated float array, other params are sanitized integers/floats
        query_str = f"""
            SELECT
                p.id,
                p.name,
                p.price,
                p.image,
                p.type,
                p.enabled,
                1 - (pe.embedding <=> '{embedding_literal}'::vector) AS similarity
            FROM product p
            JOIN product_embeddings pe ON p.id = pe.product_id
            WHERE p.shop_id = {request.shop_id}
              AND p.enabled = true
              AND pe.embedding_type = 'image'
              AND (1 - (pe.embedding <=> '{embedding_literal}'::vector)) >= {request.min_similarity}
            ORDER BY pe.embedding <=> '{embedding_literal}'::vector ASC
            LIMIT {limit}
        """

        result = await session.execute(text(query_str))
        rows = result.fetchall()

        # Step 3: Format results
        similar_products = [
            SimilarProduct(
                id=row.id,
                name=row.name,
                price=row.price,
                image=row.image,
                type=row.type,
                enabled=row.enabled,
                similarity=round(float(row.similarity), 4)
            )
            for row in rows
        ]

        # Split into exact (>=0.85) and similar (0.70-0.85) categories
        exact = [p for p in similar_products if p.similarity >= 0.85]
        similar = [p for p in similar_products if 0.70 <= p.similarity < 0.85]

        # Get total indexed count
        count_query = text(f"""
            SELECT COUNT(DISTINCT pe.product_id) as total
            FROM product_embeddings pe
            JOIN product p ON p.id = pe.product_id
            WHERE p.shop_id = {request.shop_id}
              AND p.enabled = true
              AND pe.embedding_type = 'image'
        """)
        count_result = await session.execute(count_query)
        total_indexed = count_result.scalar() or 0

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Visual search completed: {len(exact)} exact, {len(similar)} similar, "
            f"{len(similar_products)} total, {duration_ms}ms"
        )

        return VisualSearchResponse(
            success=True,
            query_image_url=request.image_url,
            exact=exact,
            similar=similar,
            total_results=len(similar_products),
            results=similar_products,  # All results for backward compatibility
            search_duration_ms=duration_ms,
            search_time_ms=duration_ms,  # Cloudflare compatibility
            total_indexed=total_indexed,
            method="pgvector"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Visual search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Visual search failed: {str(e)}"
        )


@router.get("/products/search/stats")
async def get_search_stats(
    shop_id: int = Query(..., description="Shop ID"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get visual search statistics for a shop.

    Returns:
        - Total products with embeddings
        - Embedding coverage percentage
        - Average embedding generation time
    """
    try:
        # Count total products
        total_products_query = select(Product).where(
            Product.shop_id == shop_id,
            Product.enabled == True
        )
        total_result = await session.execute(total_products_query)
        total_products = len(total_result.scalars().all())

        # Count products with embeddings
        # Use string interpolation for all parameters (same issue as similarity search)
        embeddings_query = text(f"""
            SELECT COUNT(DISTINCT pe.product_id)
            FROM product_embeddings pe
            JOIN product p ON p.id = pe.product_id
            WHERE p.shop_id = {shop_id}
              AND p.enabled = true
              AND pe.embedding_type = 'image'
        """)
        embeddings_result = await session.execute(embeddings_query)
        products_with_embeddings = embeddings_result.scalar() or 0

        coverage_percentage = (
            round((products_with_embeddings / total_products) * 100, 2)
            if total_products > 0
            else 0.0
        )

        return {
            "success": True,
            "shop_id": shop_id,
            "total_products": total_products,
            "products_with_embeddings": products_with_embeddings,
            "coverage_percentage": coverage_percentage,
            "search_ready": products_with_embeddings > 0
        }

    except Exception as e:
        logger.error(f"Failed to get search stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get search stats: {str(e)}"
        )


@router.get("/products/embeddings/list")
async def list_products_with_embeddings(
    shop_id: int = Query(..., description="Shop ID"),
    session: AsyncSession = Depends(get_session)
):
    """
    List all products that have embeddings in pgvector (DEBUG endpoint).

    Returns detailed information about each product with embeddings including:
    - Product ID, name, enabled status
    - Embedding metadata (type, model, created_at)
    - Image URL used for embedding
    """
    try:
        # Query products with embeddings (simplified for SQLite/PostgreSQL compatibility)
        query = text(f"""
            SELECT
                p.id,
                p.name,
                p.enabled,
                p.image,
                pe.embedding_type,
                pe.model_version,
                pe.source_url,
                pe.created_at
            FROM product p
            JOIN product_embeddings pe ON p.id = pe.product_id
            WHERE p.shop_id = {shop_id}
              AND pe.embedding_type = 'image'
            ORDER BY pe.created_at DESC
        """)
        result = await session.execute(query)
        rows = result.fetchall()

        products_with_embeddings = [
            {
                "product_id": row.id,
                "name": row.name,
                "enabled": row.enabled,
                "image_url": row.image,
                "embedding_type": row.embedding_type,
                "model_version": row.model_version,
                "source_url": row.source_url,
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in rows
        ]

        return {
            "success": True,
            "shop_id": shop_id,
            "total_count": len(products_with_embeddings),
            "products": products_with_embeddings
        }

    except Exception as e:
        logger.error(f"Failed to list products with embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list products with embeddings: {str(e)}"
        )
