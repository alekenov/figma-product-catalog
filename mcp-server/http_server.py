"""
HTTP wrapper for MCP server tools.
Exposes MCP tools via simple FastAPI HTTP endpoints.
"""

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn

# Import all tools from server
from server import (
    login, get_current_user,
    list_products, get_product, create_product, update_product,
    list_orders, get_order, create_order, update_order_status, track_order,
    list_warehouse_items, add_warehouse_stock,
    get_shop_settings, update_shop_settings
)

app = FastAPI(title="MCP HTTP Server")

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolCallResponse(BaseModel):
    result: Any

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/call-tool")
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """
    Call an MCP tool by name with arguments.
    """
    tool_name = request.name
    args = request.arguments

    # Map tool names to functions
    tools = {
        "login": login,
        "get_current_user": get_current_user,
        "list_products": list_products,
        "get_product": get_product,
        "create_product": create_product,
        "update_product": update_product,
        "list_orders": list_orders,
        "get_order": get_order,
        "create_order": create_order,
        "update_order_status": update_order_status,
        "track_order": track_order,
        "list_warehouse_items": list_warehouse_items,
        "add_warehouse_stock": add_warehouse_stock,
        "get_shop_settings": get_shop_settings,
        "update_shop_settings": update_shop_settings,
    }

    if tool_name not in tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    try:
        tool_func = tools[tool_name]
        result = await tool_func(**args)
        return ToolCallResponse(result=result)
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid arguments: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
