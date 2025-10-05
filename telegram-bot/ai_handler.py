"""
Claude AI Handler with Function Calling integration.
Handles natural language understanding and tool invocation via MCP.
"""
import os
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from mcp_client import MCPClient


class AIHandler:
    """Handles AI conversation and function calling via Claude."""

    def __init__(
        self,
        mcp_client: MCPClient,
        shop_id: int,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.mcp_client = mcp_client
        self.shop_id = shop_id

        # Initialize Claude client
        self.client = Anthropic(
            api_key=api_key or os.getenv("CLAUDE_API_KEY")
        )
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

        # Conversation history per user
        self.conversations: Dict[int, List[Dict[str, Any]]] = {}

    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude."""
        return f"""Ты — AI-ассистент цветочного магазина. Твоя задача помогать клиентам:

1. **Показывать каталог цветов** - используй list_products для поиска
2. **Оформлять заказы** - собери данные (имя, телефон, адрес, дату, время, товары) и вызови create_order
3. **Отслеживать заказы** - используй track_order_by_phone с номером телефона клиента
4. **Отвечать на вопросы** - о режиме работы (get_working_hours), настройках магазина (get_shop_settings)

**Важные правила:**
- Всегда используй shop_id={self.shop_id} при вызове функций
- Цены указываются в тиынах (1 тенге = 100 тиынов), показывай клиенту в тенге
- Даты в формате YYYY-MM-DD, время в формате HH:MM
- Для заказа нужны: имя, телефон, адрес доставки, дата, время, список товаров
- Будь вежливым и помогай клиенту на русском языке

**ID магазина**: {self.shop_id}
"""

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """Define Claude function calling tools schema."""
        return [
            {
                "name": "list_products",
                "description": "Получить список цветов и букетов с фильтрацией по названию, типу, цене",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "search": {
                            "type": "string",
                            "description": "Поиск по названию продукта"
                        },
                        "product_type": {
                            "type": "string",
                            "enum": ["ready", "custom", "subscription"],
                            "description": "Тип товара: ready (готовый букет), custom (на заказ), subscription (подписка)"
                        },
                        "min_price": {
                            "type": "integer",
                            "description": "Минимальная цена в тиынах (1 тенге = 100 тиынов)"
                        },
                        "max_price": {
                            "type": "integer",
                            "description": "Максимальная цена в тиынах"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Количество результатов (по умолчанию 20)",
                            "default": 20
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_product",
                "description": "Получить подробную информацию о конкретном товаре по ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "ID товара"
                        }
                    },
                    "required": ["product_id"]
                }
            },
            {
                "name": "create_order",
                "description": "Создать новый заказ на доставку цветов",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Полное имя клиента"
                        },
                        "customer_phone": {
                            "type": "string",
                            "description": "Номер телефона клиента"
                        },
                        "delivery_address": {
                            "type": "string",
                            "description": "Адрес доставки"
                        },
                        "delivery_date": {
                            "type": "string",
                            "description": "Дата доставки в формате YYYY-MM-DD"
                        },
                        "delivery_time": {
                            "type": "string",
                            "description": "Время доставки в формате HH:MM"
                        },
                        "items": {
                            "type": "array",
                            "description": "Список товаров в заказе",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "integer"},
                                    "quantity": {"type": "integer"}
                                },
                                "required": ["product_id", "quantity"]
                            }
                        },
                        "total_price": {
                            "type": "integer",
                            "description": "Общая сумма заказа в тиынах"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Дополнительные пожелания к заказу"
                        }
                    },
                    "required": [
                        "customer_name",
                        "customer_phone",
                        "delivery_address",
                        "delivery_date",
                        "delivery_time",
                        "items",
                        "total_price"
                    ]
                }
            },
            {
                "name": "track_order_by_phone",
                "description": "Отследить заказы клиента по номеру телефона",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_phone": {
                            "type": "string",
                            "description": "Номер телефона клиента"
                        }
                    },
                    "required": ["customer_phone"]
                }
            },
            {
                "name": "get_working_hours",
                "description": "Получить расписание работы магазина на неделю",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_shop_settings",
                "description": "Получить настройки и информацию о магазине",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def _execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> str:
        """
        Execute a tool call via MCP client.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool arguments

        Returns:
            String representation of tool result
        """
        # Add shop_id to all tool calls
        tool_input["shop_id"] = self.shop_id

        try:
            if tool_name == "list_products":
                result = await self.mcp_client.list_products(**tool_input)
            elif tool_name == "get_product":
                result = await self.mcp_client.get_product(**tool_input)
            elif tool_name == "create_order":
                result = await self.mcp_client.create_order(**tool_input)
            elif tool_name == "track_order_by_phone":
                result = await self.mcp_client.track_order_by_phone(**tool_input)
            elif tool_name == "get_working_hours":
                result = await self.mcp_client.get_working_hours(**tool_input)
            elif tool_name == "get_shop_settings":
                result = await self.mcp_client.get_shop_settings(**tool_input)
            else:
                return f"Ошибка: неизвестная функция {tool_name}"

            return str(result)

        except Exception as e:
            return f"Ошибка при выполнении {tool_name}: {str(e)}"

    async def process_message(
        self,
        user_id: int,
        message: str
    ) -> str:
        """
        Process user message with AI and execute function calls.

        Args:
            user_id: Telegram user ID for conversation tracking
            message: User's text message

        Returns:
            AI response text
        """
        # Initialize conversation if needed
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        # Add user message to history
        self.conversations[user_id].append({
            "role": "user",
            "content": message
        })

        # Call Claude with function calling
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self._get_system_prompt(),
            messages=self.conversations[user_id],
            tools=self._get_tools_schema()
        )

        # Process tool calls if any
        while response.stop_reason == "tool_use":
            # Extract tool calls and text from response
            tool_results = []
            assistant_content = []

            for block in response.content:
                if block.type == "tool_use":
                    # Execute tool
                    tool_result = await self._execute_tool(
                        block.name,
                        block.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result
                    })
                    assistant_content.append(block)
                elif block.type == "text":
                    assistant_content.append(block)

            # Add assistant response with tool calls to history
            self.conversations[user_id].append({
                "role": "assistant",
                "content": assistant_content
            })

            # Add tool results to history
            if tool_results:
                self.conversations[user_id].append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue conversation with tool results
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self._get_system_prompt(),
                    messages=self.conversations[user_id],
                    tools=self._get_tools_schema()
                )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if block.type == "text":
                final_text += block.text

        # Add final response to history
        self.conversations[user_id].append({
            "role": "assistant",
            "content": final_text
        })

        # Limit conversation history to last 20 messages
        if len(self.conversations[user_id]) > 20:
            self.conversations[user_id] = self.conversations[user_id][-20:]

        return final_text

    def clear_conversation(self, user_id: int):
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
