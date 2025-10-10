"""
AI Agent Service V2 - FastAPI HTTP Server with Prompt Caching
Provides universal chat API for all channels (Telegram, WhatsApp, Web).
"""

import os
import logging
import json
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
from models import ChatRequest, ChatResponse, CacheStats, RequestUsage


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
        api_key=os.getenv("CLAUDE_API_KEY"),
        backend_api_url=os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1"),
        shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8")),
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        cache_refresh_interval_hours=int(os.getenv("CACHE_REFRESH_INTERVAL_HOURS", "1"))
    )

    mcp_client = MCPClient(
        backend_api_url=os.getenv("BACKEND_API_URL", "http://localhost:8014/api/v1"),
        shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8"))
    )

    conversation_service = ConversationService(
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/conversations.db")
    )

    # Initialize chat storage service (for manager monitoring)
    chat_storage = ChatStorageService(
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/conversations.db"),
        shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8"))
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
    await claude_service.close()
    await mcp_client.close()
    await conversation_service.close()
    await chat_storage.close()


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

    Claude Sonnet 4.5 pricing:
    - Input tokens: $3.00 per 1M tokens
    - Cache reads: $0.30 per 1M tokens (90% discount)
    - Cache writes: $3.75 per 1M tokens (25% premium)
    - Output tokens: $15.00 per 1M tokens
    """
    usage = response.usage

    input_tokens = getattr(usage, 'input_tokens', 0)
    output_tokens = getattr(usage, 'output_tokens', 0)
    cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
    cache_creation_tokens = getattr(usage, 'cache_creation_input_tokens', 0)

    # Calculate cost (USD)
    input_cost = (input_tokens / 1_000_000) * 3.00
    cache_read_cost = (cache_read_tokens / 1_000_000) * 0.30
    cache_write_cost = (cache_creation_tokens / 1_000_000) * 3.75
    output_cost = (output_tokens / 1_000_000) * 15.00

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

                    # Execute tool
                    tool_result = await mcp_client.call_tool(
                        tool_name=block.name,
                        arguments=block.input
                    )

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

        # Smart detection: Set show_products=True if response contains product listings
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

        history.append({
            "role": "assistant",
            "content": final_content
        })

        # Save conversation history
        await conversation_service.save_conversation(user_id, channel, history)

        # Calculate total usage for this request
        input_cost = (total_input_tokens / 1_000_000) * 3.00
        cache_read_cost = (total_cache_read_tokens / 1_000_000) * 0.30
        cache_write_cost = (total_cache_creation_tokens / 1_000_000) * 3.75
        output_cost = (total_output_tokens / 1_000_000) * 15.00
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
