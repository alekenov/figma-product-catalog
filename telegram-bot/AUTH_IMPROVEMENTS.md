# 🔐 Улучшения Авторизации Telegram Бота

## 📋 Что было изменено

Добавлена **обязательная авторизация** для всех функций бота. Теперь пользователь не может использовать бот без номера телефона, сохраненного в БД.

---

## 🔧 Основные улучшения

### 1️⃣ Новый вспомогательный метод: `_request_authorization()`

**Назначение:** Унифицированное сообщение для запроса авторизации

**Что делает:**
- Показывает кнопку "📱 Поделиться контактом"
- Объясняет зачем нужна авторизация
- Повторно используется во всех функциях

```python
async def _request_authorization(self, update: Update):
    """Request user authorization via contact sharing."""
    contact_button = KeyboardButton(
        text="📱 Поделиться контактом",
        request_contact=True
    )
    keyboard = ReplyKeyboardMarkup(
        [[contact_button]],
        one_time_keyboard=True,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "📱 Для полного доступа к функциям бота необходимо поделиться контактом.\n\n"
        "Это нужно для:\n"
        "• Оформления заказов\n"
        "• Отслеживания доставки\n"
        "• Сохранения ваших данных\n\n"
        "Нажмите кнопку ниже, чтобы авторизоваться:",
        reply_markup=keyboard
    )
```

---

### 2️⃣ Обновлены команды с проверкой авторизации

#### `/start` - Начальная команда
**ДО:** Проверяла авторизацию
**ПОСЛЕ:** Использует новый метод `_request_authorization()`

```python
# Перед:
if not is_authorized:
    # ... старый код с дублированием кнопки

# После:
if not is_authorized:
    await self._request_authorization(update)
    return
```

#### `/catalog` - Просмотр каталога
**ДО:** Не проверяла авторизацию ❌
**ПОСЛЕ:** Обязательна проверка авторизации ✅

```python
async def catalog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check authorization
    is_authorized = await self.check_authorization(update.effective_user.id)
    if not is_authorized:
        await self._request_authorization(update)
        return

    # Показать каталог...
```

#### Кнопки каталога (button_callback)
**ДО:** Не проверяла авторизацию ❌
**ПОСЛЕ:** Обязательна проверка авторизации ✅

```python
# Когда пользователь нажимает "Готовые букеты", "На заказ" и т.д.
is_authorized = await self.check_authorization(update.effective_user.id)
if not is_authorized:
    await query.edit_message_text(
        "📱 Для использования каталога необходимо авторизоваться.\n\n"
        "Используйте /start для регистрации."
    )
    return
```

#### Обычные сообщения (handle_message) - **САМОЕ ВАЖНОЕ**
**ДО:** Не проверяла авторизацию ❌
**ПОСЛЕ:** Первым делом проверяет авторизацию ✅

```python
async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text

    # ✅ НОВОЕ: Проверка авторизации ДО обработки сообщения
    is_authorized = await self.check_authorization(user_id)
    if not is_authorized:
        await self._request_authorization(update)
        return

    # Отправить сообщение в AI Agent...
```

**Результат:**
- Пользователь напишет "Покажи букеты" → бот просит авторизацию
- Не может использовать AI функции без номера телефона
- Защита от использования без согласия на сохранение контакта

---

### 3️⃣ Исправлен endpoint очистки истории

**ДО:** `POST /clear-history/{user_id}` ❌ (неправильный путь)
**ПОСЛЕ:** `DELETE /conversations/{user_id}` ✅ (правильный API)

```python
# Перед:
response = await client.post(
    f"{self.ai_agent_url}/clear-history/{user_id}",
    params={"channel": "telegram"}
)

# После:
response = await client.delete(
    f"{self.ai_agent_url}/conversations/{user_id}",
    params={"channel": "telegram"}
)
```

---

## 🔄 Полный поток авторизации

```
User sends message:
"Покажи букеты"
       ↓
handle_message() вызывается
       ↓
check_authorization(user_id)
       ↓
┌─────────────────────┬──────────────────┐
│ Авторизирован?      │ Не авторизирован │
│ (есть в БД)         │ (нет в БД)       │
└─────────────────────┼──────────────────┘
         ↓                      ↓
   Обработать            _request_authorization()
   сообщение
   в AI Agent            Показать кнопку
         ↓               📱 Поделиться
   Отправить            контактом
   ответ                      ↓
                         User tap button
                              ↓
                         handle_contact()
                              ↓
                         register_telegram_client()
                         в БД
                              ↓
                         Авторизация успешна ✅
                              ↓
                         User может писать
                         боту сообщения
```

---

## 📊 Сравнение ДО и ПОСЛЕ

| Функция | ДО | ПОСЛЕ |
|---------|-------|--------|
| `/start` | ✅ Проверяет | ✅ Проверяет (улучшено) |
| `/catalog` | ❌ НЕ проверяет | ✅ Проверяет |
| Кнопки каталога | ❌ НЕ проверяют | ✅ Проверяют |
| Обычные сообщения | ❌ НЕ проверяют | ✅ Проверяют |
| `/clear` | ✅ Работает | ✅ Исправлен API |
| `/myorders` | ✅ Проверяет | ✅ Проверяет |

---

## 🧪 Как тестировать

### Сценарий 1: Новый пользователь без авторизации
```
1. Открыть чат бота
2. Написать "Привет"
   → Бот просит авторизацию: "📱 Для полного доступа..."
3. Написать "Покажи букеты"
   → Бот просит авторизацию
4. Нажать /catalog
   → Бот просит авторизацию
```

### Сценарий 2: Авторизованный пользователь
```
1. Нажать /start
   → Если уже авторизован: "👋 Здравствуйте!"
2. Написать "Покажи розы до 10000"
   → Бот отправляет в AI Agent (нет проверки - уже авторизован)
3. Нажать /catalog
   → Показывает категории каталога
```

### Сценарий 3: Авторизация через контакт
```
1. Новый пользователь нажимает /start
2. Бот показывает кнопку "📱 Поделиться контактом"
3. User нажимает кнопку
4. Telegram запрашивает разрешение на отправку контакта
5. User подтверждает
6. handle_contact() сохраняет номер в БД
7. User видит: "✅ Спасибо! Вы успешно авторизованы."
8. Теперь может использовать все функции бота
```

---

## 🎯 Преимущества

✅ **Безопасность** - Только авторизованные пользователи могут использовать бот
✅ **Консистентность** - Одинаковое поведение на /start, /catalog, в сообщениях
✅ **DRY принцип** - Единый метод `_request_authorization()` вместо дублирования кода
✅ **UX улучшение** - Четкое сообщение о необходимости авторизации
✅ **Трекинг** - Все заказы привязаны к сохраненному номеру телефона

---

## 📝 Примечания для разработки

1. **Database:** Авторизация проверяется через MCP client:
   ```python
   client = await self.mcp_client.get_telegram_client(
       telegram_user_id=str(user_id),
       shop_id=self.shop_id
   )
   return client is not None  # True если есть номер в БД
   ```

2. **Error handling:** Если проверка авторизации упадет, функция вернет `False` (не авторизован) и попросит авторизацию

3. **Performance:** Каждая проверка делает запрос в БД (~50ms), но это небольшая цена за безопасность

4. **Масштабируемость:** В будущем можно добавить:
   - Кэширование статуса авторизации (Redis)
   - Рефреш токены для ускорения проверок
   - Роли пользователей (admin, customer, manager)
