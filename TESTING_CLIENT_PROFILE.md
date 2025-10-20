# 🧪 Тестирование Системы Персонализации Клиентов

## 📋 Что тестируем?

Система автоматически создает профиль клиента на основе истории заказов и использует его для персонализации общения через AI бота.

**Функции:**
- ✅ Автоматическое создание профиля после доставленных заказов
- ✅ Расчет среднего/минимального/максимального чека
- ✅ Топ-3 получателей с адресами
- ✅ Персонализированные рекомендации AI
- ✅ GDPR compliance (удаление данных, отказ от персонализации)

---

## 🎯 Способ 1: Через Telegram Бота (Рекомендуется)

### Шаг 1: Создайте первый заказ

Откройте бота [@cvety_kz_bot](https://t.me/cvety_kz_bot) и напишите:

```
Хочу заказать букет роз на 15000₸
```

AI создаст заказ. Запомните номер телефона (ваш Telegram ID).

### Шаг 2: Переведите заказ в "Доставлен"

1. Откройте админку: https://frontend-production-6869.up.railway.app
2. Войдите под логином `+77015211545`, код `1234`
3. Найдите ваш заказ в списке
4. Переведите статус в: `PAID` → `ACCEPTED` → `IN_PRODUCTION` → `READY` → `IN_DELIVERY` → `DELIVERED`

**Важно:** Профиль создается только после статуса `DELIVERED`!

### Шаг 3: Создайте второй заказ

Снова напишите боту:

```
Привет! Хочу заказать букет
```

**Ожидаемый результат:** Бот должен ответить с персонализацией:

```
Хотите как обычно? Могу подобрать букет в вашем бюджете (около 15 тыс ₸).
```

### Шаг 4: Тест автозаполнения получателя

Если в первом заказе был получатель "Мария", напишите:

```
Отправить Марии
```

**Ожидаемый результат:** Бот автоматически подставит номер телефона и адрес Марии из профиля.

### Шаг 5: GDPR тесты

Попросите бота удалить ваши данные:

```
Удали мои данные
```

**Ожидаемый результат:** Профиль удален, бот больше не использует историю.

---

## 🔧 Способ 2: API Тестирование (Технический)

### Быстрый тест

Запустите автоматический тест:

```bash
cd /Users/alekenov/figma-product-catalog
./test_client_profile.sh
```

Скрипт создаст тестовый заказ и покажет инструкции для проверки профиля.

### Ручное API тестирование

#### 1. Проверить существующий профиль

```bash
curl -s "https://figma-product-catalog-production.up.railway.app/api/v1/client_profile?phone=77015211545" \
  -H "shop_id: 8" | python3 -m json.tool
```

**Ожидаемый ответ:**
```json
{
  "client_id": 123,
  "allow_personalization": true,
  "budget": {
    "avg": 1500000,
    "min": 1000000,
    "max": 2000000,
    "total_orders": 5
  },
  "frequent_recipients": [
    {
      "name": "Мария",
      "phone": "77771234567",
      "address": "ул. Абая 150",
      "order_count": 3
    }
  ],
  "last_order_at": "2025-10-17T10:30:00"
}
```

#### 2. Отключить персонализацию

```bash
curl -X PATCH "https://figma-product-catalog-production.up.railway.app/api/v1/client_profile/privacy?phone=77015211545&action=disable_personalization" \
  -H "shop_id: 8"
```

#### 3. Удалить все данные клиента

```bash
curl -X PATCH "https://figma-product-catalog-production.up.railway.app/api/v1/client_profile/privacy?phone=77015211545&action=delete_profile_data" \
  -H "shop_id: 8"
```

---

## 🐞 Способ 3: Проверка логов AI Agent

Посмотрите, как AI использует профиль:

```bash
cd /Users/alekenov/figma-product-catalog/ai-agent-service
railway logs --tail 100 | grep -A 5 "get_client_profile"
```

**Ожидаемые логи:**
```
[INFO] tool_call: get_client_profile {"customer_phone": "77015211545"}
[INFO] tool_result: {"budget": {"avg": 1500000}, "frequent_recipients": [...]}
[INFO] ai_response: "Хотите как обычно? Могу подобрать букет в вашем бюджете..."
```

---

## 📊 Проверка базы данных (Опционально)

### Через Railway CLI

```bash
cd /Users/alekenov/figma-product-catalog/backend
railway service figma-product-catalog
railway run psql -c "SELECT * FROM client_profile LIMIT 5;"
```

### Структура таблицы

```sql
TABLE client_profile (
  id SERIAL PRIMARY KEY,
  client_id INTEGER REFERENCES client(id),
  shop_id INTEGER REFERENCES shop(id),
  avg_order_total INTEGER,           -- Средний чек в копейках
  min_order_total INTEGER,           -- Минимальный чек
  max_order_total INTEGER,           -- Максимальный чек
  total_orders_count INTEGER,        -- Количество заказов
  frequent_recipients TEXT,          -- JSON топ-3 получателей
  last_order_at TIMESTAMP,           -- Дата последнего заказа
  allow_personalization BOOLEAN,     -- GDPR согласие
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

---

## ✅ Чек-лист для тестирования

- [ ] Профиль создается после первого DELIVERED заказа
- [ ] Бюджет рассчитывается корректно (avg/min/max)
- [ ] Топ-3 получателей отображаются
- [ ] AI использует профиль для персонализации ответов
- [ ] Автозаполнение получателя работает
- [ ] `disable_personalization` блокирует использование профиля
- [ ] `delete_profile_data` удаляет все данные
- [ ] `enable_personalization` восстанавливает функционал

---

## 🎯 Ожидаемое поведение AI

### Клиент С историей (5 заказов, avg=15000₸)

**User:** "Хочу заказать букет"
**AI:** "Хотите как обычно? Могу подобрать букет в вашем бюджете (около 15 тыс ₸). Доставить Марии на обычный адрес (ул. Абая 87)?"

### Клиент БЕЗ истории (новый)

**User:** "Хочу заказать букет"
**AI:** "Какой бюджет рассматриваете? Это для особого случая?"

### GDPR - Клиент отказался от персонализации

**User:** "Хочу заказать букет"
**AI:** (НЕ использует историю, ведет себя как с новым клиентом)

---

## 🚨 Troubleshooting

### Профиль не создается

**Проблема:** После DELIVERED заказа профиль не появился.

**Решение:**
1. Проверьте логи backend:
   ```bash
   railway logs | grep "profile_builder"
   ```
2. Убедитесь, что статус именно `DELIVERED` (не `delivered`)
3. Проверьте, что у клиента есть номер телефона

### AI не использует профиль

**Проблема:** AI не персонализирует ответы.

**Решение:**
1. Проверьте `allow_personalization=true` в профиле
2. Посмотрите логи AI Agent:
   ```bash
   railway logs | grep "get_client_profile"
   ```
3. Убедитесь, что MCP client правильно вызывает backend

### Ошибка 404 при запросе профиля

**Проблема:** `GET /client_profile` возвращает 404.

**Решение:**
1. Профиль создается ТОЛЬКО после DELIVERED заказов
2. Проверьте, что клиент существует в базе:
   ```bash
   railway run psql -c "SELECT * FROM client WHERE phone='77015211545';"
   ```
3. Если клиента нет - создайте заказ через публичный endpoint

---

## 📚 Дополнительные ресурсы

- **Backend API:** `backend/api/client_profile.py:29` - GET endpoint
- **Service Logic:** `backend/services/profile_builder_service.py:51` - Расчет профиля
- **AI Integration:** `ai-agent-service/services/mcp_client.py:433` - MCP tool
- **Database Migration:** `backend/database.py:191` - Создание таблицы

---

## 💡 Insight

**Почему профиль обновляется только после DELIVERED?**

Если обновлять после каждого статуса (PAID, ACCEPTED и т.д.), в профиле будут незавершенные заказы:
- Клиент отменил → средний чек искажен
- Возврат → деньги вернулись, но считаются в статистике

**DELIVERED** = финальный статус, деньги получены, товар доставлен. Только эти заказы влияют на бюджетные предпочтения клиента.
