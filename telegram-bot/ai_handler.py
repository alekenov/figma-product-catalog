"""
Claude AI Handler with Function Calling integration.
Handles natural language understanding and tool invocation via MCP.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from mcp_client import MCPClient

logger = logging.getLogger(__name__)

# Conversation logs directory
CONVERSATION_LOG_DIR = Path(__file__).parent / "conversation_logs"
CONVERSATION_LOG_DIR.mkdir(exist_ok=True)


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
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

        # Conversation history per user
        self.conversations: Dict[int, List[Dict[str, Any]]] = {}

        # Store last products with images (per user) for sending photos
        self.last_products: Dict[int, List[Dict[str, Any]]] = {}

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
- Для заказа нужны: имя, телефон, адрес доставки, дата, время, список товаров
- Будь вежливым и помогай клиенту на русском языке

**ОБРАБОТКА ДАТ И ВРЕМЕНИ:**

НЕ СПРАШИВАЙ формат даты/времени если клиент указал:
- Дата: "сегодня", "завтра", "послезавтра", "через N дней"
- Время: "утром", "днем", "вечером", "как можно скорее", "через N часов"

Если указано только "как можно скорее" без даты → используй delivery_date="сегодня"

**ПРИМЕРЫ КОРРЕКТНЫХ ЗАКАЗОВ:**
• Клиент: "как можно скорее" → create_order(delivery_date="сегодня", delivery_time="как можно скорее", ...)
• Клиент: "завтра утром" → create_order(delivery_date="завтра", delivery_time="утром", ...)
• Клиент: "послезавтра" → create_order(delivery_date="послезавтра", delivery_time="как можно скорее", ...)
• Клиент: "сегодня днем" → create_order(delivery_date="сегодня", delivery_time="днем", ...)

**ФОРМАТ ПОДТВЕРЖДЕНИЯ ЗАКАЗА:**

После успешного create_order ОБЯЗАТЕЛЬНО покажи:
- Номер заказа (orderNumber, например #12357)
- КЛИКАБЕЛЬНУЮ ССЫЛКУ для отслеживания заказа используя tracking_id

Формат подтверждения:
```
✅ Заказ успешно оформлен!

📦 Номер заказа: [orderNumber]
🔗 Отследить заказ: https://cvety-website.pages.dev/status/[tracking_id]

[детали заказа...]
```

ВАЖНО: Ссылка на отслеживание ДОЛЖНА быть кликабельной и содержать tracking_id из ответа create_order.

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
                "description": "Создать новый заказ на доставку цветов. Возвращает объект с полями: orderNumber (номер заказа, например #12357), tracking_id (9-значный ID для отслеживания, например 901637313), и другие детали заказа. ОБЯЗАТЕЛЬНО используй tracking_id для создания ссылки отслеживания: https://cvety-website.pages.dev/status/{tracking_id}",
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
                            "description": "Адрес доставки. Передавай фразу клиента БЕЗ преобразований. ЕСЛИ клиент просит 'уточнить у получателя' или 'курьер позвонит' - передавай именно эту фразу. Примеры валидных адресов: 'Астана, мкр Самал 2, дом 5', 'уточнить у получателя', 'мкр Самал, курьер позвонит для уточнения', 'адрес получатель скажет курьеру'. НЕ требуй конкретный адрес если клиент его не знает."
                        },
                        "delivery_date": {
                            "type": "string",
                            "description": "Передавай фразу клиента БЕЗ преобразований. Примеры: 'сегодня', 'завтра', 'послезавтра', 'через 2 дня'. ЕСЛИ клиент сказал 'как можно скорее' без указания даты — используй 'сегодня'. ЗАПРЕЩЕНО просить клиента указать дату в формате YYYY-MM-DD."
                        },
                        "delivery_time": {
                            "type": "string",
                            "description": "Передавай фразу клиента БЕЗ преобразований. Примеры: 'утром', 'днем', 'вечером', 'как можно скорее', 'через 2 часа'. ЕСЛИ клиент сказал 'как можно скорее' — передавай ровно 'как можно скорее'. ЗАПРЕЩЕНО просить клиента указать время в формате HH:MM."
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
        tool_input: Dict[str, Any],
        user_id: int
    ) -> str:
        """
        Execute a tool call via MCP client.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool arguments
            user_id: Telegram user ID for storing product results and order identification

        Returns:
            String representation of tool result
        """
        # Add shop_id to all tool calls
        tool_input["shop_id"] = self.shop_id

        # Add telegram_user_id for order creation
        if tool_name == "create_order":
            tool_input["telegram_user_id"] = str(user_id)
            logger.info(f"📱 Added telegram_user_id: {user_id}")

        logger.info(f"🔧 TOOL CALL: {tool_name}")
        logger.info(f"📥 Arguments: {tool_input}")

        try:
            if tool_name == "list_products":
                result = await self.mcp_client.list_products(**tool_input)
                # Store products for image sending
                if isinstance(result, list):
                    self.last_products[user_id] = result
                    logger.info(f"💾 Saved {len(result)} products for user {user_id}")
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
                logger.error(f"❌ Unknown tool: {tool_name}")
                return f"Ошибка: неизвестная функция {tool_name}"

            logger.info(f"📤 Tool result: {str(result)[:200]}...")  # First 200 chars
            return str(result)

        except Exception as e:
            logger.error(f"❌ Tool execution error: {str(e)}")
            return f"Ошибка при выполнении {tool_name}: {str(e)}"

    def _save_conversation_log(self, user_id: int, message: str, response: str, tool_calls: List[Dict[str, Any]]):
        """Save conversation to JSON log file."""
        try:
            log_file = CONVERSATION_LOG_DIR / f"user_{user_id}_{datetime.now().strftime('%Y%m%d')}.jsonl"

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "user_message": message,
                "ai_response": response,
                "tool_calls": tool_calls,
                "conversation_length": len(self.conversations.get(user_id, []))
            }

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            logger.info(f"💾 Conversation logged to: {log_file}")
        except Exception as e:
            logger.error(f"❌ Error saving conversation log: {e}")

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
        logger.info(f"👤 USER {user_id}: {message}")

        tool_calls_log = []

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
                    # Log tool call
                    tool_calls_log.append({
                        "tool": block.name,
                        "input": block.input
                    })

                    # Execute tool
                    tool_result = await self._execute_tool(
                        block.name,
                        block.input,
                        user_id
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

        logger.info(f"🤖 AI RESPONSE: {final_text}")

        # Add final response to history
        self.conversations[user_id].append({
            "role": "assistant",
            "content": final_text
        })

        # Limit conversation history to last 20 messages
        if len(self.conversations[user_id]) > 20:
            self.conversations[user_id] = self.conversations[user_id][-20:]

        # Save conversation to log file
        self._save_conversation_log(user_id, message, final_text, tool_calls_log)

        return final_text

    def clear_conversation(self, user_id: int):
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
        if user_id in self.last_products:
            del self.last_products[user_id]

    def get_last_product_images(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get product images from last list_products call for sending to Telegram.

        Returns:
            List of dicts with {url, caption} for each product with image
        """
        products = self.last_products.get(user_id, [])
        images = []

        for product in products:
            if product.get("image"):
                # Format price from tiyins to tenge
                price = product.get("price", 0)
                price_tenge = price // 100 if price else 0

                caption = f"{product.get('name', 'Продукт')}\n💰 {price_tenge:,} ₸".replace(',', ' ')

                images.append({
                    "url": product["image"],
                    "caption": caption
                })

        logger.info(f"📸 Found {len(images)} product images for user {user_id}")
        return images
