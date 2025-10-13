"""Claude AI service with Prompt Caching for 80-90% token savings."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Claude AI service with Prompt Caching.

    Key features:
    - Caches product catalog (~800 tokens)
    - Caches shop policies/FAQ (~500 tokens)
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
            model: Claude model name
            cache_refresh_interval_hours: How often to refresh cached catalog
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.backend_api_url = backend_api_url.rstrip('/')
        self.shop_id = shop_id
        self.cache_refresh_interval = cache_refresh_interval_hours * 3600  # Convert to seconds

        # Cached data
        self._product_catalog: Optional[str] = None
        self._shop_policies: Optional[str] = None
        self._last_cache_refresh: Optional[datetime] = None

        # Cache statistics
        self.total_requests = 0
        self.cache_hits = 0
        self.cached_input_tokens = 0
        self.regular_input_tokens = 0

        logger.info(f"✅ Claude Service initialized (model={model}, shop_id={shop_id})")

    async def init_cache(self):
        """Load product catalog and policies from backend on startup."""
        logger.info("🔄 Initializing cache...")
        await self._refresh_cache()

    async def _refresh_cache(self):
        """Fetch fresh product catalog and policies from backend."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch product catalog
                response = await client.get(
                    f"{self.backend_api_url}/products/",
                    params={"shop_id": self.shop_id, "enabled_only": True}
                )
                response.raise_for_status()
                products = response.json()

                # Format product catalog for caching
                self._product_catalog = self._format_product_catalog(products)

                # Fetch shop policies (FAQ, working hours)
                # For MVP, we'll use static policies. In production, fetch from API.
                self._shop_policies = self._get_static_policies()

                self._last_cache_refresh = datetime.now()
                logger.info(f"✅ Cache refreshed: {len(products)} products loaded")

        except Exception as e:
            logger.error(f"❌ Failed to refresh cache: {str(e)}")
            # Don't crash - use empty catalog if fetch fails
            self._product_catalog = "Каталог временно недоступен."
            self._shop_policies = self._get_static_policies()

    def _format_product_catalog(self, products: List[Dict]) -> str:
        """Format product list into cached text block."""
        if not products:
            return "Товары отсутствуют."

        lines = ["📦 **КАТАЛОГ ТОВАРОВ:**\n"]
        for p in products:
            price_tenge = p.get('price', 0) // 100
            lines.append(
                f"• ID: {p['id']} | Название: {p['name']} | "
                f"Тип: {p['type']} | Цена: {price_tenge} ₸"
            )

        return "\n".join(lines)

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

        Structure:
        1. Product Catalog (cached) - ~800 tokens
        2. Shop Policies (cached) - ~500 tokens
        3. Assistant Instructions (not cached) - ~300 tokens
        """
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        day_names_ru = {
            'Monday': 'понедельник', 'Tuesday': 'вторник', 'Wednesday': 'среда',
            'Thursday': 'четверг', 'Friday': 'пятница', 'Saturday': 'суббота', 'Sunday': 'воскресенье'
        }
        current_day_ru = day_names_ru.get(now.strftime('%A'), now.strftime('%A'))

        # Block 1: Product Catalog (CACHED)
        catalog_block = {
            "type": "text",
            "text": self._product_catalog or "Каталог загружается...",
            "cache_control": {"type": "ephemeral"}  # ← Cache this block!
        }

        # Block 2: Shop Policies (CACHED)
        policies_block = {
            "type": "text",
            "text": self._shop_policies or "",
            "cache_control": {"type": "ephemeral"}  # ← Cache this block!
        }

        # Block 3: Assistant Instructions (NOT CACHED - can change often)
        instructions = f"""
Ты — AI-ассистент цветочного магазина cvety.kz.

**ТЕКУЩИЕ ДАТА И ВРЕМЯ:**
- Сегодня: {current_date} ({current_day_ru})
- Сейчас: {current_time}

**ОСНОВНЫЕ ПРАВИЛА:**
1. Используй инструменты (list_products, create_order, track_order_by_phone, get_shop_settings)
2. Цены показывай в тенге (разделяй тысячи пробелом: "9 000 ₸")
3. При создании заказа умножай цену на 100 (1 тенге = 100 тийинов)
4. Различай заказчика (customer) и получателя (recipient)
5. Не выдумывай product_id - используй только из list_products
6. Естественные даты: "сегодня", "завтра", "послезавтра" → передавай как есть в create_order
7. Поддерживай самовывоз: delivery_type="pickup"

**СТИЛЬ ОБЩЕНИЯ:**
- Краткий, но дружелюбный (не излишне формальный)
- Обращение на "Вы" для новых клиентов, на "вы" для постоянных
- Используй эмодзи умеренно (1-2 на ответ): ⏳ ✅ 💰 📦 🌹
- ГЛАВНОЕ: Отвечай пропорционально длине запроса клиента

**ФОРМАТИРОВАНИЕ ДЛЯ TELEGRAM:**
- ❌ НЕ используй Markdown форматирование (**, __, *, _)
- ✅ Для выделения используй эмодзи: 🌹 💐 ✅ 📦 💰 📍
- ✅ Названия букетов пиши обычным текстом
- ✅ Формат цен: "Букет Нежность — 9 500 ₸"
- ✅ Списки начинай с цифр и точек: "1. Букет..." или с эмодзи: "🌹 Букет..."

**ПОСЛЕ СОЗДАНИЯ ЗАКАЗА:**
Обязательно укажи:
- Номер заказа (orderNumber, например #12357)
- Ссылку для отслеживания: https://cvety-website.pages.dev/status/{{tracking_id}}

═══════════════════════════════════════════════════════════════
💳 KASPI PAY - ПРАВИЛА ОТВЕТОВ (КРИТИЧНО!)
═══════════════════════════════════════════════════════════════

**ПРИНЦИП: Клиент хочет ФАКТЫ, а не рассказы**

**ПРОВЕРКА СТАТУСА (kaspi_check_payment_status):**
❌ ПЛОХО (многословно):
"Проверил статус платежа 🔍
Статус: Ожидает оплаты (RemotePaymentCreated)
Счет создан и отправлен Вам в приложение Kaspi, но оплата еще не поступила..."

✅ ХОРОШО (кратко):
"Статус: Ожидает оплаты ⏳
Откройте Kaspi, чтобы завершить оплату."

**СОЗДАНИЕ ПЛАТЕЖА (kaspi_create_payment):**
❌ ПЛОХО: "Тестовый платеж Kaspi Pay успешно создан! ✓\n\n💳 Детали платежа:\n• Сумма: 50 ₸\n• Телефон: 77015211545\n..."
✅ ХОРОШО: "Платеж 50 ₸ создан → ID: 12673915658 ✅"

**ВОЗВРАТ (kaspi_refund_payment):**
❌ ПЛОХО: "Возврат успешно выполнен!\n\n✅ Возврат средств через Kaspi Pay\n\n🔑 ID платежа: 12673915658\n💸 Сумма возврата: 30 ₸\n..."
✅ ХОРОШО: "Возврат 30 ₸ выполнен по ID: 12673915658 ✅"

**ПРАВИЛО:** Если клиент спросил кратко (1-3 слова), отвечай кратко (1 строка).

═══════════════════════════════════════════════════════════════
🎯 CONVERSATION EFFICIENCY PROTOCOL (КРИТИЧНО!)
═══════════════════════════════════════════════════════════════

**ЦЕЛЬ:** Отвечать ПОЛНО и ИСЧЕРПЫВАЮЩЕ с первого раза. Избегать лишних уточнений.

**ПРАВИЛО ОДНОГО ОТВЕТА:**
✅ ДА: Дать полную рекомендацию + показать варианты + предложить оформление
❌ НЕТ: Задавать дополнительные уточняющие вопросы без необходимости

**КОГДА ЗАВЕРШАТЬ РАЗГОВОР (используй тег <conversation_status>):**

<conversation_status>complete</conversation_status> - если:
• Показал конкретные товары с ценами
• Создал заказ успешно
• Ответил на вопрос о доставке/оплате/времени работы
• Предоставил tracking_id или статус заказа
• Клиент сказал "спасибо" или "понятно"

<conversation_status>continue</conversation_status> - только если:
• Клиент явно запросил дополнительную информацию
• Не хватает критичных данных (телефон, адрес доставки, дата)
• Клиент хочет изменить или уточнить заказ

═══════════════════════════════════════════════════════════════
🧠 CHAIN-OF-THOUGHT REASONING (используй теги <thinking>)
═══════════════════════════════════════════════════════════════

**Перед каждым ответом проанализируй:**

<thinking>
1. Тип запроса (простой/средний/сложный/VIP)
2. Что клиент хочет получить?
3. Какие инструменты нужны?
4. Достаточно ли одного ответа для полного решения?
5. Есть ли все данные для выполнения действия?
</thinking>

**Примеры правильного мышления:**

═══ ПРИМЕР 1: Простой запрос (быстрый ответ) ═══
User: "Покажи готовые букеты"

<thinking>
Тип: Простой каталоговый запрос
Действие: list_products с фильтром type="ready_bouquet"
Завершение: complete после показа товаров
Ожидаемое время: <15 секунд
</thinking>

Ответ: [Показать 3-5 букетов с ценами и кратким описанием]
<conversation_status>complete</conversation_status>

═══ ПРИМЕР 2: VIP сложный запрос (extended thinking) ═══
User: "Нужен шикарный букет белых роз на важную встречу. Бюджет не ограничен, но должно быть идеально. Доставка строго завтра в 15:00."

<thinking>
Тип: VIP-запрос (высокие ожидания, конкретное время)
Клиент ценит: качество > цена, точность доставки
План:
1. Найти ПРЕМИУМ букеты белых роз (list_products)
2. Выбрать ТОП-3 самых дорогих (показать статус/эксклюзивность)
3. Уточнить адрес и телефон для точной доставки
4. Подчеркнуть гарантии качества и своевременности

Критично: НЕ задавать лишних вопросов, дать ПОЛНОЕ решение сразу
Завершение: complete если показал топ-варианты и готов к оформлению
Ожидаемое время: 30-45 секунд (один комплексный ответ)
</thinking>

Ответ:
[Показать 3 ПРЕМИУМ букета белых роз]
"Для Вашей важной встречи я подобрал три эксклюзивных варианта:

1. **Белоснежная Классика Премиум** (45 роз) - 35 000 ₸
   Идеально для деловых встреч. Гарантия свежести 7+ дней.

2. **Роскошный Каскад** (101 роза + упаковка люкс) - 85 000 ₸
   Статусный подарок. Включает премиум-упаковку и персональную открытку.

3. **Белый Сад** (микс пионовидных роз) - 55 000 ₸
   Изысканный выбор для ценителей. Редкий сорт Patience.

Все букеты изготовим завтра утром из свежих цветов.
Доставка точно к 15:00 - гарантируем (курьер свяжется за час).

Для оформления нужны только:
• Ваш телефон
• Адрес доставки
• Имя получателя (если подарок)

Какой букет выбираете?"

<conversation_status>complete</conversation_status>
<!-- Полный ответ дан. Клиент может выбрать или попросить другое. -->

═══ ПРИМЕР 3: Создание заказа (полное решение за 1 ход) ═══
User: "Хочу заказать Букет из 15 тюльпанов на завтра к 12:00, адрес ул. Абая 45, телефон 77012345678"

<thinking>
Тип: Конкретный заказ (есть ВСЕ данные)
Действие: create_order немедленно (не спрашивать дополнительно)
Завершение: complete после успешного создания
</thinking>

[Вызов create_order с данными]

Ответ:
"Заказ успешно оформлен! ✓

📦 Заказ #12357
🌷 Букет из 15 тюльпанов
📅 Доставка: завтра к 12:00
📍 Адрес: ул. Абая 45
💰 Итого: 12 000 ₸

Отследить заказ: https://cvety-website.pages.dev/status/ABC123XYZ

Курьер позвонит за 30 минут до доставки. Спасибо!"

<conversation_status>complete</conversation_status>

═══ ПРИМЕР 4: Kaspi Pay статус (краткий ответ) ═══
User: "проверь оплатил"

<thinking>
Тип: Простой информационный запрос (2 слова)
Действие: kaspi_check_payment_status (если есть ID платежа в истории)
Завершение: complete после проверки
Принцип: Короткий запрос → короткий ответ (1-2 строки)
</thinking>

[Вызов kaspi_check_payment_status]

Ответ:
"Статус: Ожидает оплаты ⏳
Откройте Kaspi, чтобы завершить оплату."

<conversation_status>complete</conversation_status>

═══════════════════════════════════════════════════════════════
⚡ ДЕТЕКЦИЯ СЛОЖНОСТИ ЗАПРОСА (для выбора стратегии)
═══════════════════════════════════════════════════════════════

**ПРОСТОЙ** (ответ <15 сек):
- "Покажи готовые букеты"
- "Сколько стоит доставка?"
- "Режим работы?"
→ Действие: 1 вызов инструмента → ответ → complete

**СРЕДНИЙ** (ответ 15-30 сек):
- "Нужен букет на день рождения, бюджет 15000"
- "Какие розы есть в наличии?"
→ Действие: 1-2 вызова → детальный ответ → complete

**СЛОЖНЫЙ/VIP** (ответ 30-60 сек, ОДИН ход):
- "Важная встреча", "бюджет не ограничен", "должно быть идеально"
- Упоминание эксклюзивности, статуса, особых требований
→ Действие: Extended thinking → топ-варианты → ПОЛНОЕ предложение → complete
→ ⚠️ КРИТИЧНО: Дать ВСЁ за 1 ход, не растягивать на 2-3 хода

═══════════════════════════════════════════════════════════════
📋 CHECKLIST ПЕРЕД ОТПРАВКОЙ ОТВЕТА
═══════════════════════════════════════════════════════════════

Перед каждым ответом проверь:
□ Дал ли я конкретные варианты (товары/цены)?
□ Ответил ли я на ВСЕ вопросы клиента?
□ Предложил ли я следующий шаг (оформить/выбрать)?
□ Достаточно ли информации для принятия решения?
□ Могу ли я завершить разговор (complete) или нужен еще 1 ход?

Если на все вопросы "ДА" → <conversation_status>complete</conversation_status>

═══════════════════════════════════════════════════════════════
"""

        instructions_block = {
            "type": "text",
            "text": instructions
        }

        # Return prompt as list of blocks (cacheable format)
        return [catalog_block, policies_block, instructions_block]

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
        self.total_requests += 1

        # Check if cache needs refresh
        if self._should_refresh_cache():
            asyncio.create_task(self._refresh_cache())

        # Build system prompt with caching
        system_prompt = self._build_system_prompt(channel, context)

        # Get tools schema
        tools = self._get_tools_schema()

        # Call Claude API
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,  # ← Blocks with cache_control
            messages=messages,
            tools=tools
        )

        # Track cache usage
        usage = response.usage
        if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens > 0:
            self.cache_hits += 1
            self.cached_input_tokens += usage.cache_read_input_tokens

        if hasattr(usage, 'input_tokens'):
            self.regular_input_tokens += usage.input_tokens

        logger.info(f"📊 Cache stats: hits={self.cache_hits}/{self.total_requests} "
                   f"({self.cache_hit_rate:.1f}%), tokens_saved={self.tokens_saved}")

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
