# 🧪 Руководство по локальному тестированию Telegram ботов

Пошаговая инструкция для тестирования Customer Bot и Admin Bot в development режиме.

---

## 📋 Что будем тестировать

### Customer Bot (для клиентов)
- ✅ Авторизация через контакт
- ✅ Визуальный поиск (отправка фото)
- ✅ Текстовые запросы через AI
- ✅ Просмотр товаров
- ✅ Создание заказа

### Admin Bot (для сотрудников)
- ✅ Авторизация через контакт
- ✅ Просмотр списка заказов
- ✅ Изменение статуса заказа
- ✅ Добавление товара
- ✅ Просмотр склада

---

## 🚀 Шаг 1: Подготовка окружения

### 1.1 Проверка Python зависимостей

```bash
# Должен быть Python 3.10+
python3 --version

# Проверяем установлены ли зависимости для ботов
cd customer-bot
pip install -r requirements.txt

cd ../admin-bot
pip install -r requirements.txt
```

### 1.2 Проверка .env файлов

```bash
# Customer Bot Development
cat customer-bot/.env.development
# Должны быть: TELEGRAM_TOKEN, DEFAULT_SHOP_ID=8, MCP_SERVER_URL, AI_AGENT_URL

# Admin Bot Development
cat admin-bot/.env.development
# Должны быть: TELEGRAM_TOKEN, DEFAULT_SHOP_ID=8, MCP_SERVER_URL
```

---

## 🔧 Шаг 2: Запуск Backend сервисов

Открываем **5 терминалов** и запускаем сервисы по порядку:

### Terminal 1: Backend API (порт 8014)

```bash
cd backend
python main.py
```

**✅ Ожидаемый вывод:**
```
INFO:     Uvicorn running on http://0.0.0.0:8014
INFO:     Application startup complete.
```

**Проверка:**
```bash
curl http://localhost:8014/health
# Ответ: {"status":"healthy"}
```

---

### Terminal 2: MCP Server (порт 8000)

```bash
cd mcp-server
./start.sh
```

**✅ Ожидаемый вывод:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
MCP Server started successfully
```

**Проверка:**
```bash
curl http://localhost:8000/health
# Ответ: {"status":"ok"}
```

---

### Terminal 3: AI Agent Service (порт 8002)

```bash
cd ai-agent-service
python main.py
```

**✅ Ожидаемый вывод:**
```
INFO:     Uvicorn running on http://0.0.0.0:8002
AI Agent Service initialized with Claude Sonnet 4.5
```

**Проверка:**
```bash
curl http://localhost:8002/health
# Ответ: {"status":"healthy"}
```

---

### Terminal 4: Customer Bot (Development)

```bash
cd customer-bot
ENVIRONMENT=development python bot.py
```

**✅ Ожидаемый вывод:**
```
✅ Loaded .env.development
🤖 Customer Bot - Starting...
📍 Shop ID: 8
🤖 AI Agent: http://localhost:8002
🔧 MCP Server: http://localhost:8000
📡 Mode: POLLING (local development)

INFO: Bot started successfully
```

**❌ Возможные ошибки:**
- `ValueError: TELEGRAM_TOKEN must be set` → Проверьте .env.development
- `Connection refused to localhost:8000` → MCP Server не запущен
- `Connection refused to localhost:8002` → AI Agent не запущен

---

### Terminal 5: Admin Bot (Development)

```bash
cd admin-bot
ENVIRONMENT=development python bot.py
```

**✅ Ожидаемый вывод:**
```
✅ Loaded .env.development
🔧 Admin Bot - Starting...
📍 Shop ID: 8
🔧 MCP Server: http://localhost:8000
📡 Mode: POLLING (local development)

INFO: Admin bot started successfully
```

---

## 📱 Шаг 3: Тестирование Customer Bot

### 3.1 Авторизация

1. Откройте Telegram
2. Найдите бота `@kitokazbot`
3. Отправьте команду `/start`

**✅ Ожидается:**
```
🌸 Добро пожаловать в Cvety.kz!

Для использования бота необходимо авторизоваться.

Возможности:
• 🔍 Поиск букетов по фото
• 💬 Заказ через естественный язык
• 📦 Отслеживание заказов
• 💳 Оплата Kaspi Pay

Нажмите кнопку ниже, чтобы начать:
[📱 Поделиться контактом]
```

4. Нажмите кнопку "📱 Поделиться контактом"

**✅ Ожидается:**
```
✅ Спасибо, [Ваше имя]! Вы успешно авторизованы.

Отправьте фото букета или напишите ваш запрос!
```

**Логи в Terminal 4:**
```
INFO: authorization_check user_id=123456789 shop_id=8
INFO: registration_started user_id=123456789
INFO: registration_completed user_id=123456789 client_id=42
```

---

### 3.2 Тест текстового запроса (AI)

Отправьте боту:
```
Покажи розы до 15000 тенге
```

**✅ Ожидается:**
- Бот начинает "печатать..." (typing indicator)
- Через 3-5 секунд приходит ответ от AI с описанием доступных роз
- Возможно показ фотографий товаров

**Логи в Terminal 3 (AI Agent):**
```
INFO: chat_request user_id=123456789 shop_id=8
INFO: mcp_tool_call tool=list_products
INFO: response_generated tokens=450
```

**Логи в Terminal 4 (Customer Bot):**
```
INFO: message_received message_length=25
INFO: message_handled_successfully
```

---

### 3.3 Тест визуального поиска

1. Найдите любое фото букета в интернете
2. Отправьте фото боту
3. Можно добавить подпись: "Найди похожие"

**✅ Ожидается:**
- Бот начинает "печатать..."
- Через 5-10 секунд приходит ответ с похожими букетами
- Могут прийти фотографии похожих товаров

**Логи в Terminal 4:**
```
INFO: photo_received photo_count=4
INFO: visual_search_started image_url=https://...
INFO: message_handled_successfully
```

**Логи в Terminal 3 (AI Agent):**
```
INFO: image_search_request
INFO: mcp_tool_call tool=search_similar_bouquets
INFO: found_similar_products count=3
```

---

### 3.4 Тест создания заказа

Отправьте боту:
```
Хочу заказать букет роз на завтра к 15:00, доставка на Абая 150
```

**✅ Ожидается:**
- AI начинает диалог для уточнения деталей
- Запрашивает: телефон получателя, имя получателя
- Предлагает варианты букетов в нужной ценовой категории
- Показывает итоговую стоимость с доставкой

**Логи в Terminal 3:**
```
INFO: order_intent_detected
INFO: mcp_tool_call tool=create_order
INFO: order_created order_id=156 tracking_id=ABC123
```

---

## 👨‍💼 Шаг 4: Тестирование Admin Bot

### 4.1 Авторизация

1. Откройте Telegram
2. Найдите бота `@Dflowersbot`
3. Отправьте команду `/start`

**⚠️ ВАЖНО:** У вас должен быть номер телефона, зарегистрированный в системе как сотрудник!

**✅ Ожидается:**
```
🔧 Admin Bot - Cvety.kz

Для доступа необходимо авторизоваться.
Нажмите кнопку ниже:
[📱 Поделиться контактом]
```

4. Нажмите кнопку "📱 Поделиться контактом"

**✅ Ожидается:**
```
✅ Добро пожаловать, [Имя]!

Вы авторизованы как сотрудник.
Используйте /help для списка команд.
```

---

### 4.2 Тест просмотра заказов

Отправьте команду:
```
/orders
```

**✅ Ожидается (MVP):**
```
📦 Последние заказы

Статус: NEW/PAID

#156 - Букет роз, 12,000₸
     Клиент: +77011234567
     Доставка: 2025-10-24 15:00

#157 - Композиция, 25,000₸
     Клиент: +77027778899
     Доставка: 2025-10-25 12:00

Всего: 2 заказа
```

**Логи в Terminal 5:**
```
INFO: orders_command_executed user_id=987654321
INFO: mcp_tool_call tool=list_orders shop_id=8
```

---

### 4.3 Тест изменения статуса заказа

Отправьте команду:
```
/status 156 IN_PRODUCTION
```

**✅ Ожидается (MVP):**
```
✅ Статус заказа #156 изменен на IN_PRODUCTION

Клиент получит уведомление на +77011234567
```

**Логи в Terminal 5:**
```
INFO: status_change_command order_id=156 new_status=IN_PRODUCTION
INFO: mcp_tool_call tool=update_order_status
INFO: status_updated_successfully
```

---

### 4.4 Тест добавления товара

Отправьте команду:
```
/add_product
```

**✅ Ожидается (MVP):**
```
➕ Добавление товара

1️⃣ Отправьте фото букета
2️⃣ Введите данные в формате:
   Название, тип, цена

Пример: Букет "Романтика", bouquet, 1500000

Типы: bouquet, composition, box
Цена в копейках (15000 тенге = 1500000 копеек)
```

Далее:
1. Отправляете фото
2. Отправляете текст: `Букет "Нежность", bouquet, 1200000`

**✅ Ожидается:**
```
✅ Товар #234 добавлен!

Название: Букет "Нежность"
Тип: bouquet
Цена: 12,000₸
Фото загружено

Товар опубликован и доступен клиентам.
```

---

### 4.5 Тест просмотра склада

Отправьте команду:
```
/warehouse
```

**✅ Ожидается (MVP):**
```
📦 Склад - Остатки

🌹 Цветы:
• Розы красные: 50 шт ✅
• Розы белые: 30 шт ⚠️ Мало
• Лилии: 5 шт ❌ Критично

🎀 Материалы:
• Лента атласная: 100 м ✅
• Коробки большие: 15 шт ✅

Обновлено: 2025-10-23 14:30
```

---

## ✅ Чек-лист тестирования

### Customer Bot (@kitokazbot)

- [ ] Бот отвечает на `/start`
- [ ] Авторизация через контакт работает
- [ ] Текстовый запрос обрабатывается AI (3-5 сек)
- [ ] Визуальный поиск по фото работает (5-10 сек)
- [ ] Бот показывает фотографии товаров
- [ ] Создание заказа через диалог работает
- [ ] Логи показывают успешные MCP вызовы
- [ ] Нет ошибок в Terminal 4

### Admin Bot (@Dflowersbot)

- [ ] Бот отвечает на `/start`
- [ ] Авторизация через контакт работает (для сотрудника)
- [ ] `/orders` показывает список заказов
- [ ] `/status` меняет статус заказа
- [ ] `/add_product` начинает диалог добавления товара
- [ ] `/warehouse` показывает остатки склада
- [ ] Логи показывают успешные MCP вызовы
- [ ] Нет ошибок в Terminal 5

### Backend сервисы

- [ ] Backend API отвечает на http://localhost:8014/health
- [ ] MCP Server отвечает на http://localhost:8000/health
- [ ] AI Agent отвечает на http://localhost:8002/health
- [ ] Все логи показывают `INFO` уровень (не `ERROR`)

---

## 🐛 Возможные проблемы и решения

### Проблема: "Connection refused" при запуске бота

**Причина:** Backend сервисы не запущены

**Решение:**
1. Проверьте что запущены все 3 сервиса (Backend, MCP, AI Agent)
2. Проверьте порты: `lsof -i :8014,8000,8002`
3. Убедитесь что в .env.development правильные URL

---

### Проблема: Бот не отвечает на сообщения

**Причина:** Неправильный токен или бот не в polling режиме

**Решение:**
1. Проверьте токен: `curl "https://api.telegram.org/bot<TOKEN>/getMe"`
2. Убедитесь что `WEBHOOK_URL` пустой в .env.development
3. Перезапустите бота

---

### Проблема: AI не отвечает (timeout)

**Причина:** AI Agent Service не запущен или нет CLAUDE_API_KEY

**Решение:**
1. Проверьте Terminal 3 на ошибки
2. Убедитесь что `CLAUDE_API_KEY` установлен в `ai-agent-service/.env`
3. Проверьте: `curl http://localhost:8002/health`

---

### Проблема: "Not authorized" в Admin Bot

**Причина:** Номер телефона не зарегистрирован как сотрудник

**Решение:**
1. Сначала зарегистрируйтесь через Customer Bot
2. Затем в базе данных добавьте роль DIRECTOR для вашего user_id
3. Или используйте тестовый номер `+77015211545` (если есть в БД)

---

### Проблема: Фото товаров не показываются

**Причина:** URL фотографий неправильные или недоступны

**Решение:**
1. Проверьте что Cloudflare Worker работает
2. Проверьте URL в БД: `SELECT image FROM product LIMIT 5`
3. Попробуйте открыть URL в браузере

---

## 📊 Логи и отладка

### Включить DEBUG логи

В `.env.development` измените:
```bash
LOG_LEVEL=DEBUG
```

Перезапустите бота.

### Смотреть логи в реальном времени

```bash
# Customer Bot
tail -f customer-bot/logs/bot.log

# Admin Bot
tail -f admin-bot/logs/bot.log
```

### Проверить MCP вызовы

Логи MCP Server показывают все вызовы инструментов:
```
INFO: mcp_tool_called tool=list_products params={'shop_id': 8}
INFO: mcp_tool_response success=True result_count=15
```

---

## 🎯 Критерии успешного теста

### ✅ Customer Bot работает если:
1. Авторизация через контакт проходит успешно
2. AI отвечает на текстовые запросы за < 10 секунд
3. Визуальный поиск находит похожие букеты
4. Можно создать заказ через диалог
5. Нет ошибок в логах

### ✅ Admin Bot работает если:
1. Авторизация сотрудника проходит успешно
2. `/orders` показывает список заказов
3. `/status` меняет статус заказа
4. `/add_product` позволяет добавить товар
5. Нет ошибок в логах

### ✅ Все сервисы работают если:
- Backend API: `http://localhost:8014/health` → 200 OK
- MCP Server: `http://localhost:8000/health` → 200 OK
- AI Agent: `http://localhost:8002/health` → 200 OK
- Customer Bot: Отвечает в Telegram
- Admin Bot: Отвечает в Telegram

---

## 🚀 После успешного теста

Когда все тесты пройдены:

1. **Остановите локальные сервисы** (Ctrl+C в каждом терминале)
2. **Задеплойте на Railway:**
   ```bash
   # Customer Bot Production
   railway service customer-bot-production
   railway up --ci

   # Admin Bot Production
   railway service admin-bot-production
   railway up --ci
   ```
3. **Проверьте production логи:**
   ```bash
   railway logs --service customer-bot-production
   railway logs --service admin-bot-production
   ```

---

## 📞 Нужна помощь?

Если что-то не работает:
1. Проверьте все пункты чек-листа
2. Посмотрите раздел "Возможные проблемы"
3. Включите DEBUG логи
4. Проверьте логи всех сервисов

**Частые вопросы:**
- "Бот не отвечает" → Проверьте токен и polling режим
- "AI долго отвечает" → Проверьте Claude API ключ
- "Не авторизуется" → Проверьте MCP Server и БД

Удачного тестирования! 🚀
