"""
AI Agent Service V2 - FastAPI HTTP Server with Prompt Caching
Provides universal chat API for all channels (Telegram, WhatsApp, Web).
"""

import os
import logging
import json
import asyncio
import signal
import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config import settings

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import services and models
from services import ClaudeService, MCPClient, ConversationService
from services.chat_storage import ChatStorageService
from models import ChatRequest, ChatResponse, CacheStats, RequestUsage, ProductIdsRequest


# Global service instances
claude_service: Optional[ClaudeService] = None
mcp_client: Optional[MCPClient] = None
conversation_service: Optional[ConversationService] = None
chat_storage: Optional[ChatStorageService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    global claude_service, mcp_client, conversation_service, chat_storage

    logger.info("🚀 Starting AI Agent Service V2...")

    # Initialize services
    claude_service = ClaudeService(
        api_key=settings.CLAUDE_API_KEY,
        backend_api_url=settings.BACKEND_API_URL,
        shop_id=settings.DEFAULT_SHOP_ID,
        model=settings.CLAUDE_MODEL,
        cache_refresh_interval_hours=settings.CACHE_REFRESH_INTERVAL_HOURS
    )

    mcp_client = MCPClient(
        backend_api_url=settings.BACKEND_API_URL,
        shop_id=settings.DEFAULT_SHOP_ID
    )

    # Get database URL and convert to async format if needed
    database_url = settings.DATABASE_URL or f"sqlite+aiosqlite:///./{settings.DB_FILE}"
    # Railway provides postgresql:// but async SQLAlchemy needs postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    conversation_service = ConversationService(
        database_url=database_url
    )

    # Initialize chat storage service (for manager monitoring)
    chat_storage = ChatStorageService(
        database_url=database_url,
        shop_id=settings.DEFAULT_SHOP_ID
    )

    # Initialize database
    await conversation_service.init_db()

    # Initialize cache (load product catalog)
    await claude_service.init_cache()

    logger.info("✅ All services initialized successfully!")
    logger.info(f"📊 Cache Hit Rate: {claude_service.cache_hit_rate:.1f}%")

    yield

    # Shutdown
    logger.info("🛑 Shutting down AI Agent Service V2...")

    # Close services
    await claude_service.close()
    await mcp_client.close()
    await conversation_service.close()
    await chat_storage.close()
    logger.info("✅ All services closed successfully")


# Create FastAPI app
app = FastAPI(
    title="Flower Shop AI Agent V2",
    description="Universal AI agent with Prompt Caching for 80-90% token savings",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.chat import router as chat_router
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-agent-service-v2",
        "version": "2.0.0",
        "cache_hit_rate": f"{claude_service.cache_hit_rate:.1f}%",
        "total_requests": claude_service.total_requests
    }


@app.get("/cache-stats")
async def get_cache_stats() -> CacheStats:
    """Get cache statistics."""
    return CacheStats(
        total_requests=claude_service.total_requests,
        cache_hits=claude_service.cache_hits,
        cache_hit_rate=claude_service.cache_hit_rate,
        cached_input_tokens=claude_service.cached_input_tokens,
        regular_input_tokens=claude_service.regular_input_tokens,
        tokens_saved=claude_service.tokens_saved,
        cost_savings_usd=claude_service.cost_savings_usd,
        last_cache_refresh=claude_service._last_cache_refresh.isoformat() if claude_service._last_cache_refresh else None
    )


def calculate_request_usage(response) -> RequestUsage:
    """
    Calculate usage metrics from Claude API response.

    Claude Haiku 4.5 pricing:
    - Input tokens: $0.80 per 1M tokens
    - Cache reads: $0.08 per 1M tokens (90% discount)
    - Cache writes: $1.00 per 1M tokens (25% premium)
    - Output tokens: $4.00 per 1M tokens
    """
    usage = response.usage

    input_tokens = getattr(usage, 'input_tokens', 0)
    output_tokens = getattr(usage, 'output_tokens', 0)
    cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
    cache_creation_tokens = getattr(usage, 'cache_creation_input_tokens', 0)

    # Calculate cost (USD)
    input_cost = (input_tokens / 1_000_000) * 0.80
    cache_read_cost = (cache_read_tokens / 1_000_000) * 0.08
    cache_write_cost = (cache_creation_tokens / 1_000_000) * 1.00
    output_cost = (output_tokens / 1_000_000) * 4.00

    total_cost = input_cost + cache_read_cost + cache_write_cost + output_cost

    return RequestUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_creation_tokens=cache_creation_tokens,
        total_cost_usd=round(total_cost, 6),
        cache_hit=(cache_read_tokens > 0)
    )



@app.delete("/conversations/{user_id}")
async def clear_conversation(user_id: str, channel: Optional[str] = None):
    """Clear conversation history for user."""
    await conversation_service.clear_conversation(user_id, channel)
    return {"message": f"Conversation cleared for user {user_id}"}


@app.post("/admin/refresh-cache")
async def refresh_cache():
    """Manual cache refresh endpoint."""
    await claude_service._refresh_cache()
    return {
        "message": "Cache refreshed successfully",
        "last_refresh": claude_service._last_cache_refresh.isoformat()
    }


@app.post("/products/by_ids")
async def get_products_by_ids(request: ProductIdsRequest):
    """
    Get products by specific IDs (for AI-filtered product display).

    This endpoint is used when AI has pre-filtered products via list_products tool.
    Returns products in the same order as the provided IDs.
    """
    try:
        import httpx

        backend_url = settings.BACKEND_API_URL
        shop_id = settings.DEFAULT_SHOP_ID

        if not request.product_ids:
            logger.warning("⚠️ Empty product_ids list received")
            return {"products": []}

        # Fetch all requested products from backend
        async with httpx.AsyncClient() as client:
            # Backend API doesn't support filtering by IDs directly,
            # so we fetch products and filter client-side
            response = await client.get(
                f"{backend_url}/products/",
                params={
                    "shop_id": shop_id,
                    "enabled_only": "true",
                    "limit": 100  # Fetch enough products to cover the requested IDs
                }
            )
            response.raise_for_status()
            all_products = response.json()

        # Create ID-to-product mapping
        product_map = {p["id"]: p for p in all_products}

        # Filter and sort products by requested IDs (preserve order)
        filtered_products = []
        for product_id in request.product_ids:
            if product_id in product_map:
                product = product_map[product_id]
                filtered_products.append({
                    "id": product.get("id"),
                    "name": product.get("name"),
                    "price": product.get("price"),
                    "image": product.get("image"),  # Single image field for backward compatibility
                    "images": product.get("images", []),
                    "description": product.get("description", "")
                })
            else:
                logger.warning(f"⚠️ Product ID {product_id} not found in shop catalog")

        logger.info(f"📦 Returning {len(filtered_products)}/{len(request.product_ids)} filtered products")

        return {
            "products": filtered_products[:10]  # Limit to 10 for telegram display
        }

    except Exception as e:
        logger.error(f"❌ Error fetching products by IDs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
