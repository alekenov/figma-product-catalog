# Backend Utility Scripts

Эта директория содержит вспомогательные скрипты для обслуживания и отладки приложения.

## 📊 Database Utilities

### `check_production_db.py`
Проверка production базы данных на Railway.
- Подключается к production PostgreSQL
- Проверяет количество таблиц, записей
- Выводит статистику по основным таблицам

**Использование**:
```bash
cd backend
python3 scripts/check_production_db.py
```

### `check_production_users.py`
Проверка пользователей в production БД.
- Список всех пользователей
- Роли и shop_id
- Активность пользователей

### `analyze_shops.py`
Анализ магазинов и их конфигураций.
- Список всех shops
- Настройки магазинов
- Статистика по заказам и продуктам

---

## 💳 Payment Utilities

### `check_all_payments.py`
Проверка всех платежей Kaspi Pay.
- Статус всех платежей в БД
- Сверка с Kaspi API
- Поиск несоответствий

### `check_kaspi_payments.py`
Детальная проверка конкретных платежей Kaspi.
- Проверка статуса payment по ID
- История изменений
- Логи транзакций

### `manual_check_and_refund.py`
Ручная проверка и возврат платежей.
- Поиск платежа по tracking_id
- Возврат средств через Kaspi API
- Логирование операций возврата

---

## 🧪 Testing Utilities

### `create_test_user.py`
Создание тестового пользователя.
- Создает пользователя с ролью DIRECTOR
- Генерирует случайный пароль
- Выводит токен доступа

**Использование**:
```bash
python3 scripts/create_test_user.py
```

### `create_test_product.py`
Создание тестового продукта.
- Создает продукт с рандомными данными
- Назначает shop_id
- Добавляет warehouse item

---

## 🗑️ Maintenance Utilities

### `cleanup_expired_reservations.py`
Очистка истекших резервирований товаров.
- Находит резервирования старше 15 минут
- Освобождает зарезервированные товары
- Запускать как cron job каждые 10 минут

**Cron настройка**:
```bash
*/10 * * * * cd /path/to/backend && python3 scripts/cleanup_expired_reservations.py
```

### `delete_product.py`
Удаление продукта из БД (через прямой SQL).
- Удаляет продукт по ID
- Каскадно удаляет связанные записи
- **Осторожно**: необратимая операция

### `delete_product_api.py`
Удаление продукта через API (рекомендуется).
- Использует DELETE /api/v1/products/{id}
- Проверяет авторизацию
- Безопаснее, чем прямой SQL

---

## 🔐 Security & Auth

### `get_token.py`
Получение JWT токена для тестирования API.
- Логин через /api/v1/auth/login
- Выводит access_token
- Использовать для curl/Postman тестов

**Использование**:
```bash
python3 scripts/get_token.py +77015211545 1234
```

### `fix_admin_password.py`
Сброс пароля администратора.
- Находит пользователя по phone
- Обновляет пароль на новый
- Хеширует через bcrypt

**Использование**:
```bash
python3 scripts/fix_admin_password.py +77015211545 new_password_123
```

---

## 🛠️ Data Fixes

### `fix_local_db_enums.py`
Исправление enum значений в локальной БД.
- Конвертирует lowercase → UPPERCASE для OrderStatus
- Исправляет 'new' → 'NEW', 'paid' → 'PAID' и т.д.
- Запускать после импорта legacy данных

### `check_order_api.py`
Проверка API заказов.
- Тестирует основные endpoints orders API
- Проверяет авторизацию
- Валидация ответов

---

## 🏪 Initialization Scripts

### `init_recipes.py`
Инициализация рецептов для продуктов.
- Загружает базовые рецепты из JSON/CSV
- Связывает продукты с warehouse items
- Создает Recipe записи

### `init_warehouse.py`
Инициализация склада.
- Создает базовые warehouse items
- Устанавливает начальные количества
- Настраивает критические минимумы

---

## ⚠️ Important Notes

### Безопасность
- **НЕ запускать** скрипты на production без понимания последствий
- Всегда делать backup БД перед изменениями
- Проверять shop_id для multi-tenancy isolation

### Окружения
Большинство скриптов используют переменные окружения:
- `DATABASE_URL` - подключение к БД
- `SECRET_KEY` - JWT секрет
- `KASPI_API_BASE_URL` - Kaspi Pay endpoint
- `KASPI_ACCESS_TOKEN` - Kaspi API токен

### Логирование
Скрипты логируют в stdout. Для сохранения логов:
```bash
python3 scripts/script_name.py >> logs/script.log 2>&1
```

---

## 📝 Contributing

При добавлении нового скрипта:
1. Добавить описание в этот README
2. Добавить docstring в начало скрипта
3. Использовать `if __name__ == "__main__":` для запуска
4. Обрабатывать ошибки gracefully

---

**Последнее обновление**: 23 октября 2025
