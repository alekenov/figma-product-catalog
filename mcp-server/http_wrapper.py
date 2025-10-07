"""
HTTP Wrapper для MCP Server
Предоставляет HTTP API endpoint /call-tool для testing framework
"""
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

# Import all MCP tools
from server import (
    # Phase 1: Auth
    login,
    get_current_user,
    # Phase 2: Products
    list_products,
    get_product,
    create_product,
    update_product,
    # Phase 3: Orders
    list_orders,
    get_order,
    create_order,
    update_order_status,
    track_order,
    update_order,
    # Phase 4: Telegram
    get_telegram_client,
    register_telegram_client,
    # Phase 5: Inventory
    list_warehouse_items,
    add_warehouse_stock,
    # Phase 6: Shop
    get_shop_settings,
    get_working_hours,
    update_shop_settings,
    # Phase 1 New Tools
    check_product_availability,
    preview_order_cost,
    get_bestsellers,
    get_featured_products,
    get_faq,
    get_reviews,
    # Phase 2 New Tools
    get_client_profile,
    search_products_smart,
    save_client_address,
    cancel_order,
    # Phase 3 New Tools
    get_delivery_slots,
    validate_delivery_time,
    check_delivery_feasibility,
)

app = FastAPI(title="MCP Server HTTP Wrapper", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolCallRequest(BaseModel):
    """Request model for /call-tool endpoint"""
    name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """Response model for /call-tool endpoint"""
    result: Any
    error: Optional[str] = None


# Map tool names to functions
TOOL_MAP = {
    # Auth
    "login": login,
    "get_current_user": get_current_user,
    # Products
    "list_products": list_products,
    "get_product": get_product,
    "create_product": create_product,
    "update_product": update_product,
    # Orders
    "list_orders": list_orders,
    "get_order": get_order,
    "create_order": create_order,
    "update_order_status": update_order_status,
    "track_order": track_order,
    "update_order": update_order,
    # Telegram
    "get_telegram_client": get_telegram_client,
    "register_telegram_client": register_telegram_client,
    # Inventory
    "list_warehouse_items": list_warehouse_items,
    "add_warehouse_stock": add_warehouse_stock,
    # Shop
    "get_shop_settings": get_shop_settings,
    "get_working_hours": get_working_hours,
    "update_shop_settings": update_shop_settings,
    # Phase 1 New Tools
    "check_product_availability": check_product_availability,
    "preview_order_cost": preview_order_cost,
    "get_bestsellers": get_bestsellers,
    "get_featured_products": get_featured_products,
    "get_faq": get_faq,
    "get_reviews": get_reviews,
    # Phase 2 New Tools
    "get_client_profile": get_client_profile,
    "search_products_smart": search_products_smart,
    "save_client_address": save_client_address,
    "cancel_order": cancel_order,
    # Phase 3 New Tools
    "get_delivery_slots": get_delivery_slots,
    "validate_delivery_time": validate_delivery_time,
    "check_delivery_feasibility": check_delivery_feasibility,
}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": list(TOOL_MAP.keys()),
        "count": len(TOOL_MAP)
    }


@app.post("/call-tool")
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """
    Call an MCP tool by name with given arguments.

    This endpoint matches the interface expected by MCPClient in telegram-bot/mcp_client.py
    """
    tool_name = request.name
    arguments = request.arguments

    # Check if tool exists
    if tool_name not in TOOL_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available tools: {list(TOOL_MAP.keys())}"
        )

    # Get the tool function
    tool_func = TOOL_MAP[tool_name]

    try:
        # Call the tool function
        # Remove None values from arguments
        clean_args = {k: v for k, v in arguments.items() if v is not None}

        result = await tool_func(**clean_args)

        return ToolCallResponse(result=result)

    except TypeError as e:
        # Invalid arguments
        raise HTTPException(
            status_code=400,
            detail=f"Invalid arguments for tool '{tool_name}': {str(e)}"
        )
    except Exception as e:
        # Tool execution error
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}"
        )


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))

    print(f"🌸 MCP HTTP Wrapper starting on port {port}")
    print(f"📡 Endpoints:")
    print(f"   - GET  /health - Health check")
    print(f"   - GET  /tools - List available tools")
    print(f"   - POST /call-tool - Execute MCP tool")
    print(f"✅ Available tools: {len(TOOL_MAP)}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
