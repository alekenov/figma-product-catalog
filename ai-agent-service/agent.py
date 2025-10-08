"""
Universal AI Agent for Flower Shop built on Claude Sonnet 4.5.
Handles multi-channel conversations, orchestrates MCP tool calls, and returns
Telegram-friendly responses with additional metadata for product galleries.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx
from anthropic import AsyncAnthropic

from prompts import build_system_prompt

logger = logging.getLogger(__name__)


class FlowerShopAgent:
    """Universal AI agent that coordinates Claude API with MCP tools."""

    MAX_HISTORY_TURNS = 4  # number of previous exchanges to keep per user/channel

    def __init__(
        self,
        api_key: str,
        mcp_server_url: str,
        shop_id: int = 8,
        model: Optional[str] = None,
    ) -> None:
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not defined")

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model or os.getenv("MODEL", "claude-sonnet-4-5-20250929")
        self.mcp_url = mcp_server_url.rstrip('/')
        self.shop_id = shop_id

        # Simple in-memory conversation state
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.last_products: Dict[str, List[Dict[str, Any]]] = {}

        # Tool schema cache (fetched from MCP server)
        self._tool_schemas: Optional[List[Dict[str, Any]]] = None
        self._schemas_fetched_at: Optional[float] = None
        self._schema_cache_ttl = 3600  # Cache for 1 hour

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        message: str,
        user_id: str,
        channel: str = "telegram",
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a user message via Claude API and MCP tools."""
        conversation_key = self._conversation_key(channel, user_id)
        logger.info(f"👤 USER {conversation_key}: {message}")

        system_prompt = build_system_prompt(self.shop_id, channel, context)
        history = self.conversations.get(conversation_key, [])

        # Add user message to history
        messages = history + [{"role": "user", "content": message}]

        # Track metadata for this interaction
        tracking_id: Optional[str] = None
        order_number: Optional[str] = None
        list_products_used = False

        # Store request_id for MCP calls
        self._request_id = request_id

        # Call Claude with function calling
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            tools=await self._get_tools_schema(),
        )

        # Process tool calls if any
        while response.stop_reason == "tool_use":
            # Extract tool calls and content from response
            tool_results = []
            assistant_content = []

            for block in response.content:
                if block.type == "tool_use":
                    # Execute tool
                    logger.info(f"🔧 MCP TOOL CALL REQUESTED: {block.name} -> {block.input}")
                    tool_result = await self._call_mcp_tool(
                        tool_name=block.name,
                        tool_input=block.input,
                        user_id=user_id,
                        channel=channel,
                    )

                    # Store metadata for later response
                    if block.name == "create_order" and isinstance(tool_result, dict):
                        tracking_id = tool_result.get("tracking_id")
                        order_number = tool_result.get("orderNumber")
                    if block.name == "list_products":
                        list_products_used = True

                    serialized_output = self._serialize_tool_output(block.name, tool_result)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": serialized_output,
                    })
                    assistant_content.append(block)
                    logger.info(f"📤 Tool result ({block.name}): {serialized_output[:300]}...")

                elif block.type == "text":
                    assistant_content.append(block)

            # Add assistant response with tool calls to history
            messages.append({
                "role": "assistant",
                "content": assistant_content
            })

            # Add tool results to history
            if tool_results:
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue conversation with tool results
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=messages,
                    tools=await self._get_tools_schema(),
                )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if block.type == "text":
                final_text += block.text

        logger.info(f"🤖 ASSISTANT: {final_text[:200]}...")

        # Update conversation memory (only store user/assistant text)
        self._update_history(conversation_key, message, final_text)

        # Keep or clear last products for gallery
        if not list_products_used:
            self.last_products.pop(conversation_key, None)

        return {
            "text": final_text,
            "tracking_id": tracking_id,
            "order_number": order_number,
            "show_products": list_products_used,
        }

    def clear_conversation(self, user_id: str, channel: str = "telegram") -> None:
        """Reset stored history and cached products for a user/channel."""
        conversation_key = self._conversation_key(channel, user_id)
        self.conversations.pop(conversation_key, None)
        self.last_products.pop(conversation_key, None)
        logger.info(f"🗑️ Cleared conversation for {conversation_key}")

    def get_last_products(self, user_id: str, channel: str = "telegram") -> List[Dict[str, Any]]:
        """Return last cached product list for image galleries."""
        conversation_key = self._conversation_key(channel, user_id)
        return self.last_products.get(conversation_key, [])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _conversation_key(self, channel: str, user_id: str) -> str:
        return f"{channel}:{user_id}"

    def _update_history(self, key: str, user_text: str, assistant_text: str) -> None:
        history = self.conversations.get(key, [])
        history = (history + [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ])
        # Retain only last N turns (user+assistant counted as one turn)
        max_messages = self.MAX_HISTORY_TURNS * 2
        if len(history) > max_messages:
            history = history[-max_messages:]
        self.conversations[key] = history

    async def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """Fetch tool schemas from MCP server (with caching)."""
        # Check cache freshness
        if self._tool_schemas and self._schemas_fetched_at:
            age = time.time() - self._schemas_fetched_at
            if age < self._schema_cache_ttl:
                logger.debug(f"💾 Using cached schemas ({len(self._tool_schemas)} tools, age={int(age)}s)")
                return self._tool_schemas

        # Fetch from MCP server
        url = f"{self.mcp_url}/tools/schema"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            # Cache result
            self._tool_schemas = data.get("schemas", [])
            self._schemas_fetched_at = time.time()
            logger.info(f"📥 Fetched {len(self._tool_schemas)} tool schemas from MCP server")

            return self._tool_schemas

        except Exception as exc:
            logger.error(f"❌ Failed to fetch schemas from {url}: {exc}")
            # Return empty list as fallback
            return []

    async def _call_mcp_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        user_id: str,
        channel: str,
    ) -> Any:
        """Call MCP server tool via HTTP and handle book-keeping."""
        tool_input = dict(tool_input or {})
        # Normalize specific arguments before sending to MCP
        self._normalize_tool_arguments(tool_name, tool_input)

        tools_requiring_shop_id = {"list_products", "get_product", "create_order", "get_shop_settings", "get_working_hours", "track_order_by_phone"}
        if tool_name in tools_requiring_shop_id:
            tool_input.setdefault("shop_id", self.shop_id)

        if tool_name == "create_order" and channel == "telegram":
            tool_input.setdefault("telegram_user_id", user_id)

        url = f"{self.mcp_url}/call-tool"
        payload = {"name": tool_name, "arguments": tool_input}

        # Build headers with request_id for tracing
        headers = {}
        if hasattr(self, '_request_id') and self._request_id:
            headers["X-Request-ID"] = self._request_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

        content = result.get("result", result)

        # Cache products for gallery display
        if tool_name == "list_products" and isinstance(content, list):
            key = self._conversation_key(channel, user_id)
            self.last_products[key] = content
            logger.info(f"💾 Cached {len(content)} products for {key}")

        return content

    def _normalize_tool_arguments(self, tool_name: str, args: Dict[str, Any]) -> None:
        """Adjust argument values to match MCP expectations."""
        if tool_name == "create_order":
            # Normalize delivery_date tokens (model may use snake_case)
            mapping = {
                "day_after_tomorrow": "day after tomorrow",
                "day-after-tomorrow": "day after tomorrow",
            }
            date_value = args.get("delivery_date")
            if isinstance(date_value, str):
                key = date_value.strip().lower()
                if key in mapping:
                    args["delivery_date"] = mapping[key]
            time_value = args.get("delivery_time")
            if isinstance(time_value, str):
                key = time_value.strip().lower()
                if key in mapping:
                    args["delivery_time"] = mapping[key]
        # NOTE: update_order normalization removed - MCP Server handles delivery_time -> scheduled_time conversion

    def _serialize_tool_output(self, tool_name: str, result: Any) -> str:
        """Return compact JSON string for feeding back into the model."""
        try:
            if tool_name == "list_products" and isinstance(result, list):
                trimmed = []
                for product in result[:8]:
                    trimmed.append({
                        "id": product.get("id"),
                        "name": product.get("name"),
                        "price": product.get("price"),
                        "description": product.get("description"),
                        "images": (product.get("images") or [])[:1],
                        "type": product.get("type"),
                    })
                payload = {"products": trimmed, "total": len(result)}
                return json.dumps(payload, ensure_ascii=False)

            if tool_name == "create_order" and isinstance(result, dict):
                payload = {
                    "orderNumber": result.get("orderNumber"),
                    "tracking_id": result.get("tracking_id"),
                    "status": result.get("status"),
                    "delivery_date": result.get("delivery_date"),
                    "delivery_address": result.get("delivery_address"),
                    "scheduled_time": result.get("scheduled_time"),
                }
                return json.dumps(payload, ensure_ascii=False)

            if tool_name in {"track_order", "update_order"}:
                return json.dumps(result, ensure_ascii=False)

            if tool_name in {"get_shop_settings", "get_working_hours", "get_product"}:
                return json.dumps(result, ensure_ascii=False)

            return json.dumps(result, ensure_ascii=False)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"❌ Failed to serialize tool result ({tool_name}): {exc}")
            return json.dumps({"error": "serialization_failed"}, ensure_ascii=False)
