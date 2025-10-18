"""
Visual Search API - endpoints for image-based product search

Provides endpoints for:
1. POST /search/visual - search products by uploaded image
2. POST /products/{id}/generate-embedding - generate embedding for a product
3. POST /admin/batch-generate-embeddings - batch generate embeddings
4. GET /admin/embeddings-stats - embedding generation statistics
"""

import os
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
import structlog

from models.products import Product
from models.shop import Shop
from services.embedding_service import (
    generate_clip_embedding,
    download_image_from_url,
    calculate_cosine_similarity,
    db_format_to_embedding_vector,
    embedding_vector_to_db_format,
    EmbeddingError,
    SIMILARITY_THRESHOLD_LOW
)
from api.auth import get_current_user_token

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["visual_search"])


# ===============================
# Public Endpoints
# ===============================

@router.post("/search/visual")
async def visual_search(
    file: UploadFile = File(...),
    shop_id: int = Query(8, description="Shop ID"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return")
):
    """
    Search for similar products by uploading an image

    - Generates CLIP embedding from uploaded image
    - Finds products with highest cosine similarity
    - Returns products with similarity scores
    - Falls back to "not found" if no good matches

    Args:
        file: Image file (JPEG, PNG, etc.)
        shop_id: Shop to search within (default: 8)
        limit: Maximum number of results (default: 10, max: 100)

    Returns:
        List of similar products with similarity_score, or error message
    """
    try:
        logger.info(
            "visual_search_started",
            shop_id=shop_id,
            limit=limit,
            filename=file.filename
        )

        # Read uploaded file
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Generate embedding from uploaded image
        try:
            query_embedding = generate_clip_embedding(file_bytes)
        except EmbeddingError as e:
            logger.warning("embedding_generation_failed", error=str(e))
            return JSONResponse(
                status_code=400,
                content={"error": f"Could not process image: {str(e)}"}
            )

        # Get database session (simplified for this example)
        from config import SessionLocal
        session = SessionLocal()

        try:
            # Find products with embeddings for this shop
            statement = select(Product).where(
                (Product.shop_id == shop_id) &
                (Product.image_embedding.isnot(None)) &
                (Product.enabled == True)
            )
            products_with_embeddings = session.exec(statement).all()

            if not products_with_embeddings:
                logger.info("no_products_with_embeddings", shop_id=shop_id)
                return JSONResponse(
                    content={
                        "error": "Не могу найти похожие букеты",
                        "message": "В каталоге нет букетов с анализированными изображениями"
                    }
                )

            # Calculate similarity scores
            results = []
            for product in products_with_embeddings:
                try:
                    # Convert stored embedding to vector
                    stored_embedding = db_format_to_embedding_vector(product.image_embedding)
                    if not stored_embedding:
                        continue

                    # Calculate cosine similarity
                    similarity = calculate_cosine_similarity(query_embedding, stored_embedding)

                    results.append({
                        "product_id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "image": product.image,
                        "similarity_score": round(similarity, 3),
                        "similarity_percent": round(similarity * 100, 1)
                    })

                except Exception as e:
                    logger.error("similarity_calculation_failed", product_id=product.id, error=str(e))
                    continue

            # Sort by similarity (highest first)
            results.sort(key=lambda x: x["similarity_score"], reverse=True)

            # Filter by threshold and limit
            filtered_results = [r for r in results if r["similarity_score"] >= SIMILARITY_THRESHOLD_LOW][:limit]

            if not filtered_results:
                logger.info("no_similar_products_found", shop_id=shop_id)
                return JSONResponse(
                    content={
                        "error": "Не могу найти похожие букеты",
                        "message": f"По загруженному изображению не найдено похожих букетов (пороговое значение сходства: {SIMILARITY_THRESHOLD_LOW})",
                        "suggestion": "Попробуйте загрузить более четкое фото букета"
                    }
                )

            logger.info(
                "visual_search_success",
                shop_id=shop_id,
                results_count=len(filtered_results),
                top_similarity=filtered_results[0]["similarity_score"] if filtered_results else 0
            )

            return {
                "results": filtered_results,
                "count": len(filtered_results),
                "threshold": SIMILARITY_THRESHOLD_LOW
            }

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("visual_search_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


# ===============================
# Admin Endpoints
# ===============================

@router.post("/products/{product_id}/generate-embedding")
async def generate_product_embedding(
    product_id: int,
    token: str = Query(..., description="Admin JWT token")
):
    """
    Generate or regenerate CLIP embedding for a single product

    Args:
        product_id: Product ID
        token: Admin JWT token

    Returns:
        Success status with embedding generation info
    """
    try:
        # Verify admin token
        user_data = get_current_user_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid token")

        logger.info(
            "generate_product_embedding_started",
            product_id=product_id,
            user_id=user_data.get("sub")
        )

        from config import SessionLocal
        session = SessionLocal()

        try:
            # Get product
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            # Check shop access
            if product.shop_id != user_data.get("shop_id"):
                raise HTTPException(status_code=403, detail="Access denied")

            # Get image
            if not product.image:
                raise HTTPException(status_code=400, detail="Product has no image")

            # Download image
            image_bytes = download_image_from_url(product.image)
            if not image_bytes:
                raise HTTPException(status_code=400, detail="Failed to download image")

            # Generate embedding
            try:
                embedding = generate_clip_embedding(image_bytes)
            except EmbeddingError as e:
                logger.error("embedding_generation_failed", product_id=product_id, error=str(e))
                raise HTTPException(status_code=400, detail=f"Embedding generation failed: {str(e)}")

            # Save to database
            from datetime import datetime
            product.image_embedding = embedding  # pgvector will handle it
            product.embedding_generated_at = datetime.utcnow()
            session.add(product)
            session.commit()

            logger.info(
                "embedding_generated_success",
                product_id=product_id,
                embedding_dim=len(embedding) if embedding else 0
            )

            return {
                "status": "success",
                "product_id": product_id,
                "embedding_dim": len(embedding) if embedding else 0,
                "generated_at": product.embedding_generated_at
            }

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("generate_product_embedding_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/batch-generate-embeddings")
async def batch_generate_embeddings(
    shop_id: int = Query(8),
    token: str = Query(...),
    background_tasks: BackgroundTasks = None
):
    """
    Batch generate embeddings for all products without embeddings

    Runs in background. Use /admin/embeddings-stats to check progress.

    Args:
        shop_id: Shop ID (default: 8)
        token: Admin JWT token
        background_tasks: FastAPI background tasks

    Returns:
        Task info with estimated products to process
    """
    try:
        # Verify admin token
        user_data = get_current_user_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid token")

        from config import SessionLocal
        session = SessionLocal()

        try:
            # Count products without embeddings
            statement = select(func.count(Product.id)).where(
                (Product.shop_id == shop_id) &
                (Product.image.isnot(None)) &
                (Product.image_embedding.is_(None))
            )
            missing_count = session.exec(statement).one()

            if missing_count == 0:
                return {
                    "status": "nothing_to_do",
                    "message": "All products have embeddings",
                    "products_count": 0
                }

            logger.info(
                "batch_generation_started",
                shop_id=shop_id,
                products_count=missing_count
            )

            # Schedule background task
            if background_tasks:
                background_tasks.add_task(_background_batch_generate, shop_id)

            return {
                "status": "queued",
                "message": "Batch generation queued",
                "estimated_products": missing_count,
                "note": "Check /admin/embeddings-stats for progress"
            }

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("batch_generate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/embeddings-stats")
async def embeddings_stats(
    shop_id: int = Query(8),
    token: str = Query(...),
):
    """
    Get embedding generation statistics for a shop

    Args:
        shop_id: Shop ID (default: 8)
        token: Admin JWT token

    Returns:
        Statistics on embedding generation progress
    """
    try:
        # Verify admin token
        user_data = get_current_user_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid token")

        from config import SessionLocal
        session = SessionLocal()

        try:
            # Count total products
            total_stmt = select(func.count(Product.id)).where(Product.shop_id == shop_id)
            total_products = session.exec(total_stmt).one()

            # Count products with images
            with_images_stmt = select(func.count(Product.id)).where(
                (Product.shop_id == shop_id) &
                (Product.image.isnot(None))
            )
            with_images = session.exec(with_images_stmt).one()

            # Count products with embeddings
            with_embeddings_stmt = select(func.count(Product.id)).where(
                (Product.shop_id == shop_id) &
                (Product.image_embedding.isnot(None))
            )
            with_embeddings = session.exec(with_embeddings_stmt).one()

            # Count missing
            missing = with_images - with_embeddings
            percentage = (with_embeddings / with_images * 100) if with_images > 0 else 0

            return {
                "total_products": total_products,
                "products_with_images": with_images,
                "products_with_embeddings": with_embeddings,
                "products_missing_embeddings": missing,
                "completion_percentage": round(percentage, 1)
            }

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("embeddings_stats_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# Background Tasks
# ===============================

async def _background_batch_generate(shop_id: int):
    """Background task to generate embeddings for all products without them"""
    from config import SessionLocal
    from datetime import datetime

    session = SessionLocal()
    try:
        # Get products without embeddings
        statement = select(Product).where(
            (Product.shop_id == shop_id) &
            (Product.image.isnot(None)) &
            (Product.image_embedding.is_(None)) &
            (Product.enabled == True)
        )
        products = session.exec(statement).all()

        logger.info(
            "background_batch_start",
            shop_id=shop_id,
            product_count=len(products)
        )

        processed = 0
        failed = 0

        for product in products:
            try:
                # Download image
                image_bytes = download_image_from_url(product.image)
                if not image_bytes:
                    failed += 1
                    continue

                # Generate embedding
                embedding = generate_clip_embedding(image_bytes)

                # Save
                product.image_embedding = embedding
                product.embedding_generated_at = datetime.utcnow()
                session.add(product)
                session.commit()

                processed += 1

                # Rate limiting - sleep between requests
                import time
                time.sleep(0.1)

            except Exception as e:
                logger.error("batch_product_error", product_id=product.id, error=str(e))
                failed += 1
                continue

        logger.info(
            "background_batch_complete",
            shop_id=shop_id,
            processed=processed,
            failed=failed
        )

    except Exception as e:
        logger.error("background_batch_error", error=str(e), exc_info=True)
    finally:
        session.close()
