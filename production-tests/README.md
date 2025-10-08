# Production CRM Testing

Автоматизированные E2E тесты для проверки всех функций CRM на продакшене после деплоя.

## Структура

```
production-tests/
├── scenarios/                      # YAML test scenarios
│   ├── 01_auth_registration.yaml   # Регистрация и авторизация
│   ├── 02_product_management.yaml  # CRUD товаров
│   ├── 03_order_creation.yaml      # Создание и управление заказами
│   ├── 04_warehouse_operations.yaml # Складские операции
│   ├── 05_client_management.yaml   # Управление клиентами
│   └── 06_profile_updates.yaml     # Обновление профиля и настроек
├── reports/                        # Test results (auto-generated)
├── test_production.py              # Test runner
├── config_production.py            # Configuration
└── README.md                       # This file
```

## Установка

```bash
cd production-tests
pip install -r requirements.txt
```

## Использование

### Запустить все тесты

```bash
python test_production.py --all
```

### Запустить с подробным выводом

```bash
python test_production.py --all --verbose
```

### Запустить конкретный сценарий

```bash
python test_production.py --scenario 01_auth_registration.yaml
```

### Указать другой URL (например, staging)

```bash
python test_production.py --all --url https://staging.example.com/api/v1
```

## Тестовые сценарии

### 01. Authentication & Registration
- ✅ Регистрация нового менеджера
- ✅ Авторизация по phone + password
- ✅ Получение данных пользователя (/auth/me)
- ✅ Проверка валидности токена
- ✅ Refresh token

### 02. Product Management
- ✅ Список товаров (public + admin)
- ✅ Создание товара (букет)
- ✅ Получение товара по ID
- ✅ Обновление товара (цена, описание)
- ✅ Включение/выключение товара
- ✅ Удаление товара

### 03. Order Creation & Management
- ✅ Получение списка товаров для заказа
- ✅ Создание заказа с доставкой
- ✅ Создание заказа с самовывозом
- ✅ Список всех заказов
- ✅ Детали заказа
- ✅ Обновление статуса заказа
- ✅ Трекинг по tracking_id (public)
- ✅ Трекинг по телефону (public)

### 04. Warehouse Operations
- ✅ Список складских позиций
- ✅ Добавление stock
- ✅ История операций
- ✅ Список рецептов
- ✅ Статус inventory check
- ✅ Статистика склада

### 05. Client Management
- ✅ Список клиентов
- ✅ Детали клиента + статистика
- ✅ Обновление заметок
- ✅ Поиск по телефону
- ✅ Dashboard статистика
- ✅ Синхронизация telegram клиентов

### 06. Profile & Shop Settings
- ✅ Получение профиля пользователя
- ✅ Обновление профиля
- ✅ Настройки магазина (public)
- ✅ Рабочие часы
- ✅ FAQ (public)
- ✅ Отзывы (public)
- ✅ Обновление настроек магазина (admin)

## Конфигурация

Настройки в `config_production.py`:

```python
# Production URL
BASE_URL = "https://figma-product-catalog-production.up.railway.app/api/v1"

# Test credentials
TEST_USER_PHONE = "77001234567"
TEST_USER_PASSWORD = "TestPass123!"

# Timeout settings
REQUEST_TIMEOUT = 30
TEST_TIMEOUT = 180

# Skip specific tests
SKIP_TESTS = []  # e.g., ["06_profile_updates.yaml"]
```

## Формат YAML сценариев

```yaml
name: "Test Scenario Name"
description: "What this test does"

environment:
  base_url: "https://..."
  shop_id: 8
  test_var: "value"

test_steps:
  - name: "Step description"
    endpoint: "/path/{{variable}}"
    method: "POST"
    headers:
      Authorization: "Bearer {{token}}"
    body:
      field: "value"
    query_params:
      limit: 10
    assertions:
      - status_code: 200
      - response.field: exists
      - response: is_array
    save:
      variable_name: "response.field"
    optional: false  # true to allow failure

success_criteria:
  - feature_works: true
```

## Переменные в YAML

- `{{variable}}` - замена из context
- `{{timestamp}}` - текущее время ISO format
- Переменные сохраняются через `save:` блок
- Переменные доступны в следующих шагах

## Assertions

- `status_code: 200` - точное совпадение
- `status_code: [200, 201]` - один из списка
- `response.field: exists` - поле существует
- `response: is_array` - ответ является массивом

## Reports

После каждого запуска создается JSON отчет:

```
reports/production_test_20251008_143022.json
```

Содержит:
- Timestamp
- Summary (общая статистика)
- Детали по каждому сценарию
- Passed/failed steps

## Exit Codes

- `0` - все тесты прошли
- `1` - есть упавшие тесты

## CI/CD Integration

Можно использовать в GitHub Actions после деплоя:

```yaml
- name: Run production tests
  run: |
    cd production-tests
    python test_production.py --all
```

## Troubleshooting

### Timeout errors
Увеличить `REQUEST_TIMEOUT` в config_production.py

### Authentication failures
Проверить credentials в config_production.py

### Отсутствуют тестовые данные
Некоторые тесты требуют наличия товаров/клиентов в базе

## Безопасность

⚠️ Не коммитить `config_production.py` с реальными паролями в git!

Использовать environment variables:

```bash
export PROD_TEST_PASSWORD="secret"
python test_production.py --all
```

## Roadmap

- [ ] HTML reports
- [ ] Slack notifications on failure
- [ ] Performance metrics collection
- [ ] Screenshot capture on failure
- [ ] Parallel test execution
