# 🚀 AI Agent v2 - План Улучшений

**Дата создания**: 2025-10-09
**Основано на**: Benchmark v1 vs v2 (40 сценариев)
**Цель**: Довести v2 до production-ready состояния

---

## 🔴 КРИТИЧНЫЕ ЗАДАЧИ (Must Fix Before Production)

### 1. Исправить сценарий 04 (VIP клиенты) - Таймаут 179s

**Проблема**:
- v2 делает 2 хода вместо 1, превышая timeout 150s
- VIP клиенты критичны для бизнеса - 0% tolerance для провалов

**Решение**:
```python
# В AI Agent Service V2 добавить логику:
def should_complete_conversation(message, response, context):
    """Определяет, нужно ли завершить диалог после ответа"""

    # Если это первый ответ и он содержит полную информацию
    if context.turn_count == 1:
        if has_product_recommendations(response):
            if has_delivery_confirmation(response):
                if has_order_details(response):
                    return True  # Завершить диалог

    # VIP клиенты: агрессивное завершение после первого полного ответа
    if is_vip_customer(context.user_id):
        if response_is_complete(response):
            return True

    return False
```

**Приоритет**: 🔴 **CRITICAL**
**ETA**: 1-2 дня
**Owner**: Backend team
**Testing**: Unit тесты + повторный бенчмарк на сценарии 04

---

### 2. Настроить агрессивное завершение диалога

**Проблема**:
- v2 слишком "разговорчив", пытается продолжить диалог
- Это увеличивает response time и cost

**Решение**:
```python
# Добавить настройки в config:
CONVERSATION_COMPLETION_CONFIG = {
    "max_turns_before_force_complete": 3,
    "force_complete_after_order_created": True,
    "force_complete_after_tracking_provided": True,
    "force_complete_if_no_followup_question": True,
}

# Обновить логику в chat endpoint:
if should_force_complete(conversation):
    response["conversation_complete"] = True
    response["next_action"] = None
```

**Приоритет**: 🔴 **CRITICAL**
**ETA**: 1 день
**Owner**: AI team
**Метрика успеха**: Avg turns должен упасть с 1.2 до ~1.0

---

### 3. Добавить специальные unit тесты для edge cases

**Проблема**:
- Сценарий 04 не был покрыт отдельным unit тестом
- Нужны тесты для всех timeout-чувствительных сценариев

**Решение**:
```python
# tests/test_vip_scenarios.py
def test_vip_customer_timeout_compliance():
    """VIP клиенты должны получать ответ за < 150s"""
    response = agent.chat(
        message="Нужен шикарный букет...",
        user_type="vip",
        timeout=150
    )
    assert response.total_time < 150
    assert response.turns <= 1  # Не более 1 хода

def test_complex_order_single_turn():
    """Сложные заказы должны обрабатываться за 1 ход"""
    response = agent.chat(
        message="Заказ с множеством деталей...",
        timeout=100
    )
    assert response.turns == 1
    assert response.order_created == True
```

**Приоритет**: 🔴 **CRITICAL**
**ETA**: 1 день
**Owner**: QA team
**Coverage target**: 100% для timeout-sensitive scenarios

---

## 🟠 ВЫСОКИЙ ПРИОРИТЕТ (Performance Improvements)

### 4. Оптимизировать простые запросы (< 10s target)

**Проблема**:
- Простые запросы (адреса, профиль, статус) занимают 12-16s
- v1 делает это за 4-6s
- Пользователи ожидают мгновенного ответа на простые вопросы

**Решение**:
```python
# Добавить fast path для trivial requests:
def classify_request_complexity(message):
    """Классифицирует сложность запроса"""

    simple_patterns = [
        r"мой профиль",
        r"мой адрес",
        r"статус заказа",
        r"рабочие часы",
        r"контакты",
    ]

    if any(re.search(pattern, message.lower()) for pattern in simple_patterns):
        return "simple"

    return "complex"

# В chat endpoint:
if classify_request_complexity(message) == "simple":
    # Используем упрощенный промпт без лишних инструкций
    response = agent.quick_response(message)
else:
    # Полный AI pipeline
    response = agent.full_response(message)
```

**Приоритет**: 🟠 **HIGH**
**ETA**: 2-3 дня
**Owner**: Backend team
**Метрика успеха**: Simple queries < 10s (сейчас 12-16s)

---

### 5. Реализовать мониторинг token usage и cost

**Проблема**:
- Нет visibility на token usage и cost в production
- Невозможно оптимизировать без метрик

**Решение**:
```python
# В AI Agent Service V2:
class TokenUsageTracker:
    def track_request(self, request_id, usage_data):
        """Отслеживает использование токенов"""
        self.db.insert({
            "request_id": request_id,
            "timestamp": datetime.now(),
            "input_tokens": usage_data.input_tokens,
            "output_tokens": usage_data.output_tokens,
            "cache_read_tokens": usage_data.cache_read_tokens,
            "cache_creation_tokens": usage_data.cache_creation_tokens,
            "estimated_cost_usd": self.calculate_cost(usage_data),
            "user_id": request_id.user_id,
            "scenario_type": classify_scenario(request_id.message),
        })

# Добавить в /chat response:
response = {
    "text": "...",
    "usage": {
        "input_tokens": 1234,
        "output_tokens": 567,
        "cache_hit_rate": 0.98,
        "estimated_cost": 0.0042,
    }
}
```

**Приоритет**: 🟠 **HIGH**
**ETA**: 2 дня
**Owner**: DevOps team
**Dashboard**: Grafana with real-time cost metrics

---

### 6. Добавить метрики производительности в response

**Проблема**:
- Нет метрик в response для debugging
- Сложно понять, почему запрос был медленным

**Решение**:
```python
# В /chat response добавить:
response = {
    "text": "...",
    "tracking_id": "...",
    "performance": {
        "total_time_ms": 12345,
        "mcp_tool_calls": 3,
        "tools_used": ["list_products", "create_order", "track_order"],
        "cache_hit_rate": 0.98,
        "turns_count": 1,
        "model": "claude-sonnet-4-5",
    },
    "debug": {
        "conversation_complete": True,
        "next_action": None,
        "thought_process": "...",  # Optional for debugging
    }
}
```

**Приоритет**: 🟠 **HIGH**
**ETA**: 1 день
**Owner**: Backend team
**Benefit**: Easier debugging and optimization

---

## 🟡 СРЕДНИЙ ПРИОРИТЕТ (Production Readiness)

### 7. Реализовать A/B testing router в Telegram bot

**Проблема**:
- Нужен плавный переход с v1 на v2
- Требуется A/B testing для валидации

**Решение**:
```python
# В telegram-bot/bot.py:
class AgentRouter:
    def __init__(self):
        self.ab_test_percentage = float(os.getenv("V2_AB_TEST_PCT", "0"))
        self.vip_users_on_v1 = True  # Временно, пока не исправим сценарий 04

    def select_agent_version(self, user_id, message):
        """Выбирает версию агента для запроса"""

        # VIP клиенты всегда на v1 (временно)
        if self.is_vip_user(user_id) and self.vip_users_on_v1:
            return "v1"

        # A/B test: случайное распределение
        if random.random() * 100 < self.ab_test_percentage:
            return "v2"

        return "v1"  # Fallback

    def get_agent_url(self, version):
        if version == "v2":
            return "http://localhost:8002"
        return "http://localhost:8000"

# Usage:
router = AgentRouter()
agent_version = router.select_agent_version(user_id, message)
agent_url = router.get_agent_url(agent_version)
response = requests.post(f"{agent_url}/chat", json={...})
```

**Приоритет**: 🟡 **MEDIUM**
**ETA**: 1 день
**Owner**: Telegram bot team
**Feature flag**: `V2_AB_TEST_PCT` env variable (0-100)

---

### 8. Настроить timeout handling

**Проблема**:
- Текущий timeout 150s может быть недостаточен для сложных сценариев
- Но слишком большой timeout = плохой UX

**Решение**:
```python
# Динамический timeout на основе сложности:
def calculate_timeout(message, user_type):
    """Вычисляет оптимальный timeout для запроса"""

    base_timeout = 100  # 100s для обычных запросов

    # VIP клиенты: больше времени
    if user_type == "vip":
        base_timeout = 150

    # Сложные multi-step операции
    if is_order_creation(message):
        base_timeout += 50

    # Простые запросы: меньше времени
    if is_simple_query(message):
        base_timeout = 30

    return base_timeout

# В chat endpoint:
timeout = calculate_timeout(message, user.type)
response = await agent.chat(message, timeout=timeout)
```

**Приоритет**: 🟡 **MEDIUM**
**ETA**: 1 день
**Owner**: Backend team
**Метрика**: 0% timeout errors в production

---

### 9. Создать real-time performance dashboard

**Проблема**:
- Нет visibility на production performance
- Невозможно быстро реагировать на проблемы

**Решение**:
```yaml
# Grafana dashboard с метриками:
- Response time (p50, p95, p99)
- Success rate (% успешных запросов)
- Token usage (input, output, cache)
- Cost per hour/day
- Errors by type
- Slow requests (> 30s)
- Agent version distribution (v1 vs v2)
- User satisfaction (если есть feedback)

# Alerts:
- Response time > 30s для > 5% запросов
- Success rate < 95%
- Cost per hour > $10
- Error rate > 2%
```

**Приоритет**: 🟡 **MEDIUM**
**ETA**: 2-3 дня
**Owner**: DevOps team
**Stack**: Grafana + Prometheus + Loki

---

### 10. Добавить логику "conversation complete" после 1 хода

**Проблема**:
- v2 не всегда понимает, когда диалог завершён
- Это приводит к лишним ходам

**Решение**:
```python
# Добавить анализ response для определения завершения:
def is_conversation_complete(response, context):
    """Определяет, завершён ли диалог"""

    # Если создан заказ и выдан tracking_id
    if response.order_created and response.tracking_id:
        return True

    # Если показаны продукты и нет follow-up вопроса
    if response.products_shown and not has_open_question(response):
        return True

    # Если ответ на простой вопрос (FAQ, часы работы)
    if is_simple_info_request(context.message) and response.info_provided:
        return True

    # Если пользователь сказал "спасибо" или "всё"
    if is_goodbye_message(context.last_user_message):
        return True

    return False
```

**Приоритет**: 🟡 **MEDIUM**
**ETA**: 2 дня
**Owner**: AI team
**Testing**: Повторный бенчмарк должен показать avg_turns < 1.0

---

## 🟢 НИЗКИЙ ПРИОРИТЕТ (Nice to Have)

### 11. Провести stress testing

**Цель**: Проверить поведение под высокой нагрузкой

**План**:
```bash
# Использовать locust или artillery для load testing:
# - 100+ concurrent users
# - 1000 requests за 5 минут
# - Микс простых и сложных запросов
# - Измерить: response time, error rate, cost

# Ожидаемые результаты:
# - Response time < 30s для 95% запросов
# - Error rate < 1%
# - No memory leaks
# - Cost < $5 per 1000 requests
```

**Приоритет**: 🟢 **LOW**
**ETA**: 1 день
**Owner**: QA team

---

### 12. Оптимизировать промпты для token usage

**Цель**: Уменьшить стоимость запросов

**Идеи**:
- Удалить избыточные инструкции из system prompt
- Использовать более короткие примеры
- Сжать описания MCP tools
- Кэшировать части промпта

**Потенциальная экономия**: 10-20% tokens

**Приоритет**: 🟢 **LOW**
**ETA**: 2-3 дня
**Owner**: AI team

---

### 13. Добавить caching для частых запросов

**Цель**: Ускорить ответы на повторяющиеся вопросы

**Примеры**:
```python
# Кэшировать:
- Список продуктов (ttl: 5 минут)
- FAQ (ttl: 1 час)
- Рабочие часы (ttl: 1 день)
- Информация о доставке (ttl: 1 час)

# Redis cache:
cache_key = f"products:{shop_id}:{filters_hash}"
cached_products = redis.get(cache_key)
if cached_products:
    return cached_products
```

**Потенциальная экономия**: 30-50% на часто запрашиваемые данные

**Приоритет**: 🟢 **LOW**
**ETA**: 2 дня
**Owner**: Backend team

---

### 14. Документировать best practices

**Цель**: Помочь команде поддерживать качество

**Документы**:
- Conversation flow design patterns
- Timeout optimization guidelines
- Token usage optimization tips
- Testing checklist for new features

**Приоритет**: 🟢 **LOW**
**ETA**: 1 день
**Owner**: Tech lead

---

## 📊 Метрики успеха (KPIs)

После внедрения улучшений:

| Метрика | Текущее (v2) | Целевое | Улучшение |
|---------|--------------|---------|-----------|
| **Success Rate** | 97.5% | 99.5%+ | +2% |
| **Avg Response Time** | 18.25s | 15s | -18% |
| **Simple Query Time** | 12-16s | < 10s | -25%+ |
| **Timeout Errors** | 1 (2.5%) | 0 (0%) | -100% |
| **Avg Turns** | 1.2 | 1.0 | -17% |
| **Token Usage** | Baseline | -15% | Оптимизация |
| **Cost per 1000 req** | TBD | < $3 | Целевой |

---

## 🗓️ Roadmap

### Неделя 1 (Критичные)
- [ ] День 1-2: Исправить сценарий 04 (VIP timeout)
- [ ] День 3: Настроить агрессивное завершение диалога
- [ ] День 4-5: Unit тесты + повторный бенчмарк

### Неделя 2 (Высокий приоритет)
- [ ] День 1-2: Оптимизировать простые запросы
- [ ] День 3: Добавить token usage tracking
- [ ] День 4-5: Метрики производительности в response

### Неделя 3 (Средний приоритет)
- [ ] День 1-2: A/B testing router
- [ ] День 3-4: Performance dashboard
- [ ] День 5: Conversation completion logic

### Неделя 4 (Deployment)
- [ ] День 1: Final testing
- [ ] День 2-3: A/B test 10% users
- [ ] День 4-5: Мониторинг и корректировки

### Неделя 5+ (Оптимизации)
- [ ] Stress testing
- [ ] Prompt optimization
- [ ] Caching implementation
- [ ] Documentation

---

## 🎯 Ожидаемые результаты

После всех улучшений:

✅ **v2 готов к production** с 99.5%+ success rate
✅ **Лучший UX**: средний response time 15s (vs текущий 18.25s)
✅ **0 timeout errors** на всех сценариях
✅ **Экономия 15-20%** на token usage и cost
✅ **Full observability** с real-time dashboard
✅ **Safe deployment** через A/B testing

**Итоговая оценка после улучшений: 5/5 ⭐⭐⭐⭐⭐**

---

**Создано**: AI Agent Testing Framework
**Дата**: 2025-10-09
**Версия**: 1.0
