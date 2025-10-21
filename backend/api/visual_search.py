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
    image_url: str = Field(..., description="URL of the query image")
    shop_id: int = Field(..., description="Shop ID to search within")
    limit: int = Field(default=5, ge=1, le=50, description="Number of results to return")
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
    query_image_url: str
    total_results: int
    results: List[SimilarProduct]
    search_duration_ms: int


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
    start_time = time.time()

    try:
        logger.info(f"Visual search: generating embedding for {request.image_url[:80]}...")

        # Step 1: Generate embedding for query image
        query_embedding = await embedding_client.generate_image_embedding(
            image_url=request.image_url,
            product_id=None  # Not associated with a product
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
            LIMIT {request.limit}
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

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Visual search completed: {len(similar_products)} results, "
            f"{duration_ms}ms"
        )

        return VisualSearchResponse(
            success=True,
            query_image_url=request.image_url,
            total_results=len(similar_products),
            results=similar_products,
            search_duration_ms=duration_ms
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
