"""Claude AI service with Prompt Caching for 80-90% token savings."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from anthropic import AsyncAnthropic
import anthropic

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Claude AI service with Prompt Caching.

    Key features:
    - Caches shop policies/FAQ (~500 tokens)
    - Caches assistant instructions (~2000 tokens)
    - NO product catalog (forces AI to call list_products tool for filtering)
    - Auto-refresh every hour
    - Tracks cache hit rate for monitoring
    """

    def __init__(
        self,
        api_key: str,
        backend_api_url: str,
        shop_id: int,
        model: str = "claude-sonnet-4-5-20250929",
        cache_refresh_interval_hours: int = 1
    ):
        """
        Initialize Claude service.

        Args:
            api_key: Anthropic API key
            backend_api_url: Backend API URL for fetching product catalog
            shop_id: Shop ID for multi-tenancy
            model: Claude model name (e.g., "claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929")
            cache_refresh_interval_hours: How often to refresh cached catalog
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.backend_api_url = backend_api_url.rstrip('/')
        self.shop_id = shop_id
        self.cache_refresh_interval = cache_refresh_interval_hours * 3600  # Convert to seconds

        # Cached data (NO product catalog - forces AI to use list_products tool)
        self._shop_policies: Optional[str] = None
        self._last_cache_refresh: Optional[datetime] = None

        # Cache statistics
        self.total_requests = 0
        self.cache_hits = 0
        self.cached_input_tokens = 0
        self.regular_input_tokens = 0

        # Determine model capabilities
        self._is_haiku = "haiku" in model.lower()
        self._is_sonnet = "sonnet" in model.lower()

        logger.info(f"✅ Claude Service initialized (model={model}, shop_id={shop_id})")
        if self._is_haiku:
            logger.info("💡 Using Claude Haiku 4.5 - optimized for speed and cost efficiency")

    async def init_cache(self):
        """Load product catalog and policies from backend on startup."""
        logger.info("🔄 Initializing cache...")
        await self._refresh_cache()

    async def _refresh_cache(self):
        """Fetch shop policies (NO product catalog - force AI to use list_products)."""
        try:
            # Fetch shop policies (FAQ, working hours)
            # For MVP, we'll use static policies. In production, fetch from API.
            self._shop_policies = self._get_static_policies()

            self._last_cache_refresh = datetime.now()
            logger.info(f"✅ Cache refreshed: policies loaded (NO product catalog - use list_products tool)")

        except Exception as e:
            logger.error(f"❌ Failed to refresh cache: {str(e)}")
            # Don't crash - use empty policies if fetch fails
            self._shop_policies = self._get_static_policies()

    def _get_static_policies(self) -> str:
        """Get static shop policies (FAQ, working hours, etc)."""
        return """
🏪 **ИНФОРМАЦИЯ О МАГАЗИНЕ:**

**Режим работы:**
• Понедельник-Воскресенье: 09:00 - 21:00
• Без выходных

**Доставка:**
• Доставка по Алматы: 2000 ₸
• Доставка за город: по договорённости
• Самовывоз: бесплатно (адрес: Алматы, ул. Абая 150)

**Оплата:**
• Наличными курьеру
• Kaspi Pay
• Банковский перевод

**FAQ:**
Q: Можно ли изменить заказ после оформления?
A: Да, используйте команду update_order с tracking_id

Q: Как отследить заказ?
A: Используйте ссылку https://cvety-website.pages.dev/status/{tracking_id}

Q: Какие цветы свежие?
A: Все букеты изготавливаются в день доставки из свежих цветов
"""

    def _build_system_prompt(self, channel: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Build system prompt with cached blocks.

        Structure (NO product catalog - forces AI to use list_products tool):
        1. Shop Policies (cached) - ~500 tokens
        2. Assistant Instructions (cached) - ~2000 tokens
        """
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        day_names_ru = {
            'Monday': 'понедельник', 'Tuesday': 'вторник', 'Wednesday': 'среда',
            'Thursday': 'четверг', 'Friday': 'пятница', 'Saturday': 'суббота', 'Sunday': 'воскресенье'
        }
        current_day_ru = day_names_ru.get(now.strftime('%A'), now.strftime('%A'))

        # Block 1: Shop Policies (CACHED)
        policies_block = {
            "type": "text",
            "text": self._shop_policies or "",
            "cache_control": {"type": "ephemeral"}  # ← Cache this block!
        }

        # Block 3: Assistant Instructions (NOT CACHED - can change often)
        # Following Anthropic Best Practices: XML-structured prompt for clarity and maintainability
        instructions = f"""
<role>
Ты — AI-ассистент цветочного магазина cvety.kz.
</role>

<context>
**ТЕКУЩИЕ ДАТА И ВРЕМЯ:**
- Сегодня: {current_date} ({current_day_ru})
- Сейчас: {current_time}
</context>

<core_rules>
**ОСНОВНЫЕ ПРАВИЛА:**
1. Используй инструменты (list_products, create_order, track_order_by_phone, get_shop_settings)
2. Цены показывай в тенге (разделяй тысячи пробелом: "9 000 ₸")
3. При создании заказа умножай цену на 100 (1 тенге = 100 тийинов)
4. Различай заказчика (customer) и получателя (recipient)
5. Не выдумывай product_id - используй только из list_products
6. Естественные даты: "сегодня", "завтра", "послезавтра" → передавай как есть в create_order
7. Поддерживай самовывоз: delivery_type="pickup"
8. **КРИТИЧНО**: При создании заказа ВСЕГДА устанавливай payment_method="kaspi"
</core_rules>

<personalization>
**ПЕРСОНАЛИЗАЦИЯ КЛИЕНТА:**

9. **ПРОФИЛЬ КЛИЕНТА (get_client_profile):**
   - ВСЕГДА вызывай get_client_profile при первом сообщении клиента (проверь, есть ли история)
   - Используй профиль для персонализации: "Хотите как обычно в вашем бюджете?"
   - Профиль содержит: avg/min/max чек, топ-3 получателей с адресами, дату последнего заказа

10. **АВТОЗАПОЛНЕНИЕ ПОЛУЧАТЕЛЕЙ:**
    - Если клиент не указал получателя, но в профиле есть топ-3:
      Предложи: "Доставить как обычно? Мария (ул. Абая 87) или Анна (ул. Розыбакиева 12)?"
    - Если клиент назвал имя из топ-3: подставь номер и адрес БЕЗ лишних вопросов

11. **GDPR (ПРИВАТНОСТЬ ДАННЫХ):**
    - "удалить мои данные" → update_profile_privacy(action="delete_profile_data")
    - "не сохранять привычки" → update_profile_privacy(action="disable_personalization")
</personalization>

<product_catalog_rules>
**ИСПОЛЬЗОВАНИЕ list_products (КРИТИЧНО!):**

12. **ВСЕГДА вызывай list_products В СЛУЧАЯХ:**
   - Конкретный букет: "покажи Весенний" → list_products(search="Весенний")
   - Категория: "покажи розы" → list_products(search="роз")
   - Цена: "до 10000" → list_products(max_price=1000000)
   - НЕ используй данные из памяти - ВСЕГДА вызывай list_products!

13. **КОГДА ПОКАЗЫВАТЬ ФОТО (show_products):**
    ✅ Используй <show_products>true</show_products> если:
    - Слова: "покажи", "хочу увидеть", "какие есть"
    - Найдено ≤5 букетов

    ❌ Используй <show_products>false</show_products> если:
    - Вопрос только о цене БЕЗ "покажи"
    - Найдено >5 букетов (сначала спроси)

14. **ЛИМИТ БУКЕТОВ:**
    - ≤5 букетов → <show_products>true</show_products>, покажи все
    - >5 букетов → спроси о бюджете, затем list_products(limit=5)
</product_catalog_rules>

<communication_style>
**СТИЛЬ ОБЩЕНИЯ:**
- Краткий, дружелюбный (не формальный)
- Эмодзи умеренно (1-2): ⏳ ✅ 💰 📦 🌹
- Отвечай пропорционально длине запроса
</communication_style>

<telegram_formatting>
**ФОРМАТИРОВАНИЕ ДЛЯ TELEGRAM:**
- ❌ НЕ используй Markdown (**, __, *, _) НИКОГДА
- ❌ НЕ включай ссылки на изображения НИКОГДА
- ❌ Когда show_products=true: ТОЛЬКО короткая фраза ("Показываю букеты 💐"), НЕ перечисляй названия/цены!
- ✅ Используй эмодзи для выделения: 🌹 💐 ✅ 📦
- ✅ Формат цен: "Букет Нежность — 9 500 ₸"
</telegram_formatting>

<order_creation>
**ПОСЛЕ СОЗДАНИЯ ЗАКАЗА:**
- Номер заказа (orderNumber)
- Ссылка: https://cvety-website.pages.dev/status/{{{{tracking_id}}}}
- **КРИТИЧНО**: "Я отправил счет на оплату на ваш номер {{{{phone}}}}. Проверьте Kaspi."

**УТОЧНЕНИЕ АДРЕСА/ВРЕМЕНИ:**
- Адрес неизвестен → ask_delivery_address=true
- Время неизвестно → ask_delivery_time=true
- НЕ отказывай в заказе - используй флаги!
</order_creation>

<kaspi_pay_protocol>
**KASPI PAY - ПРАВИЛА (КРИТИЧНО!):**
**ПРИНЦИП: Клиент хочет ФАКТЫ, а не рассказы**

- kaspi_check_payment_status → "Статус: Ожидает оплаты ⏳"
- kaspi_create_payment → "Платеж 50 ₸ создан → ID: 12673915658 ✅"
- kaspi_refund_payment → "Возврат 30 ₸ выполнен ✅"
- **ПРАВИЛО:** Короткий запрос → короткий ответ (1 строка)
</kaspi_pay_protocol>

<conversation_efficiency>
**CONVERSATION EFFICIENCY (КРИТИЧНО!):**

**ЦЕЛЬ:** Отвечать ПОЛНО с первого раза. Избегать лишних уточнений.

**ЗАВЕРШЕНИЕ (<conversation_status>):**
- complete: Показал товары/создал заказ/ответил на вопрос/клиент сказал "спасибо"
- continue: Нужны критичные данные/клиент запросил дополнительно
</conversation_efficiency>

<reasoning_framework>
**CHAIN-OF-THOUGHT REASONING (<thinking>):**

Перед ответом анализируй в тегах <thinking>:
1. Тип запроса (простой/средний/сложный/VIP)
2. Что клиент хочет?
3. Какие инструменты?
4. Достаточно ли одного ответа?
5. Есть ли все данные?

**ТИПЫ ЗАПРОСОВ:**
- ПРОСТОЙ (<15 сек): "Покажи букеты" → 1 вызов → complete
- СРЕДНИЙ (15-30 сек): "Букет на ДР, бюджет 15000" → 1-2 вызова → complete
- VIP (30-60 сек): "Бюджет не ограничен, идеально" → Extended thinking → ВСЁ за 1 ход → complete
</reasoning_framework>

<quality_checklist>
**CHECKLIST ПЕРЕД ОТВЕТОМ:**
□ Дал конкретные варианты (товары/цены)?
□ Ответил на ВСЕ вопросы?
□ Предложил следующий шаг?
□ Достаточно ли информации?
□ Могу завершить (complete)?
</quality_checklist>

<visual_search_protocol>
**VISUAL SEARCH (MANDATORY!):**

Паттерн "[User sent an image: https://...]" → **ОБЯЗАН**:
1. **НЕМЕДЛЕННО** search_similar_bouquets(image_url=...)
2. **ДОЖДАТЬСЯ** результатов
3. **ТОЛЬКО ПОСЛЕ** — форматировать ответ

❌ НЕ МОЖЕШЬ:
- Отвечать "не могу обработать" БЕЗ вызова search_similar_bouquets
- Писать текст ДО получения результатов

**ВРЕМЯ ПОИСКА:** 5-10 секунд
**API УПАЛ:** "Поиск недоступен, попробуй позже"
</visual_search_protocol>
"""

        instructions_block = {
            "type": "text",
            "text": instructions,
            "cache_control": {"type": "ephemeral"}  # Cache instructions too
        }

        # Return prompt as list of blocks (cacheable format)
        return [policies_block, instructions_block]

    def _validate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean message history to prevent tool_use_id errors.

        Rules:
        - Each tool_result must have corresponding tool_use in previous assistant message
        - Remove ONLY orphaned tool_result blocks (selective cleanup)
        - Preserve valid tool_use/tool_result pairs to maintain conversation context
        - This prevents infinite loop bug where AI forgets previous tool calls
        """
        if not messages:
            return messages

        # Collect all tool_use IDs from assistant messages
        valid_tool_use_ids = set()
        has_any_orphaned = False

        for msg in messages:
            if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if block.get("type") == "tool_use":
                        valid_tool_use_ids.add(block.get("id"))
            elif msg.get("role") == "user" and isinstance(msg.get("content"), list):
                # Check for orphaned tool_results
                for block in msg["content"]:
                    if block.get("type") == "tool_result":
                        tool_use_id = block.get("tool_use_id")
                        if tool_use_id not in valid_tool_use_ids:
                            has_any_orphaned = True
                            logger.warning(f"🔍 Found orphaned tool_result for ID: {tool_use_id}")
                            break

        # If we found orphaned blocks, do SELECTIVE cleanup (only remove orphans, keep valid pairs)
        # This prevents infinite loop bug where AI loses context about previous tool calls
        if has_any_orphaned:
            logger.warning("⚠️ SELECTIVE CLEANUP: Removing only orphaned tool_result blocks (keeping valid tool_use/tool_result pairs)")
            # No cleanup here - fall through to selective cleanup below

        # Otherwise, do selective cleanup of orphaned tool_results only
        cleaned_messages = []
        for msg in messages:
            if msg.get("role") == "user" and isinstance(msg.get("content"), list):
                cleaned_content = []
                for block in msg["content"]:
                    if block.get("type") == "tool_result":
                        tool_use_id = block.get("tool_use_id")
                        if tool_use_id in valid_tool_use_ids:
                            cleaned_content.append(block)
                    else:
                        cleaned_content.append(block)

                if cleaned_content:
                    cleaned_messages.append({**msg, "content": cleaned_content})
            else:
                cleaned_messages.append(msg)

        # Final cleanup: Remove empty text blocks from all messages
        final_cleaned = []
        for msg in cleaned_messages:
            if isinstance(msg.get("content"), list):
                # Filter out empty text blocks
                non_empty_content = []
                for block in msg["content"]:
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        if text and text.strip():  # Only keep non-empty text
                            non_empty_content.append(block)
                    else:
                        # Keep all non-text blocks (tool_use, tool_result)
                        non_empty_content.append(block)

                if non_empty_content:
                    final_cleaned.append({**msg, "content": non_empty_content})
                else:
                    logger.warning(f"⚠️ Removed message with only empty text blocks, role={msg.get('role')}")
            elif isinstance(msg.get("content"), str):
                # String content - check if empty
                if msg.get("content") and msg.get("content").strip():
                    final_cleaned.append(msg)
                else:
                    logger.warning(f"⚠️ Removed message with empty string content, role={msg.get('role')}")
            else:
                # Keep other content types
                final_cleaned.append(msg)

        return final_cleaned

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        channel: str = "telegram",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process chat message with Claude AI.

        Args:
            messages: Conversation history (list of {role, content})
            channel: Channel name (telegram, whatsapp, etc)
            context: Optional user context

        Returns:
            Dict with response text and metadata
        """
        import time
        start_time = time.time()  # Track response latency
        self.total_requests += 1

        # Check if cache needs refresh
        if self._should_refresh_cache():
            asyncio.create_task(self._refresh_cache())

        # Build system prompt with caching
        system_prompt = self._build_system_prompt(channel, context)

        # Get tools schema
        tools = self._get_tools_schema()

        # Validate and clean message history before sending to API
        messages = self._validate_messages(messages)

        # Call Claude API with auto-recovery for corrupted conversation history
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,  # ← Blocks with cache_control
                messages=messages,
                tools=tools
            )
        except anthropic.BadRequestError as e:
            # Auto-recover from corrupted conversation history
            # This happens when:
            # 1. tool_use_id in tool_result has no corresponding tool_use
            # 2. Empty text content blocks in message history
            # (e.g., service restarted mid-execution, history saved incorrectly)
            error_message = str(e)
            if ("unexpected `tool_use_id`" in error_message or
                "tool_result" in error_message or
                "text content blocks must be non-empty" in error_message or
                "must be non-empty" in error_message):
                logger.warning(
                    f"🔧 Detected corrupted conversation history: {error_message[:100]}... "
                    f"Auto-recovering by clearing history and keeping only last user message"
                )

                # Keep only the last user message (discard corrupted tool_use/tool_result pairs)
                last_user_message = None
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        # Extract only plain text content, discard tool_result blocks
                        if isinstance(msg.get("content"), list):
                            for block in msg["content"]:
                                if block.get("type") == "text":
                                    last_user_message = msg
                                    break
                        elif isinstance(msg.get("content"), str):
                            last_user_message = msg
                            break

                if last_user_message:
                    messages = [last_user_message]
                    logger.info(f"✅ Recovered conversation with fresh history (1 message)")

                    # Retry API call with cleaned history
                    response = await self.client.messages.create(
                        model=self.model,
                        max_tokens=2048,
                        system=system_prompt,
                        messages=messages,
                        tools=tools
                    )
                else:
                    logger.error("❌ Auto-recovery failed: no user message found in history")
                    raise
            else:
                # Different error, re-raise
                raise

        # Track cache usage
        usage = response.usage
        if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens > 0:
            self.cache_hits += 1
            self.cached_input_tokens += usage.cache_read_input_tokens

        if hasattr(usage, 'input_tokens'):
            self.regular_input_tokens += usage.input_tokens

        # Track response latency for logging
        elapsed_time = time.time() - start_time

        logger.info(f"📊 Cache stats: hits={self.cache_hits}/{self.total_requests} "
                   f"({self.cache_hit_rate:.1f}%), tokens_saved={self.tokens_saved}, latency={elapsed_time:.2f}s")

        return response

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed."""
        if not self._last_cache_refresh:
            return True

        elapsed = (datetime.now() - self._last_cache_refresh).total_seconds()
        return elapsed >= self.cache_refresh_interval

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100

    @property
    def tokens_saved(self) -> int:
        """Calculate tokens saved by caching."""
        # Cached tokens cost 10% of regular, so we save 90%
        return int(self.cached_input_tokens * 0.9)

    @property
    def cost_savings_usd(self) -> float:
        """Estimate cost savings in USD."""
        # Claude Sonnet 4.5: $3 per 1M input tokens
        # Cached: $0.30 per 1M (90% savings)
        saved_tokens = self.tokens_saved
        return (saved_tokens / 1_000_000) * 3.0 * 0.9

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get MCP tools schema for function calling."""
        # Import tools schema (we'll create this file next)
        from prompts.tools_schema import get_tools_schema
        return get_tools_schema()

    async def close(self):
        """Close Claude client."""
        await self.client.close()
