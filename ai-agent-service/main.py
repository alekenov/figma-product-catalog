"""
AI Agent Service - FastAPI HTTP Server
Provides universal chat API for all channels (Telegram, WhatsApp, Web, Instagram).
"""
import os
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent import FlowerShopAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
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
    try:
        logger.info(f"📨 Incoming chat request: {request.channel}:{request.user_id}")

        result = await agent.chat(
            message=request.message,
            user_id=request.user_id,
            channel=request.channel,
            context=request.context
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}", exc_info=True)  # Include full traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


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
