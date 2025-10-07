"""
Universal AI Agent for Flower Shop built on Claude Sonnet 4.5.
Handles multi-channel conversations, orchestrates MCP tool calls, and returns
Telegram-friendly responses with additional metadata for product galleries.
"""

import json
import logging
import os
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        message: str,
        user_id: str,
        channel: str = "telegram",
        context: Optional[Dict[str, Any]] = None,
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

        # Call Claude with function calling
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            tools=self._get_tools_schema(),
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
                    if block.name == "list_products" and isinstance(tool_result, list):
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
                    tools=self._get_tools_schema(),
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

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """Definitions for all MCP tools exposed to Claude (using input_schema format)."""
        return [
            {
                "name": "list_products",
                "description": "Получить список товаров магазина с фильтрами поиска.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "search": {"type": "string", "description": "Запрос поиска (например, 'розы')"},
                        "product_type": {
                            "type": "string",
                            "enum": ["flowers", "sweets", "fruits", "gifts"],
                            "description": "Категория товара, если известна"
                        },
                        "min_price": {"type": "integer", "description": "Минимальная цена в тиынах"},
                        "max_price": {"type": "integer", "description": "Максимальная цена в тиынах"},
                        "limit": {"type": "integer", "description": "Количество результатов", "default": 20},
                    },
                },
            },
            {
                "name": "get_product",
                "description": "Получить подробную информацию о товаре по ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "integer", "description": "ID товара"},
                    },
                    "required": ["product_id"],
                },
            },
            {
                "name": "create_order",
                "description": "Создать новый заказ на доставку цветов. Требуются данные клиента, адрес, дата, время и товары.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string", "description": "Имя заказчика (человек, который платит)"},
                        "customer_phone": {"type": "string", "description": "Телефон заказчика (человек, который платит)"},
                        "delivery_address": {"type": "string"},
                        "delivery_date": {"type": "string", "description": "Например: 'сегодня', 'завтра', '2025-02-14'"},
                        "delivery_time": {"type": "string", "description": "Например: 'утром', 'вечером', '18:30'"},
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "integer"},
                                    "quantity": {"type": "integer", "minimum": 1},
                                },
                                "required": ["product_id", "quantity"],
                            },
                        },
                        "total_price": {"type": "integer", "description": "Итоговая стоимость в тиынах"},
                        "notes": {"type": "string", "description": "Дополнительные пожелания"},
                        "recipient_name": {"type": "string", "description": "Имя получателя (человек, которому доставляют цветы). Если не указано, то = customer_name"},
                        "recipient_phone": {"type": "string", "description": "Телефон получателя (человек, которому доставляют цветы). Если не указано, то = customer_phone"},
                        "sender_phone": {"type": "string", "description": "Телефон отправителя (дубликат customer_phone для ясности)"},
                    },
                    "required": [
                        "customer_name",
                        "customer_phone",
                        "delivery_address",
                        "delivery_date",
                        "delivery_time",
                        "items",
                        "total_price",
                    ],
                },
            },
            {
                "name": "track_order",
                "description": "Получить статус заказа по tracking ID (9 цифр).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tracking_id": {"type": "string", "description": "Цифровой tracking ID"},
                    },
                    "required": ["tracking_id"],
                },
            },
            {
                "name": "update_order",
                "description": "Обновить заказ по tracking ID (адрес, время, комментарии).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tracking_id": {"type": "string"},
                        "delivery_address": {"type": "string"},
                        "delivery_date": {"type": "string"},
                        "delivery_time": {"type": "string"},
                        "delivery_notes": {"type": "string"},
                        "notes": {"type": "string"},
                        "recipient_name": {"type": "string"},
                    },
                    "required": ["tracking_id"],
                },
            },
            {
                "name": "get_shop_settings",
                "description": "Публичная информация о магазине (адрес, способы оплаты, контакты).",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_working_hours",
                "description": "График работы магазина на неделю.",
                "input_schema": {"type": "object", "properties": {}},
            },
        ]

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

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
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
        if tool_name == "update_order":
            # Align field names with backend expectations
            if "delivery_time" in args:
                args["scheduled_time"] = args.pop("delivery_time")

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
