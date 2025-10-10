"""
AI Manager Service - Simulates flower shop manager.
Uses Claude 4.5 with MCP tools integration and comprehensive logging.
"""
import sys
import os
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

# Add parent dir to path to import telegram-bot's mcp_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'telegram-bot'))
from mcp_client import MCPClient

import config
from logger_analyzer import TestLogger

logger = logging.getLogger(__name__)


class AIManager:
    """
    AI Manager that simulates a flower shop assistant.
    Uses Claude 4.5 with MCP integration for real backend interaction.
    """

    def __init__(
        self,
        test_logger: TestLogger,
        shop_id: int = None,
        mcp_server_url: str = None
    ):
        """
        Initialize AI Manager.

        Args:
            test_logger: TestLogger instance for logging
            shop_id: Shop ID (defaults to config.SHOP_ID)
            mcp_server_url: MCP server URL (defaults to config.MCP_SERVER_URL)
        """
        self.logger = test_logger
        self.shop_id = shop_id or config.SHOP_ID
        self.mcp_server_url = mcp_server_url or config.MCP_SERVER_URL

        # Initialize Claude client
        self.client = Anthropic(api_key=config.CLAUDE_API_KEY)
        self.model = config.CLAUDE_MODEL_MANAGER

        # Initialize MCP client
        self.mcp_client = MCPClient(self.mcp_server_url)

        # Conversation history
        self.messages: List[Dict[str, Any]] = []

        # Memory directory for this manager
        self.memory_dir = config.MEMORIES_DIR / "manager"
        self.memory_dir.mkdir(exist_ok=True)

        logger.info(f"🤖 AI Manager initialized (model: {self.model})")
        logger.info(f"🔗 MCP Server: {self.mcp_server_url}")
        logger.info(f"🏪 Shop ID: {self.shop_id}")

    def get_system_prompt(self) -> str:
        """Get system prompt for manager AI."""
        # Get current date/time for natural language understanding
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        current_day = now.strftime('%A')  # Day of week in English

        # Russian day names mapping
        day_names_ru = {
            'Monday': 'понедельник',
            'Tuesday': 'вторник',
            'Wednesday': 'среда',
            'Thursday': 'четверг',
            'Friday': 'пятница',
            'Saturday': 'суббота',
            'Sunday': 'воскресенье'
        }
        current_day_ru = day_names_ru.get(current_day, current_day)

        return f"""Ты — профессиональный менеджер цветочного магазина. Твоя задача — помогать клиентам выбрать и заказать цветы.

**ТЕКУЩИЕ ДАТА И ВРЕМЯ:**
- Сегодня: {current_date} ({current_day_ru})
- Сейчас: {current_time}

**Доступные функции (MCP tools):**
- `list_products` - показать каталог букетов с фильтрацией
- `get_product` - получить детальную информацию о конкретном букете
- `create_order` - оформить заказ на доставку (поддерживает естественный язык для дат!)
- `track_order` - отследить статус заказа
- `get_shop_settings` - узнать информацию о магазине
- `get_working_hours` - узнать время работы

**Важные правила:**
1. Всегда используй shop_id={self.shop_id} при вызове функций
2. Цены в базе хранятся в тиынах (1 тенге = 100 тиынов), показывай клиенту в тенге
3. Будь вежливым, внимательным и помогай клиенту сделать правильный выбор
4. Если клиент говорит "недорого" - предложи букеты до 15000тг
5. Всегда уточняй детали доставки (адрес, дата, время)
6. Для заказа нужны: имя, телефон, адрес, дата, время, список товаров

**КРИТИЧЕСКИ ВАЖНО - Работа с датами:**
1. ❌ НИКОГДА не спрашивай клиента "какое сегодня число?" или "в каком формате дата?"
2. ✅ Клиенты используют естественный язык: "сегодня", "завтра", "послезавтра", "как можно скорее"
3. ✅ Функция create_order АВТОМАТИЧЕСКИ понимает:
   - "сегодня" → текущая дата ({current_date})
   - "завтра" → следующий день
   - "послезавтра" → через два дня
   - "через N дней" → соответствующая дата
   - "сегодня к 18:00" → {current_date} + время 18:00
   - "завтра утром" → завтра + 10:00
   - "как можно скорее" → ближайшее доступное время
4. ✅ Просто передавай в create_order то, что сказал клиент ("сегодня", "завтра к 18:00", и т.д.)

**ID магазина:** {self.shop_id}

Отвечай кратко и по делу. Используй функции для получения актуальных данных.
"""

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Define Claude function calling tools schema matching MCP server."""
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
                            "enum": ["flowers", "sweets", "fruits", "gifts"],
                            "description": "Тип товара"
                        },
                        "min_price": {
                            "type": "integer",
                            "description": "Минимальная цена в тиынах"
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
                            "description": "Дата доставки. Поддерживает естественный язык: 'сегодня', 'завтра', 'послезавтра', 'через N дней' или формат YYYY-MM-DD"
                        },
                        "delivery_time": {
                            "type": "string",
                            "description": "Время доставки. Поддерживает естественный язык: 'утром' (10:00), 'днем' (14:00), 'вечером' (18:00), 'как можно скорее' (ближайшее) или формат HH:MM"
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
                "description": "Получить расписание работы магазина",
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

    async def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> str:
        """
        Execute a tool call via MCP client with logging.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool arguments

        Returns:
            String representation of tool result
        """
        # Add shop_id to all tool calls
        tool_input["shop_id"] = self.shop_id

        # Log tool call
        self.logger.log_message(
            sender="manager",
            message_type="tool_call",
            content=f"Calling {tool_name}",
            metadata={
                "tool_name": tool_name,
                "arguments": tool_input
            }
        )

        start_time = time.time()

        try:
            # Call appropriate MCP method
            if tool_name == "list_products":
                result = await self.mcp_client.list_products(**tool_input)
            elif tool_name == "get_product":
                result = await self.mcp_client.get_product(**tool_input)
            elif tool_name == "create_order":
                # Add telegram_user_id placeholder for testing
                tool_input["telegram_user_id"] = "test_client"
                result = await self.mcp_client.create_order(**tool_input)
            elif tool_name == "track_order_by_phone":
                result = await self.mcp_client.track_order_by_phone(**tool_input)
            elif tool_name == "get_working_hours":
                result = await self.mcp_client.get_working_hours(**tool_input)
            elif tool_name == "get_shop_settings":
                result = await self.mcp_client.get_shop_settings(**tool_input)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            latency = (time.time() - start_time) * 1000

            # Log successful tool call
            self.logger.log_tool_call(
                tool_name=tool_name,
                arguments=tool_input,
                result=result,
                latency_ms=latency,
                success=True
            )

            # Log tool result
            self.logger.log_message(
                sender="manager",
                message_type="tool_result",
                content=f"Tool {tool_name} succeeded",
                metadata={
                    "tool_name": tool_name,
                    "result": result
                }
            )

            return str(result)

        except Exception as e:
            latency = (time.time() - start_time) * 1000

            # Log failed tool call
            self.logger.log_tool_call(
                tool_name=tool_name,
                arguments=tool_input,
                latency_ms=latency,
                success=False,
                error=str(e)
            )

            logger.error(f"Tool execution error ({tool_name}): {str(e)}")
            return f"Ошибка при выполнении {tool_name}: {str(e)}"

    async def process_message(self, message: str) -> str:
        """
        Process a message from client and generate response.

        Args:
            message: Client's text message

        Returns:
            Manager's text response
        """
        # Log incoming message
        self.logger.log_message(
            sender="client",
            message_type="text",
            content=message
        )

        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": message
        })

        # Call Claude with function calling and new features
        response = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            system=self.get_system_prompt(),
            messages=self.messages,
            tools=self.get_tools_schema(),
            extra_headers=config.CLAUDE_EXTRA_HEADERS  # Enable memory, context editing, interleaved thinking
        )

        # Process tool calls if any
        while response.stop_reason == "tool_use":
            # Extract tool calls and content from response
            tool_results = []
            assistant_content = []

            for block in response.content:
                if block.type == "thinking":
                    # Log thinking block (interleaved thinking feature)
                    self.logger.log_message(
                        sender="manager",
                        message_type="thinking",
                        content=block.thinking
                    )
                    assistant_content.append(block)

                elif block.type == "tool_use":
                    # Execute tool
                    tool_result = await self.execute_tool(
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
            self.messages.append({
                "role": "assistant",
                "content": assistant_content
            })

            # Add tool results to history
            if tool_results:
                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue conversation with tool results
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=config.MAX_TOKENS,
                    system=self.get_system_prompt(),
                    messages=self.messages,
                    tools=self.get_tools_schema(),
                    extra_headers=config.CLAUDE_EXTRA_HEADERS
                )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if block.type == "thinking":
                # Log final thinking if any
                self.logger.log_message(
                    sender="manager",
                    message_type="thinking",
                    content=block.thinking
                )
            elif block.type == "text":
                final_text += block.text

        # Log manager's response
        self.logger.log_message(
            sender="manager",
            message_type="text",
            content=final_text
        )

        # Add final response to history
        self.messages.append({
            "role": "assistant",
            "content": final_text
        })

        # Limit conversation history to prevent token overflow
        # Context editing should handle this, but as safety measure
        if len(self.messages) > 30:
            # Keep system context, trim middle
            self.messages = self.messages[:2] + self.messages[-28:]

        return final_text

    async def close(self):
        """Close MCP client connection."""
        await self.mcp_client.close()
