"""
Embedding Service - Microservice for generating ML embeddings

This standalone FastAPI service generates vector embeddings for images and text
using Google Vertex AI. It's deployed separately on Railway for scalability.

Endpoints:
- GET /health - Health check
- POST /embed/image - Generate embedding for image URL
- POST /embed/batch - Batch generate embeddings for multiple images
- GET /stats - Service statistics

Environment Variables:
- VERTEX_PROJECT_ID: GCP project ID
- VERTEX_LOCATION: GCP region (e.g., us-central1)
- VERTEX_SERVICE_ACCOUNT_KEY: GCP service account JSON (as string)
- PORT: Server port (default: 8001)
- LOG_LEVEL: Logging level (default: INFO)
"""

import os
import time
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

from services.vertex_ai import VertexAIClient
from services.embedding import EmbeddingService

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global clients (initialized in lifespan)
vertex_client: Optional[VertexAIClient] = None
embedding_service: Optional[EmbeddingService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - initialize clients on startup."""
    global vertex_client, embedding_service

    logger.info("Initializing Embedding Service...")

    # Load environment variables
    project_id = os.getenv("VERTEX_PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    service_account_key = os.getenv("VERTEX_SERVICE_ACCOUNT_KEY")

    if not all([project_id, location, service_account_key]):
        logger.error("Missing required environment variables!")
        logger.error(f"VERTEX_PROJECT_ID: {'✓' if project_id else '✗'}")
        logger.error(f"VERTEX_LOCATION: {'✓' if location else '✗'}")
        logger.error(f"VERTEX_SERVICE_ACCOUNT_KEY: {'✓' if service_account_key else '✗'}")
        raise ValueError("Missing Vertex AI credentials")

    # Initialize Vertex AI client
    vertex_client = VertexAIClient(
        project_id=project_id,
        location=location,
        service_account_key=service_account_key
    )

    # Initialize embedding service
    embedding_service = EmbeddingService(vertex_client)

    logger.info(f"✅ Embedding Service initialized (project: {project_id}, location: {location})")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Embedding Service...")


# Create FastAPI app
app = FastAPI(
    title="Embedding Service",
    description="Microservice for generating ML embeddings using Vertex AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# Request/Response Models
# ===============================

class EmbedImageRequest(BaseModel):
    """Request to generate embedding for an image."""
    image_url: str = Field(..., description="URL of the image to embed")
    product_id: Optional[int] = Field(None, description="Optional product ID for logging")


class EmbedImageResponse(BaseModel):
    """Response with generated embedding."""
    success: bool
    embedding: List[float] = Field(..., description="512-dimensional embedding vector")
    dimensions: int = Field(..., description="Vector dimensions (should be 512)")
    model: str = Field(..., description="Model identifier")
    duration_ms: int = Field(..., description="Processing time in milliseconds")


class BatchEmbedRequest(BaseModel):
    """Request to batch generate embeddings."""
    image_urls: List[str] = Field(..., description="List of image URLs to embed", min_items=1, max_items=50)


class BatchEmbedResult(BaseModel):
    """Result for a single batch item."""
    image_url: str
    success: bool
    embedding: Optional[List[float]] = None
    error: Optional[str] = None


class BatchEmbedResponse(BaseModel):
    """Response for batch embedding request."""
    success: bool
    total: int
    successful: int
    failed: int
    results: List[BatchEmbedResult]
    duration_ms: int


class StatsResponse(BaseModel):
    """Service statistics."""
    service: str
    status: str
    uptime_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_duration_ms: float


# ===============================
# Global Statistics
# ===============================

service_stats = {
    "start_time": time.time(),
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_duration_ms": 0,
}


# ===============================
# API Endpoints
# ===============================

@app.get("/")
async def root():
    """Root endpoint - service information."""
    return {
        "service": "embedding-service",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": [
            "GET /health - Health check",
            "POST /embed/image - Generate image embedding",
            "POST /embed/batch - Batch generate embeddings",
            "GET /stats - Service statistics"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "embedding-service",
        "vertex_ai_configured": vertex_client is not None
    }


@app.post("/embed/image", response_model=EmbedImageResponse)
async def embed_image(request: EmbedImageRequest):
    """
    Generate embedding for a single image.

    Process:
    1. Download image from URL
    2. Generate 512D embedding using Vertex AI
    3. Return normalized vector

    Args:
        request: Image URL and optional product ID

    Returns:
        EmbedImageResponse with 512D embedding vector
    """
    if not embedding_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    start_time = time.time()
    service_stats["total_requests"] += 1

    try:
        logger.info(f"Generating embedding for: {request.image_url[:80]}...")

        # Download image (follow redirects for cvety.kz URLs)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(request.image_url)
            response.raise_for_status()
            image_bytes = response.content

        logger.info(f"Downloaded {len(image_bytes)} bytes")

        # Generate embedding
        embedding = await embedding_service.generate_image_embedding(image_bytes)

        duration_ms = int((time.time() - start_time) * 1000)
        service_stats["successful_requests"] += 1
        service_stats["total_duration_ms"] += duration_ms

        logger.info(
            f"Generated embedding for product {request.product_id}: "
            f"{len(embedding)} dims, {duration_ms}ms"
        )

        return EmbedImageResponse(
            success=True,
            embedding=embedding,
            dimensions=len(embedding),
            model="vertex-multimodal-001",
            duration_ms=duration_ms
        )

    except httpx.HTTPError as e:
        service_stats["failed_requests"] += 1
        logger.error(f"Failed to download image: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

    except Exception as e:
        service_stats["failed_requests"] += 1
        logger.error(f"Embedding generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


@app.post("/embed/batch", response_model=BatchEmbedResponse)
async def embed_batch(request: BatchEmbedRequest):
    """
    Batch generate embeddings for multiple images.

    Processes images in parallel with concurrency limit to avoid
    overwhelming Vertex AI API.

    Args:
        request: List of image URLs (max 50)

    Returns:
        BatchEmbedResponse with results for each image
    """
    if not embedding_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    start_time = time.time()
    service_stats["total_requests"] += 1

    try:
        logger.info(f"Batch embedding request: {len(request.image_urls)} images")

        results = await embedding_service.batch_generate_embeddings(request.image_urls)

        duration_ms = int((time.time() - start_time) * 1000)

        # Convert to response format
        batch_results = []
        successful = 0
        failed = 0

        for result in results:
            if result["success"]:
                successful += 1
                batch_results.append(BatchEmbedResult(
                    image_url=result["image_url"],
                    success=True,
                    embedding=result["embedding"]
                ))
            else:
                failed += 1
                batch_results.append(BatchEmbedResult(
                    image_url=result["image_url"],
                    success=False,
                    error=result.get("error", "Unknown error")
                ))

        service_stats["successful_requests"] += successful
        service_stats["failed_requests"] += failed
        service_stats["total_duration_ms"] += duration_ms

        logger.info(
            f"Batch embedding completed: {successful} success, {failed} failed, "
            f"{duration_ms}ms total ({duration_ms/len(request.image_urls):.0f}ms avg)"
        )

        return BatchEmbedResponse(
            success=True,
            total=len(request.image_urls),
            successful=successful,
            failed=failed,
            results=batch_results,
            duration_ms=duration_ms
        )

    except Exception as e:
        service_stats["failed_requests"] += 1
        logger.error(f"Batch embedding failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get service statistics."""
    uptime = time.time() - service_stats["start_time"]
    total = service_stats["total_requests"]
    avg_duration = (
        service_stats["total_duration_ms"] / service_stats["successful_requests"]
        if service_stats["successful_requests"] > 0
        else 0
    )

    return StatsResponse(
        service="embedding-service",
        status="healthy" if embedding_service else "degraded",
        uptime_seconds=uptime,
        total_requests=total,
        successful_requests=service_stats["successful_requests"],
        failed_requests=service_stats["failed_requests"],
        average_duration_ms=avg_duration
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "production") == "development"
    )
