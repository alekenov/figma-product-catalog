"""
HTTP Wrapper for FastMCP Server - Refactored

Uses ToolRegistry for automatic tool discovery instead of hardcoded mappings.
Eliminates manual tool list maintenance.
"""
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

# Configure structured logging FIRST
from core.logging import configure_logging, get_logger, bind_request_context, clear_request_context

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Import core infrastructure
from core.registry import ToolRegistry

# Import server to trigger tool registration
import server

app = FastAPI(title="MCP HTTP Wrapper - Refactored")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CallToolRequest(BaseModel):
    """Request model for /call-tool endpoint"""
    name: str
    arguments: Optional[Dict[str, Any]] = None


class CallToolResponse(BaseModel):
    """Response model for /call-tool endpoint"""
    result: Any
    error: Optional[str] = None


@app.get("/health")
async def health():
    """
    Health check endpoint for Railway/monitoring systems.
    Checks backend API connectivity.
    """
    from datetime import datetime
    import httpx

    backend_status = "unknown"
    backend_error = None

    # Check backend API connectivity
    try:
        backend_url = os.getenv("API_BASE_URL", "http://localhost:8014/api/v1")
        # Strip /api/v1 to get base URL for health check
        base_url = backend_url.replace("/api/v1", "")

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            if response.status_code == 200:
                backend_status = "healthy"
            else:
                backend_status = "degraded"
                backend_error = f"Status code: {response.status_code}"
    except Exception as e:
        backend_status = "unhealthy"
        backend_error = str(e)[:100]

    # Overall status
    overall_status = "healthy" if backend_status == "healthy" else "degraded"

    response_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mcp-server",
        "version": "1.0.0",
        "backend_url": os.getenv("API_BASE_URL", "http://localhost:8014/api/v1"),
        "dependencies": {
            "backend_api": {
                "status": backend_status,
                "error": backend_error
            }
        }
    }

    # Return 503 if degraded (for load balancers)
    status_code = 200 if overall_status == "healthy" else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(content=response_data, status_code=status_code)


@app.post("/call-tool", response_model=CallToolResponse)
async def call_tool(tool_request: CallToolRequest, request: Request):
    """
    Call an MCP tool by name with arguments.

    Uses ToolRegistry for automatic tool discovery.
    No hardcoded tool lists required!
    """
    # Extract request_id from headers
    request_id = request.headers.get("x-request-id", f"req_mcp_{id(request)}")

    # Bind request context for structured logging
    bind_request_context(
        request_id=request_id,
        tool_name=tool_request.name
    )

    try:
        logger.info("tool_call_started",
                    arguments_count=len(tool_request.arguments or {}))

        # Get tool function from registry
        tool_func = ToolRegistry.get_tool(tool_request.name)

        if tool_func is None:
            available_tools = ToolRegistry.list_tools()
            logger.error("tool_not_found",
                        available_tools_count=len(available_tools))
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_request.name}' not found. Available tools: {', '.join(available_tools[:5])}..."
            )

        # Call the tool with arguments
        kwargs = tool_request.arguments or {}

        # Add request_id to kwargs only if tool accepts it
        # Check function signature to avoid unexpected keyword argument errors
        import inspect
        tool_params = inspect.signature(tool_func).parameters
        if "request_id" in tool_params:
            kwargs["request_id"] = request_id
            logger.debug("request_id_added", tool_has_request_id=True)
        else:
            logger.debug("request_id_skipped", tool_has_request_id=False)

        result = await tool_func(**kwargs)

        logger.info("tool_call_completed")

        return CallToolResponse(result=result, error=None)

    except HTTPException:
        raise

    except Exception as e:
        logger.error("tool_call_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        return CallToolResponse(
            result=None,
            error=str(e)
        )
    finally:
        # Clear request context
        clear_request_context()


@app.get("/tools")
async def list_available_tools():
    """List all available MCP tools with metadata."""
    tools = []
    for name in ToolRegistry.list_tools():
        metadata = ToolRegistry.get_metadata(name)
        tools.append({
            "name": name,
            "domain": metadata.domain,
            "requires_auth": metadata.requires_auth,
            "is_public": metadata.is_public,
            "description": metadata.description.split("\n")[0] if metadata.description else ""
        })

    return {
        "total": len(tools),
        "tools": sorted(tools, key=lambda x: (x["domain"], x["name"]))
    }


@app.get("/tools/schema")
async def get_tools_schema():
    """
    Get Claude-compatible schemas for all registered tools.

    This endpoint auto-generates schemas from Python type annotations,
    eliminating the need for hardcoded schema definitions in client code.

    Returns:
        JSON array of Claude tool schemas with input_schema format
    """
    try:
        schemas = ToolRegistry.generate_all_schemas()

        logger.info(f"schema_generated", tool_count=len(schemas))

        return {
            "schemas": schemas,
            "total": len(schemas),
            "generated_at": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"schema_generation_failed", error=str(e), exc_info=True)
        return {
            "schemas": [],
            "total": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    print(f"🌸 Starting MCP HTTP Wrapper (Refactored) on port {port}")
    print(f"📡 Backend API: {os.getenv('API_BASE_URL', 'http://localhost:8014/api/v1')}")
    print(f"🏪 Shop ID: {os.getenv('DEFAULT_SHOP_ID', '8')}")
    print(f"🔧 Registered Tools: {len(ToolRegistry.list_tools())}")

    # Validate registry
    try:
        ToolRegistry.validate()
        logger.info("✅ ToolRegistry validated successfully")
    except ValueError as e:
        logger.error(f"❌ ToolRegistry validation failed: {e}")
        raise

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
