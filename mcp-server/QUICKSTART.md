# MCP Server Quick Start

## ⚡ Быстрый старт

### 1. Установка

```bash
cd mcp-server
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Запуск

```bash
# Способ 1: Скрипт
./start.sh

# Способ 2: Напрямую
.venv/bin/python server.py

# Способ 3: С MCP Inspector (рекомендуется для тестирования)
.venv/bin/python -m fastmcp dev server.py
```

### 3. Проверка

```bash
.venv/bin/python test_server.py
```

## 🔧 Настройка окружения

```bash
# В .env файле или экспорт переменных:
export API_BASE_URL="http://localhost:8014/api/v1"
export DEFAULT_SHOP_ID="8"
```

## 📚 Доступные инструменты (15)

### Аутентификация
- `login(phone, password)` - Вход в систему
- `get_current_user(token)` - Получить текущего пользователя

### Продукты
- `list_products(...)` - Список товаров с фильтрами
- `get_product(product_id)` - Детали товара
- `create_product(token, ...)` - Создать товар (admin)
- `update_product(token, product_id, ...)` - Обновить товар (admin)

### Заказы
- `list_orders(token, ...)` - Список заказов (admin)
- `get_order(token, order_id)` - Детали заказа (admin)
- `create_order(...)` - Создать заказ (public)
- `update_order_status(token, order_id, status)` - Обновить статус (admin)
- `track_order(tracking_id)` - Отследить заказ (public)

### Склад
- `list_warehouse_items(token, ...)` - Список складских позиций (admin)
- `add_warehouse_stock(token, warehouse_item_id, quantity)` - Добавить товар на склад (admin)

### Настройки магазина
- `get_shop_settings(token)` - Получить настройки (admin)
- `update_shop_settings(token, ...)` - Обновить настройки (admin)

## 💡 Примеры использования

### Пример 1: Аутентификация и получение товаров

```python
# 1. Войти в систему
result = await login(phone="77015211545", password="yourpass")
token = result["access_token"]

# 2. Получить список товаров
products = await list_products(shop_id=8, enabled_only=True, limit=10)
```

### Пример 2: Создание заказа

```python
order = await create_order(
    customer_name="Иван Иванов",
    customer_phone="77011234567",
    delivery_address="ул. Абая 1",
    delivery_date="2025-10-10",
    delivery_time="14:00",
    shop_id=8,
    items=[{"product_id": 1, "quantity": 2, "price": 5000}],
    total_price=10000
)

# Сохранить tracking_id для отслеживания
tracking_id = order["tracking_id"]
```

### Пример 3: Отслеживание заказа (public endpoint)

```python
status = await track_order(tracking_id="ORD-12345-ABCDE")
print(status)  # {"status": "processing", "customer_name": "...", ...}
```

## 🔗 Интеграция с Claude Code

### Добавление через CLI

```bash
claude mcp add flower-shop \
  --transport stdio \
  "/Users/alekenov/figma-product-catalog/mcp-server/.venv/bin/python /Users/alekenov/figma-product-catalog/mcp-server/server.py"
```

### Или через конфигурацию

Добавить в `~/.config/claude/mcp_config.json`:

```json
{
  "mcpServers": {
    "flower-shop": {
      "transport": "stdio",
      "command": "/Users/alekenov/figma-product-catalog/mcp-server/.venv/bin/python",
      "args": ["/Users/alekenov/figma-product-catalog/mcp-server/server.py"],
      "env": {
        "API_BASE_URL": "http://localhost:8014/api/v1",
        "DEFAULT_SHOP_ID": "8"
      }
    }
  }
}
```

## 🐛 Решение проблем

### Ошибка: Python версии < 3.10

```bash
# Используйте Python 3.10+
python3.12 -m venv .venv
```

### Ошибка: Backend недоступен

```bash
# Убедитесь, что backend запущен
cd ../backend
python3 main.py  # Должен быть на порту 8014
```

### Ошибка: 401 Unauthorized

```bash
# Проверьте токен и credentials
# Используйте правильный phone и password при login
```

## 📖 Дополнительная документация

- Полная документация: `README.md`
- Примеры API: `../backend/test_api_endpoints.sh`
- Swagger UI: http://localhost:8014/docs (когда backend запущен)
