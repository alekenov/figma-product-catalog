# 🚀 QUICK REFERENCE - Авторизация Telegram Бота

## ⚡ Самые Важные Команды

### Запуск Локально (4 Терминала)

```bash
# Terminal 1 - Backend
cd /Users/alekenov/figma-product-catalog/backend && python3 main.py

# Terminal 2 - MCP Server
cd /Users/alekenov/figma-product-catalog/mcp-server && python server.py

# Terminal 3 - Telegram Bot
cd /Users/alekenov/figma-product-catalog/telegram-bot && python bot.py

# Terminal 4 - Проверка БД
bash /Users/alekenov/figma-product-catalog/QUICK_DB_CHECK.sh
```

---

## 🔍 Проверка БД

### Быстро Посмотреть Статистику
```bash
bash /Users/alekenov/figma-product-catalog/QUICK_DB_CHECK.sh
```

### Найти Авторизованного Пользователя
```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT phone, customerName, telegram_user_id, telegram_username, created_at
FROM client
WHERE telegram_user_id IS NOT NULL
ORDER BY created_at DESC;
EOF
```

### Проверить Конкретного Пользователя
```bash
# Замени 123456789 на реальный Telegram ID
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT * FROM client WHERE telegram_user_id = '123456789';
EOF
```

### Статистика по Магазину
```bash
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db << 'EOF'
SELECT
  COUNT(*) as total,
  COUNT(CASE WHEN telegram_user_id IS NOT NULL THEN 1 END) as authorized,
  COUNT(CASE WHEN telegram_user_id IS NULL THEN 1 END) as not_authorized
FROM client WHERE shop_id = 8;
EOF
```

---

## 🧪 Тестовые Сценарии (в Telegram)

### Сценарий 1: Новый Пользователь
```
→ Пиши: /start
← Ожидай: Запрос авторизации (кнопка "Поделиться контактом")
✅ PASS если: Бот просит авторизацию
```

### Сценарий 2: Сообщение БЕЗ Авторизации
```
→ Пиши: Привет
← Ожидай: Запрос авторизации
✅ PASS если: Бот ответил запросом авторизации (главное!)
```

### Сценарий 3: Каталог БЕЗ Авторизации
```
→ Пиши: /catalog
← Ожидай: Запрос авторизации
✅ PASS если: Не показывает каталог
```

### Сценарий 4: Авторизация
```
→ Нажми: "Поделиться контактом"
→ Разреши: В диалоге Telegram
← Ожидай: "✅ Спасибо! Вы успешно авторизованы."
✅ PASS если: Видишь подтверждение
```

### Сценарий 5: После Авторизации
```
→ Пиши: /start
← Ожидай: Нормальное приветствие с меню
✅ PASS если: Меню появляется

→ Пиши: /catalog
← Ожидай: Категории каталога
✅ PASS если: Каталог открывается

→ Пиши: Букеты до 5000
← Ожидай: AI обрабатывает и показывает результаты
✅ PASS если: Работает как раньше но ТОЛЬКо после авторизации
```

---

## 📁 Ключевые Файлы

| Файл | Назначение |
|------|-----------|
| `/telegram-bot/bot.py` | Главный бот с авторизацией |
| `/backend/figma_catalog.db` | БД с таблицей `client` |
| `/telegram-bot/.env` | Конфиг (TELEGRAM_TOKEN уже там) |
| `AUTHORIZATION_IMPLEMENTATION_COMPLETE.md` | Полная сводка всех изменений |
| `LOCAL_TESTING_GUIDE.md` | Подробный гайд тестирования |

---

## ✅ Проверка Что Все Работает

```bash
# 1. Есть ли авторизация в коде?
grep -n "_request_authorization\|check_authorization" /Users/alekenov/figma-product-catalog/telegram-bot/bot.py | wc -l
# Ожидай: 10+ совпадений ✅

# 2. БД нормальная?
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db ".tables" | grep client
# Ожидай: client ✅

# 3. Структура таблицы верная?
sqlite3 /Users/alekenov/figma-product-catalog/backend/figma_catalog.db ".schema client" | grep telegram_user_id
# Ожидай: telegram_user_id VARCHAR ✅
```

---

## 🚀 Коммит и Пуш

```bash
# Перейти в проект
cd /Users/alekenov/figma-product-catalog

# Добавить все файлы
git add telegram-bot/bot.py telegram-bot/*.md *.md QUICK_DB_CHECK.sh

# Коммитить
git commit -m "feat: Add mandatory Telegram authorization to bot

- Add authorization checks to all bot functions
- Users cannot interact without sharing contact
- Data persists to SQLite database
- Comprehensive documentation included"

# Пушить
git push origin main

# Railway автоматически задеплоит!
```

---

## 🔄 Жизненный Цикл Авторизации

```
User Joins Bot
    ↓
Writes /start or sends message
    ↓
check_authorization() - query DB
    ↓
Not found in DB?
    ├─ YES → Show "Share Contact" button
    │        User taps → Telegram sends phone
    │        handle_contact() → HTTP POST to Backend
    │        Backend → INSERT INTO client (telegram_user_id, phone, ...)
    │        ✅ NOW AUTHORIZED
    │
    └─ NO → User is in DB ✅ AUTHORIZED!
        ↓
    All features work:
    - /catalog ✅
    - Regular messages ✅
    - /myorders ✅
    - Buttons ✅
```

---

## 🐛 Если Что-то Не Работает

### Bot не отвечает
```bash
# 1. Проверить логи bot.py - должны быть "Bot initialized successfully"
# 2. Проверить MCP server запущен: curl http://localhost:8000/health
# 3. Проверить Backend запущен: curl http://localhost:8014/health
```

### Авторизация не работает
```bash
# 1. Проверить в БД есть ли запись:
sqlite3 /backend/figma_catalog.db "SELECT * FROM client WHERE telegram_user_id = 'ВАШ_ID';"

# 2. Если нет - проверить логи bot.py на ошибки
# 3. Если есть - возможно check_authorization() не читает из БД
```

### Данные не сохраняются
```bash
# 1. Проверить Backend логи на ошибки при POST /clients/telegram/register
# 2. Проверить что номер телефона отправляется корректно: curl -X POST ...
# 3. Проверить БД таблица есть: sqlite3 /backend/figma_catalog.db ".tables"
```

---

## 📞 Важные Параметры

| Параметр | Значение | Файл |
|----------|----------|------|
| Backend URL | http://localhost:8014 | .env |
| MCP Server URL | http://localhost:8000 | .env |
| Telegram Token | 5261... (в .env) | .env |
| Shop ID | 8 | .env |
| DB Path (local) | /backend/figma_catalog.db | N/A |
| Bot polling | Enabled (local dev) | bot.py |

---

## 🎯 Финальный Чек-Лист Перед Продакшеном

- [ ] Все 4 компонента запускаются локально
- [ ] Все 5 тестовых сценариев работают
- [ ] БД показывает авторизованных пользователей
- [ ] Изменения запушены на github
- [ ] Railway задеплоил (проверить https://figma-product-catalog-production.up.railway.app/health)
- [ ] Telegram бот отвечает в production

---

## 📚 Полные Гайды

Если нужно глубже разобраться:
- 📖 `AUTHORIZATION_IMPLEMENTATION_COMPLETE.md` - Полная сводка
- 📖 `LOCAL_TESTING_GUIDE.md` - Как тестировать
- 📖 `DATABASE_GUIDE.md` - Структура БД
- 📖 `telegram-bot/AUTH_IMPROVEMENTS.md` - Технические детали
- 📖 `telegram-bot/CHANGES_SUMMARY.md` - Все изменения в коде

---

**Готово! 🚀 Система авторизации полностью реализована и задокументирована.**
