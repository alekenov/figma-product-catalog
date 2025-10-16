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
    list_orders, get_order, create_order, update_order_status, update_order, track_order, track_order_by_phone,
    list_warehouse_items, add_warehouse_stock,
    get_telegram_client, register_telegram_client,
    get_shop_settings, get_working_hours, update_shop_settings
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

@app.get("/tools/schema")
async def tools_schema():
    """
    Return JSON Schema for all available MCP tools.
    Format expected by Claude's Tool Use API.
    """
    schemas = [
        {
            "name": "login",
            "description": "Authenticate user and get access token",
            "input_schema": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "User phone number"},
                    "password": {"type": "string", "description": "User password"}
                },
                "required": ["phone", "password"]
            }
        },
        {
            "name": "get_current_user",
            "description": "Get current authenticated user information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"}
                },
                "required": ["token"]
            }
        },
        {
            "name": "list_products",
            "description": "Get list of products with filtering options",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shop_id": {"type": "integer", "description": "Shop ID"},
                    "search": {"type": "string", "description": "Search query for product name"},
                    "product_type": {"type": "string", "description": "Filter by type: flowers, sweets, fruits, gifts", "enum": ["flowers", "sweets", "fruits", "gifts"]},
                    "enabled_only": {"type": "boolean", "description": "Show only enabled products", "default": True},
                    "min_price": {"type": "integer", "description": "Minimum price in kopecks"},
                    "max_price": {"type": "integer", "description": "Maximum price in kopecks"},
                    "skip": {"type": "integer", "description": "Number of items to skip", "default": 0},
                    "limit": {"type": "integer", "description": "Number of items to return", "default": 20}
                },
                "required": []
            }
        },
        {
            "name": "get_product",
            "description": "Get detailed information about a specific product",
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "Product ID"},
                    "shop_id": {"type": "integer", "description": "Shop ID"}
                },
                "required": ["product_id"]
            }
        },
        {
            "name": "create_product",
            "description": "Create a new product (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "name": {"type": "string", "description": "Product name"},
                    "type": {"type": "string", "description": "Product type: flowers, sweets, fruits, gifts", "enum": ["flowers", "sweets", "fruits", "gifts"]},
                    "price": {"type": "integer", "description": "Price in kopecks"},
                    "description": {"type": "string", "description": "Product description"},
                    "enabled": {"type": "boolean", "description": "Is product enabled", "default": True}
                },
                "required": ["token", "name", "type", "price"]
            }
        },
        {
            "name": "update_product",
            "description": "Update an existing product (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "product_id": {"type": "integer", "description": "Product ID"},
                    "name": {"type": "string", "description": "Product name"},
                    "price": {"type": "integer", "description": "Price in kopecks"},
                    "description": {"type": "string", "description": "Product description"},
                    "enabled": {"type": "boolean", "description": "Is product enabled"}
                },
                "required": ["token", "product_id"]
            }
        },
        {
            "name": "create_order",
            "description": "Create a new order for a customer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "customer_phone": {"type": "string", "description": "Customer phone number"},
                    "delivery_date": {"type": "string", "description": "Delivery date: 'today', 'tomorrow', 'day after tomorrow', or ISO date"},
                    "delivery_time": {"type": "string", "description": "Delivery time: '10:00-12:00', '14:00-16:00', etc."},
                    "shop_id": {"type": "integer", "description": "Shop ID"},
                    "items": {"type": "array", "description": "Array of order items with product_id and quantity", "items": {"type": "object"}},
                    "total_price": {"type": "integer", "description": "Total price in kopecks"},
                    "delivery_type": {"type": "string", "description": "Delivery type: 'delivery' or 'pickup'", "default": "delivery"},
                    "delivery_address": {"type": "string", "description": "Delivery address (required for delivery type)"},
                    "pickup_address": {"type": "string", "description": "Pickup address (optional for pickup type)"},
                    "notes": {"type": "string", "description": "Order notes"},
                    "telegram_user_id": {"type": "string", "description": "Telegram user ID"},
                    "recipient_name": {"type": "string", "description": "Recipient name"},
                    "recipient_phone": {"type": "string", "description": "Recipient phone"},
                    "sender_phone": {"type": "string", "description": "Sender phone"}
                },
                "required": ["customer_name", "customer_phone", "delivery_date", "delivery_time", "shop_id", "items", "total_price"]
            }
        },
        {
            "name": "get_telegram_client",
            "description": "Get telegram client by telegram_user_id and shop_id",
            "input_schema": {
                "type": "object",
                "properties": {
                    "telegram_user_id": {"type": "string", "description": "Telegram user ID"},
                    "shop_id": {"type": "integer", "description": "Shop ID"}
                },
                "required": ["telegram_user_id", "shop_id"]
            }
        },
        {
            "name": "register_telegram_client",
            "description": "Register or update a telegram client with contact information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "telegram_user_id": {"type": "string", "description": "Telegram user ID"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "shop_id": {"type": "integer", "description": "Shop ID"},
                    "telegram_username": {"type": "string", "description": "Telegram username"},
                    "telegram_first_name": {"type": "string", "description": "Telegram first name"}
                },
                "required": ["telegram_user_id", "phone", "customer_name", "shop_id"]
            }
        },
        {
            "name": "get_shop_settings",
            "description": "Get public shop settings and configuration",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shop_id": {"type": "integer", "description": "Shop ID"}
                },
                "required": ["shop_id"]
            }
        },
        {
            "name": "get_working_hours",
            "description": "Get shop working hours schedule",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shop_id": {"type": "integer", "description": "Shop ID"}
                },
                "required": ["shop_id"]
            }
        },
        {
            "name": "update_shop_settings",
            "description": "Update shop settings (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "shop_name": {"type": "string", "description": "Shop name"},
                    "description": {"type": "string", "description": "Shop description"},
                    "phone": {"type": "string", "description": "Shop phone"},
                    "email": {"type": "string", "description": "Shop email"},
                    "address": {"type": "string", "description": "Shop address"}
                },
                "required": ["token"]
            }
        },
        {
            "name": "list_orders",
            "description": "Get list of orders with filtering (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "status": {"type": "string", "description": "Filter by status"},
                    "customer_phone": {"type": "string", "description": "Filter by customer phone"},
                    "search": {"type": "string", "description": "Search query"},
                    "skip": {"type": "integer", "description": "Number of items to skip", "default": 0},
                    "limit": {"type": "integer", "description": "Number of items to return", "default": 20}
                },
                "required": ["token"]
            }
        },
        {
            "name": "get_order",
            "description": "Get detailed information about a specific order (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "order_id": {"type": "integer", "description": "Order ID"}
                },
                "required": ["token", "order_id"]
            }
        },
        {
            "name": "update_order_status",
            "description": "Update order status (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "order_id": {"type": "integer", "description": "Order ID"},
                    "status": {"type": "string", "description": "New status: NEW, PAID, ACCEPTED, IN_PRODUCTION, READY, IN_DELIVERY, DELIVERED, CANCELLED"},
                    "notes": {"type": "string", "description": "Status change notes"}
                },
                "required": ["token", "order_id", "status"]
            }
        },
        {
            "name": "update_order",
            "description": "Update order details by tracking ID (customer-facing)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tracking_id": {"type": "string", "description": "Order tracking ID"},
                    "delivery_address": {"type": "string", "description": "Delivery address"},
                    "delivery_date": {"type": "string", "description": "Delivery date"},
                    "delivery_time": {"type": "string", "description": "Delivery time"},
                    "delivery_notes": {"type": "string", "description": "Delivery notes"},
                    "notes": {"type": "string", "description": "Order notes"},
                    "recipient_name": {"type": "string", "description": "Recipient name"}
                },
                "required": ["tracking_id"]
            }
        },
        {
            "name": "track_order",
            "description": "Track order status by tracking ID (public endpoint)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tracking_id": {"type": "string", "description": "Order tracking ID"}
                },
                "required": ["tracking_id"]
            }
        },
        {
            "name": "track_order_by_phone",
            "description": "Track orders by customer phone number",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_phone": {"type": "string", "description": "Customer phone number"},
                    "shop_id": {"type": "integer", "description": "Shop ID"}
                },
                "required": ["customer_phone", "shop_id"]
            }
        },
        {
            "name": "list_warehouse_items",
            "description": "Get list of warehouse inventory items (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "search": {"type": "string", "description": "Search query"},
                    "skip": {"type": "integer", "description": "Number of items to skip", "default": 0},
                    "limit": {"type": "integer", "description": "Number of items to return", "default": 50}
                },
                "required": ["token"]
            }
        },
        {
            "name": "add_warehouse_stock",
            "description": "Add stock to warehouse item (admin only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "JWT access token"},
                    "warehouse_item_id": {"type": "integer", "description": "Warehouse item ID"},
                    "quantity": {"type": "integer", "description": "Quantity to add"},
                    "notes": {"type": "string", "description": "Operation notes"}
                },
                "required": ["token", "warehouse_item_id", "quantity"]
            }
        }
    ]

    return {"schemas": schemas}

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
        "update_order": update_order,
        "track_order": track_order,
        "track_order_by_phone": track_order_by_phone,
        "list_warehouse_items": list_warehouse_items,
        "add_warehouse_stock": add_warehouse_stock,
        "get_telegram_client": get_telegram_client,
        "register_telegram_client": register_telegram_client,
        "get_shop_settings": get_shop_settings,
        "get_working_hours": get_working_hours,
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
