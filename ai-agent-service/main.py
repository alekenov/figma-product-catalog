"""
AI Agent Service V2 - FastAPI HTTP Server with Prompt Caching
Provides universal chat API for all channels (Telegram, WhatsApp, Web).
"""

import os
import logging
import json
import asyncio
import signal
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Graceful shutdown tracking
active_requests = 0
shutdown_event = asyncio.Event()
SHUTDOWN_TIMEOUT_SECONDS = 30  # Max time to wait for active requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    global claude_service, mcp_client, conversation_service, chat_storage

    logger.info("🚀 Starting AI Agent Service V2...")

    # Initialize services
    claude_service = ClaudeService(
        api_key=os.getenv("CLAUDE_API_KEY"),
        backend_api_url=os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1"),
        shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8")),
        model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
        cache_refresh_interval_hours=int(os.getenv("CACHE_REFRESH_INTERVAL_HOURS", "1"))
    )

    mcp_client = MCPClient(
        backend_api_url=os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1"),
        shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8"))
    )

    # Get database URL and convert to async format if needed
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/conversations.db")
    # Railway provides postgresql:// but async SQLAlchemy needs postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    conversation_service = ConversationService(
        database_url=database_url
    )

    # Initialize chat storage service (for manager monitoring)
    chat_storage = ChatStorageService(
        database_url=database_url,
        shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8"))
    )

    # Initialize database
    await conversation_service.init_db()

    # Initialize cache (load product catalog)
    await claude_service.init_cache()

    logger.info("✅ All services initialized successfully!")
    logger.info(f"📊 Cache Hit Rate: {claude_service.cache_hit_rate:.1f}%")

    yield

    # Shutdown - wait for active requests to complete
    logger.info("🛑 Shutting down AI Agent Service V2...")

    global active_requests
    if active_requests > 0:
        logger.info(f"⏳ Waiting for {active_requests} active requests to complete...")
        logger.info(f"⏱️  Max wait time: {SHUTDOWN_TIMEOUT_SECONDS} seconds")

        # Wait for active requests with timeout
        try:
            await asyncio.wait_for(
                shutdown_event.wait(),
                timeout=SHUTDOWN_TIMEOUT_SECONDS
            )
            logger.info("✅ All active requests completed gracefully")
        except asyncio.TimeoutError:
            logger.warning(f"⚠️  Shutdown timeout reached with {active_requests} requests still active")
            logger.warning("⚠️  Forcing shutdown to prevent data loss")

    # Close services
    await claude_service.close()
    await mcp_client.close()
    await conversation_service.close()
    await chat_storage.close()
    logger.info("✅ All services closed successfully")


# Middleware to track active requests for graceful shutdown
class ActiveRequestMiddleware(BaseHTTPMiddleware):
    """Track active requests to enable graceful shutdown."""

    async def dispatch(self, request: Request, call_next):
        global active_requests

        # Skip health checks from counter
        if request.url.path == "/health":
            return await call_next(request)

        # Increment active request counter
        active_requests += 1
        logger.debug(f"📊 Active requests: {active_requests} (+1)")

        try:
            # Process request
            response = await call_next(request)
            return response
        finally:
            # Decrement counter when request completes (success or error)
            active_requests -= 1
            logger.debug(f"📊 Active requests: {active_requests} (-1)")

            # Signal shutdown event if all requests completed
            if active_requests == 0:
                shutdown_event.set()


# Create FastAPI app
app = FastAPI(
    title="Flower Shop AI Agent V2",
    description="Universal AI agent with Prompt Caching for 80-90% token savings",
    version="2.0.0",
    lifespan=lifespan
)

# Add active request tracking middleware (must be first)
app.add_middleware(ActiveRequestMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Universal chat endpoint for all channels.

    Processes user message with Claude AI, executes MCP tools, and returns response.
    """
    try:
        user_id = request.user_id
        channel = request.channel
        message = request.message

        logger.info(f"👤 USER {user_id} ({channel}): {message}")

        # Create or get chat session for monitoring
        session_id = await chat_storage.create_or_get_session(
            user_id=user_id,
            channel=channel,
            customer_name=request.context.get("customer_name") if request.context else None,
            customer_phone=request.context.get("customer_phone") if request.context else None
        )

        # Save user message to database
        if session_id:
            await chat_storage.save_message(
                session_id=session_id,
                role="user",
                content=message
            )

        # Get conversation history
        history = await conversation_service.get_conversation(user_id, channel)

        # Add user message
        history.append({"role": "user", "content": message})

        # Track metadata
        tracking_id = None
        order_number = None
        order_id = None
        list_products_used = False
        product_ids = None  # Store product IDs from list_products for filtered display

        # Track usage across all API calls in this conversation turn
        total_input_tokens = 0
        total_output_tokens = 0
        total_cache_read_tokens = 0
        total_cache_creation_tokens = 0

        # Call Claude with function calling
        response = await claude_service.chat(
            messages=history,
            channel=channel,
            context=request.context
        )

        # Accumulate usage from first response
        usage = response.usage
        total_input_tokens += getattr(usage, 'input_tokens', 0)
        total_output_tokens += getattr(usage, 'output_tokens', 0)
        total_cache_read_tokens += getattr(usage, 'cache_read_input_tokens', 0)
        total_cache_creation_tokens += getattr(usage, 'cache_creation_input_tokens', 0)

        # Process tool calls if any
        while response.stop_reason == "tool_use":
            # Extract tool calls and content
            tool_results = []
            assistant_content = []

            for block in response.content:
                if block.type == "tool_use":
                    # Execute tool via MCP
                    logger.info(f"🔧 Tool call: {block.name}")

                    # Track list_products usage
                    if block.name == "list_products":
                        list_products_used = True

                    # Execute tool - inject telegram_user_id for user-specific operations
                    tool_args = block.input.copy()
                    if block.name in ["create_order", "update_order", "track_order_by_phone"]:
                        tool_args["telegram_user_id"] = user_id
                        logger.info(f"💾 Injected telegram_user_id={user_id} for {block.name}")

                    tool_result = await mcp_client.call_tool(
                        tool_name=block.name,
                        arguments=tool_args
                    )

                    # Extract product IDs from list_products result
                    if block.name == "list_products":
                        try:
                            result_dict = json.loads(tool_result) if isinstance(tool_result, str) else tool_result
                            products = result_dict if isinstance(result_dict, list) else []
                            # Extract IDs from product list
                            extracted_ids = [p.get("id") for p in products if isinstance(p, dict) and p.get("id")]
                            if extracted_ids:
                                product_ids = extracted_ids
                                logger.info(f"📦 Extracted {len(product_ids)} product IDs from list_products: {product_ids}")
                        except (json.JSONDecodeError, TypeError) as e:
                            logger.warning(f"⚠️ Could not extract product IDs from list_products result: {e}")

                    if block.name == "create_order":
                        try:
                            result_dict = json.loads(tool_result)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse create_order response: {e}")
                            logger.error(f"Raw tool_result: {tool_result[:200]}")
                            result_dict = {}
                        except Exception as e:
                            logger.error(f"Unexpected error parsing create_order: {e}")
                            result_dict = {}

                        if result_dict:
                            tracking_id = result_dict.get("tracking_id") or tracking_id
                            order_number = result_dict.get("orderNumber") or order_number
                            order_id = result_dict.get("id") or order_id

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result
                    })
                    # Convert ToolUseBlock to dict for JSON serialization
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                elif block.type == "text":
                    assistant_content.append({
                        "type": "text",
                        "text": block.text
                    })

            # Add assistant response to history
            history.append({
                "role": "assistant",
                "content": assistant_content
            })

            # Add tool results to history
            if tool_results:
                history.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue conversation with tool results
                response = await claude_service.chat(
                    messages=history,
                    channel=channel,
                    context=request.context
                )

                # Accumulate usage from continuation
                usage = response.usage
                total_input_tokens += getattr(usage, 'input_tokens', 0)
                total_output_tokens += getattr(usage, 'output_tokens', 0)
                total_cache_read_tokens += getattr(usage, 'cache_read_input_tokens', 0)
                total_cache_creation_tokens += getattr(usage, 'cache_creation_input_tokens', 0)

        # Extract final text response and filter internal tags
        import re
        final_text = ""
        for block in response.content:
            if block.type == "text":
                # Remove internal tags from text blocks (Claude may include thinking in text)
                cleaned_text = block.text
                cleaned_text = re.sub(r'<thinking>.*?</thinking>', '', cleaned_text, flags=re.DOTALL)
                cleaned_text = re.sub(r'<conversation_status>.*?</conversation_status>', '', cleaned_text, flags=re.DOTALL)
                cleaned_text = cleaned_text.strip()
                if cleaned_text:  # Only add non-empty text
                    final_text += cleaned_text
            elif block.type == "thinking":
                # Sonnet 4.5 can generate thinking as separate block - skip it
                logger.debug(f"💭 Skipping thinking block: {block.thinking[:100]}...")
                continue

        final_text = final_text.strip()

        # Parse explicit <show_products> tag from Claude's response
        show_products_match = re.search(r'<show_products>(true|false)</show_products>', final_text)
        if show_products_match:
            show_products_explicit = show_products_match.group(1) == "true"
            # Remove tag from final text
            final_text = re.sub(r'<show_products>.*?</show_products>', '', final_text, flags=re.DOTALL).strip()
            list_products_used = show_products_explicit
            logger.info(f"📸 Explicit <show_products> tag: {show_products_explicit}")
        else:
            # Fallback: Auto-detection if no explicit tag
            # Detect patterns like "Букет 'Название' — 9 000 ₸" or "**Букет" (markdown bold)
            if not list_products_used and (
                re.search(r'Букет .+? — \d+', final_text) or  # Price pattern
                re.search(r'\*\*Букет', final_text) or  # Bold букет in markdown
                re.search(r'\d+\.\s+\*\*Букет', final_text)  # Numbered list with букет
            ):
                list_products_used = True
                logger.info("📦 Auto-detected product listing in response, setting show_products=true")

        logger.info(f"🤖 AI RESPONSE: {final_text[:100]}...")

        # Add final response to history with proper content block structure
        # Must use content blocks (not plain string) to match Claude API format
        final_content = []
        for block in response.content:
            if block.type == "text":
                # Use cleaned text without <thinking> blocks
                final_content.append({
                    "type": "text",
                    "text": final_text
                })
                break  # Only need one text block
            elif block.type == "tool_use":
                # Preserve tool_use blocks in final response
                final_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

        # Only append final content if it has meaningful content
        if final_content:
            history.append({
                "role": "assistant",
                "content": final_content
            })
        else:
            # Fallback: if no content extracted, still add text block
            history.append({
                "role": "assistant",
                "content": [{"type": "text", "text": final_text}]
            })

        # Save conversation history
        await conversation_service.save_conversation(user_id, channel, history)

        # Calculate total usage for this request
        # Claude Haiku 4.5 pricing
        input_cost = (total_input_tokens / 1_000_000) * 0.80
        cache_read_cost = (total_cache_read_tokens / 1_000_000) * 0.08
        cache_write_cost = (total_cache_creation_tokens / 1_000_000) * 1.00
        output_cost = (total_output_tokens / 1_000_000) * 4.00
        total_cost = input_cost + cache_read_cost + cache_write_cost + output_cost

        request_usage = RequestUsage(
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            cache_read_tokens=total_cache_read_tokens,
            cache_creation_tokens=total_cache_creation_tokens,
            total_cost_usd=round(total_cost, 6),
            cache_hit=(total_cache_read_tokens > 0)
        )

        logger.info(f"💰 Request cost: ${total_cost:.6f} | Cache hit: {request_usage.cache_hit}")

        # Save assistant message to database
        if session_id:
            from decimal import Decimal

            # Save message with metadata about tools and tokens
            metadata = {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cache_read_tokens": total_cache_read_tokens,
                "cache_creation_tokens": total_cache_creation_tokens,
                "cache_hit": request_usage.cache_hit
            }

            await chat_storage.save_message(
                session_id=session_id,
                role="assistant",
                content=final_text,
                metadata=metadata,
                cost_usd=Decimal(str(total_cost))
            )

            # Update session statistics
            await chat_storage.update_session_stats(
                session_id=session_id,
                increment_messages=2,  # User message + assistant message
                add_cost_usd=Decimal(str(total_cost)),
                created_order=(order_id is not None),
                order_id=order_id
            )

        return ChatResponse(
            text=final_text,
            tracking_id=tracking_id,
            order_number=order_number,
            show_products=list_products_used,
            product_ids=product_ids,
            usage=request_usage
        )

    except Exception as e:
        logger.error(f"❌ Error processing chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


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


@app.get("/products/{user_id}")
async def get_products(user_id: str, channel: Optional[str] = None):
    """
    Get product list for displaying in Telegram bot.

    This endpoint is called by telegram-bot when AI response indicates show_products=true.
    Returns formatted product list with images for media group display.
    """
    try:
        import httpx

        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")
        shop_id = int(os.getenv("DEFAULT_SHOP_ID", "8"))

        # Fetch products from backend API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{backend_url}/products/",
                params={
                    "shop_id": shop_id,
                    "enabled_only": "true",
                    "limit": 20  # Get first 20 products
                }
            )
            response.raise_for_status()
            products_data = response.json()

        # Format products for telegram bot
        products = []
        for product in products_data:
            products.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "price": product.get("price"),  # Already in tiyns
                "images": product.get("images", []),
                "description": product.get("description", "")
            })

        logger.info(f"📦 Returning {len(products)} products for user {user_id}")

        return {
            "products": products[:10]  # Bot only shows first 10
        }

    except Exception as e:
        logger.error(f"❌ Error fetching products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


@app.post("/products/by_ids")
async def get_products_by_ids(request: ProductIdsRequest):
    """
    Get products by specific IDs (for AI-filtered product display).

    This endpoint is used when AI has pre-filtered products via list_products tool.
    Returns products in the same order as the provided IDs.
    """
    try:
        import httpx

        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1")
        shop_id = int(os.getenv("DEFAULT_SHOP_ID", "8"))

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

    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
