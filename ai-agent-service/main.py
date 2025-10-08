"""
AI Agent Service - FastAPI HTTP Server
Provides universal chat API for all channels (Telegram, WhatsApp, Web, Instagram).
"""
import os
import sys
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables BEFORE validation
load_dotenv()

# Configure structured logging FIRST
from logging_config import configure_logging, get_logger, bind_request_context, clear_request_context

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Add shared directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from config_validator import ConfigValidator

# Validate configuration at startup
ConfigValidator.validate_all({
    "CLAUDE_API_KEY": {
        "required": True
    },
    "MCP_SERVER_URL": {
        "required": True,
        "type": "url"
    },
    "DEFAULT_SHOP_ID": {
        "required": False,
        "default": "8",
        "type": "integer"
    },
    "PORT": {
        "required": False,
        "default": "8000",
        "type": "integer"
    },
    "DEBUG": {
        "required": False,
        "default": "false",
        "type": "boolean"
    }
}, service_name="AI Agent Service")

from agent import FlowerShopAgent

# Create FastAPI app
app = FastAPI(
    title="Flower Shop AI Agent",
    description="Universal AI agent for omnichannel customer service",
    version="1.0.0"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent
agent = FlowerShopAgent(
    api_key=os.getenv("CLAUDE_API_KEY"),
    mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
    shop_id=int(os.getenv("DEFAULT_SHOP_ID", "8"))
)

logger.info(f"✅ AI Agent initialized with shop_id={agent.shop_id}")


# ===== Pydantic Models =====

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message text")
    user_id: str = Field(..., description="Unique user identifier (telegram_id, phone, session_id)")
    channel: str = Field(default="telegram", description="Channel name (telegram, whatsapp, web, instagram)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context (user info, etc)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Покажи букеты до 10000 тенге",
                "user_id": "123456789",
                "channel": "telegram",
                "context": {"username": "johndoe", "first_name": "John"}
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    text: str = Field(..., description="AI response text")
    tracking_id: Optional[str] = Field(default=None, description="Order tracking ID (if order created)")
    order_number: Optional[str] = Field(default=None, description="Order number (if order created)")
    show_products: Optional[bool] = Field(default=False, description="Should the Telegram bot send cached product gallery")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "✅ Заказ успешно оформлен!\n📦 Номер заказа: #12357\n🔗 Отследить: https://cvety-website.pages.dev/status/903757396",
                "tracking_id": "903757396",
                "order_number": "#12357",
                "show_products": False
            }
        }


class ClearHistoryResponse(BaseModel):
    """Response model for clear history endpoint."""
    status: str = Field(..., description="Status message")
    user_id: str = Field(..., description="User ID")
    channel: str = Field(..., description="Channel name")


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint - service info."""
    return {
        "service": "Flower Shop AI Agent",
        "version": "1.0.0",
        "status": "running",
        "model": agent.model,
        "shop_id": agent.shop_id
    }


@app.get("/health")
async def health():
    """
    Health check endpoint for Railway/monitoring systems.
    Checks MCP server connectivity and Claude API key configuration.
    """
    from datetime import datetime
    import httpx

    mcp_status = "unknown"
    mcp_error = None

    # Check MCP server connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to reach MCP server (it runs on stdio, so check backend instead)
            mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
            response = await client.get(f"{mcp_url.replace('/api/v1', '')}/health", timeout=5.0)
            if response.status_code == 200:
                mcp_status = "healthy"
            else:
                mcp_status = "degraded"
                mcp_error = f"Status code: {response.status_code}"
    except Exception as e:
        mcp_status = "unhealthy"
        mcp_error = str(e)[:100]

    # Check Claude API key configured
    claude_key_configured = bool(os.getenv("CLAUDE_API_KEY"))

    # Overall status
    overall_status = "healthy" if (mcp_status == "healthy" and claude_key_configured) else "degraded"

    response = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-agent",
        "version": "1.0.0",
        "model": agent.model,
        "shop_id": agent.shop_id,
        "dependencies": {
            "mcp_server": {
                "status": mcp_status,
                "error": mcp_error
            },
            "claude_api": {
                "status": "configured" if claude_key_configured else "missing"
            }
        }
    }

    # Return 503 if degraded (for load balancers)
    status_code = 200 if overall_status == "healthy" else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(content=response, status_code=status_code)


@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    """
    Universal chat endpoint for all channels.

    Processes user message with AI and returns response.
    Supports multi-turn conversations with automatic function calling.

    **Channel-specific behavior:**
    - telegram: Friendly, uses emojis ✅
    - whatsapp: Professional, no emojis
    - instagram: Youth style, emojis ✅
    - web: Structured, consultant tone

    **Examples:**
    ```python
    # Telegram
    POST /chat
    {
        "message": "покажи букеты",
        "user_id": "123456789",
        "channel": "telegram"
    }

    # WhatsApp
    POST /chat
    {
        "message": "хочу заказать розы на завтра",
        "user_id": "+77011234567",
        "channel": "whatsapp"
    }

    # Web
    POST /chat
    {
        "message": "какой статус моего заказа?",
        "user_id": "session_abc123",
        "channel": "web"
    }
    ```
    """
    # Extract request_id from headers
    request_id = request.headers.get("x-request-id", f"req_unknown_{id(request)}")

    # Bind request context for structured logging
    bind_request_context(
        request_id=request_id,
        user_id=chat_request.user_id,
        channel=chat_request.channel
    )

    try:
        logger.info("chat_request_received",
                    message_length=len(chat_request.message))

        # Pass request_id to agent for MCP calls
        result = await agent.chat(
            message=chat_request.message,
            user_id=chat_request.user_id,
            channel=chat_request.channel,
            context=chat_request.context,
            request_id=request_id  # Pass to agent
        )

        logger.info("chat_response_sent",
                    response_length=len(result.get("text", "")))

        return ChatResponse(**result)

    except Exception as e:
        logger.error("chat_error",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )
    finally:
        # Clear request context
        clear_request_context()


@app.post("/clear-history/{user_id}", response_model=ClearHistoryResponse)
async def clear_history(
    user_id: str,
    channel: str = "telegram"
):
    """
    Clear conversation history for a user.

    Useful for:
    - User requests to start fresh
    - Debugging
    - Privacy compliance

    **Example:**
    ```
    POST /clear-history/123456789?channel=telegram
    ```
    """
    try:
        agent.clear_conversation(user_id, channel)

        logger.info(f"🗑️ Cleared history for {channel}:{user_id}")

        return ClearHistoryResponse(
            status="cleared",
            user_id=user_id,
            channel=channel
        )

    except Exception as e:
        logger.error(f"❌ Clear history error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing history: {str(e)}"
        )


@app.get("/products/{user_id}")
async def get_last_products(
    user_id: str,
    channel: str = "telegram"
):
    """
    Get last fetched products for a user.

    Useful for:
    - Telegram bot to send product images
    - Web widget to display product cards

    **Example:**
    ```
    GET /products/123456789?channel=telegram
    ```
    """
    try:
        products = agent.get_last_products(user_id, channel)

        return {
            "user_id": user_id,
            "channel": channel,
            "products": products,
            "count": len(products)
        }

    except Exception as e:
        logger.error(f"❌ Get products error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting products: {str(e)}"
        )


# ===== Startup/Shutdown =====

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("🚀 AI Agent Service started")
    logger.info(f"📡 MCP Server: {agent.mcp_url}")
    logger.info(f"🏪 Shop ID: {agent.shop_id}")
    logger.info(f"🤖 Model: {agent.model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("👋 AI Agent Service shutting down")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
