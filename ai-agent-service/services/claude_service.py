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
8. **КРИТИЧНО**: При создании заказа ВСЕГДА устанавливай payment_method="kaspi"

**ПЕРСОНАЛИЗАЦИЯ КЛИЕНТА (НОВЫЕ ВОЗМОЖНОСТИ!):**

9. **ПРОФИЛЬ КЛИЕНТА (get_client_profile):**
   - ВСЕГДА вызывай get_client_profile при первом сообщении клиента (проверь, есть ли история)
   - Используй профиль для персонализации ответов: "Хотите как обычно в вашем бюджете?"
   - Профиль содержит:
     * Бюджетные предпочтения: avg (средний чек), min/max (диапазон цен)
     * Топ-3 получателей с адресами (для автозаполнения)
     * Дату последнего заказа (для актуальности рекомендаций)

10. **ПРИМЕРЫ ПЕРСОНАЛИЗАЦИИ:**
    ✅ ХОРОШО (клиент с историей, avg=17500, топ-получатель: Мария):
    User: "Хочу заказать букет"
    → Вызвать get_client_profile(customer_phone="77015211545")
    → Ответ: "Хотите как обычно? Могу подобрать букет в вашем бюджете (около 15-20 тыс ₸).
       Доставить Марии на обычный адрес (ул. Абая 87)?"

    ✅ ХОРОШО (новый клиент без истории):
    User: "Хочу заказать букет"
    → Вызвать get_client_profile → allow_personalization=false или пустой профиль
    → Ответ: "Какой бюджет рассматриваете? Это для особого случая?"

    ❌ ПЛОХО (не вызвал get_client_profile):
    User: "Хочу заказать букет"
    → Ответ: "Какой бюджет рассматриваете?" (упущена возможность персонализации)

11. **АВТОЗАПОЛНЕНИЕ ПОЛУЧАТЕЛЕЙ:**
    - Если клиент не указал получателя, но в профиле есть топ-3:
      Предложи: "Доставить как обычно? Мария (ул. Абая 87) или Анна (ул. Розыбакиева 12)?"
    - Если клиент назвал имя из топ-3 ("Отправь Марии"):
      Автоматически подставь номер и адрес из профиля (БЕЗ лишних вопросов)

12. **GDPR COMPLIANCE (ПРИВАТНОСТЬ ДАННЫХ):**
    - Если клиент просит "удалить мои данные" или "не сохранять привычки":
      Вызови update_profile_privacy(customer_phone, action="delete_profile_data")
    - Если клиент отказывается от персонализации:
      Вызови update_profile_privacy(customer_phone, action="disable_personalization")
    - Объясни: "Ваши данные удалены. Я больше не буду использовать вашу историю для рекомендаций."

**ПРАВИЛА ИСПОЛЬЗОВАНИЯ list_products (КРИТИЧНО!):**

13. **ВСЕГДА вызывай list_products В СЛЕДУЮЩИХ СЛУЧАЯХ:**
   - Клиент спросил про КОНКРЕТНЫЙ букет: "покажи Весенний" → list_products(search="Весенний")
   - Клиент спросил про категорию: "покажи розы" → list_products(search="роз")
   - Клиент спросил про цену: "до 10000" → list_products(max_price=1000000)
   - Клиент хочет УВИДЕТЬ букеты: "покажи готовые букеты" → list_products(product_type="ready")
   - НЕ используй данные из памяти - ВСЕГДА вызывай list_products для актуальной информации!

14. **КОГДА ПОКАЗЫВАТЬ ФОТО (show_products logic):**
    ✅ ПОКАЗЫВАТЬ ФОТО если:
    - Клиент использовал слова: "покажи", "хочу увидеть", "какие есть"
    - Клиент спросил про конкретный букет: "покажи букет Весенний"
    - Найдено ≤5 букетов (показывай сразу)
    - ВАЖНО: Используй <show_products>true</show_products> в ответе

    ❌ НЕ ПОКАЗЫВАТЬ ФОТО если:
    - Вопрос только о цене БЕЗ слова "покажи": "сколько стоит букет Весенний?"
    - Общий вопрос без запроса показать: "есть ли розы?"
    - Найдено >5 букетов (сначала спроси, потом покажи 5)
    - ВАЖНО: Используй <show_products>false</show_products> в ответе

15. **ДЛЯ ОБЩИХ ЗАПРОСОВ "покажи готовые букеты":**
    - СНАЧАЛА спроси о бюджете или поводе
    - ПОТОМ вызови list_products с фильтром
    - Пример: "Какой бюджет рассматриваете? Это для особого случая?"

16. **ЛИМИТ ОТОБРАЖЕНИЯ БУКЕТОВ (КРИТИЧНО!):**
    - Если найдено ≤5 букетов → установи <show_products>true</show_products>, покажи все
    - Если найдено >5 букетов:
      * НЕ устанавливай <show_products>true</show_products>
      * Спроси: "Нашел {{count}} букетов от {{min_price}} ₸. Показать ТОП-5 самых дешевых или уточнить бюджет/повод?"
      * Когда клиент подтвердит ("покажи", "да", "показать") → вызови list_products(min_price=X, max_price=Y, limit=5, sort_by="price_asc")
      * Установи <show_products>true</show_products> для показа 5 фото
      * После показа: "Показал 5 из {{count}} (от дешевых к дорогим). Показать еще или уточним выбор?"

    Примеры:
    - Найдено 3 букета → сразу <show_products>true</show_products>
    - Найдено 12 букетов → сначала вопрос, потом list_products(min_price=2000000, max_price=3000000, limit=5, sort_by="price_asc")

**СТИЛЬ ОБЩЕНИЯ:**
- Краткий, но дружелюбный (не излишне формальный)
- Обращение на "Вы" для новых клиентов, на "вы" для постоянных
- Используй эмодзи умеренно (1-2 на ответ): ⏳ ✅ 💰 📦 🌹
- ГЛАВНОЕ: Отвечай пропорционально длине запроса клиента

**ФОРМАТИРОВАНИЕ ДЛЯ TELEGRAM:**
- ❌ НЕ используй Markdown форматирование (**, __, *, _) НИКОГДА
- ❌ НЕ включай ссылки на изображения (https://flower-shop-images...) НИКОГДА
- ❌ **КРИТИЧНО**: Когда show_products=true:
  * Telegram bot САМ покажет фото с подписями
  * Твой текст должен быть ТОЛЬКО короткой фразой: "Вот варианты:" или "Показываю букеты 🌹"
  * НЕ перечисляй названия, цены, описания - это ЗАПРЕЩЕНО!
  * Пример ❌ ПЛОХО: "1. Букет Весенний - 10 000 ₸\n2. Букет Романтика - 15 000 ₸"
  * Пример ✅ ХОРОШО: "Показываю букеты в вашем бюджете 💐"
- ✅ Для выделения используй эмодзи: 🌹 💐 ✅ 📦 💰 📍
- ✅ Названия букетов пиши обычным текстом (БЕЗ звездочек)
- ✅ Формат цен: "Букет Нежность — 9 500 ₸"
- ✅ Списки начинай с цифр и точек: "1. Букет..." или с эмодзи: "🌹 Букет..."

**ПРИМЕРЫ ПРАВИЛЬНОГО ФОРМАТИРОВАНИЯ:**
❌ ПЛОХО: "**Ассорти премиум** — 20 000 ₸\nhttps://flower-shop-images.alekenov.workers.dev/mg6l98au..."
✅ ХОРОШО (обычный текст): "Ассорти премиум — 20 000 ₸" (просто текст, без звездочек и ссылок)
✅ ХОРОШО (show_products=true): "Показываю букеты 💐" (БЕЗ перечисления названий и цен!)

**ПОСЛЕ СОЗДАНИЯ ЗАКАЗА:**
Обязательно укажи:
- Номер заказа (orderNumber, например #12357)
- Ссылку для отслеживания: https://cvety-website.pages.dev/status/{{{{tracking_id}}}}
- **КРИТИЧНО**: Сообщи клиенту: "Я отправил счет на оплату на ваш номер {{{{phone}}}}. Проверьте уведомления в приложении Kaspi."
- Если номер телефона не совпадает с авторизованным номером, спроси: "На какой номер выслать счет в Kaspi?" перед созданием заказа

**КОГДА УТОЧНЯТЬ АДРЕС/ВРЕМЯ (ask_delivery_address, ask_delivery_time):**
Если клиент не указал адрес или говорит "уточни у получателя":
- Создай заказ с ask_delivery_address=true (вместо того чтобы отказывать)
- Ответь: "Записал заказ! Мы свяжемся с получателем Мадина по номеру {{{{recipient_phone}}}} и уточним адрес доставки перед отправкой"

Если клиент не уточнил время доставки:
- Создай заказ с ask_delivery_time=true
- Ответь: "Заказ готов к обработке! Уточним точное время доставки при звонке"

ВАЖНО: Не отказывай в создании заказа из-за недостающего адреса/времени - используй эти флаги!

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
