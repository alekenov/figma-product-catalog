# План рефакторинга архитектуры проекта

**Дата создания**: 23 октября 2025
**Статус**: Утверждено к выполнению
**Приоритет**: Высокий

---

## Резюме аудита

Проведен комплексный архитектурный аудит проекта. Выявлено:
- **8 критических проблем** (требуют немедленного решения)
- **12 проблем высокой важности** (решить в течение 2-3 недель)
- **15 проблем средней важности** (решить в течение месяца)
- **35 файлов превышают лимиты** (19 backend >300 строк, 10 frontend >200 строк)
- **517 строк устаревшего кода** в worker файлах
- **60 Python файлов** в корне backend (должно быть <20)

---

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ (Week 1)

### 1. Удалить устаревшие worker файлы ❌ DELETE
**Файлы**:
```
backend/worker.py           (147 строк)
backend/worker_d1.py        (295 строк)
backend/worker_fixed.py     (50 строк)
backend/worker_simple.py    (25 строк)
```

**Причина удаления**:
- Не используются нигде в коде (проверено grep)
- Устаревший экспериментальный код Cloudflare Workers
- Загромождают backend директорию

**Действие**:
```bash
git rm backend/worker*.py
git commit -m "Remove obsolete Cloudflare Worker experiments"
```

**Время**: 5 минут
**Риск**: Нулевой (файлы не импортируются)

---

### 2. Удалить дублирующий availability_service.py ❌ DELETE
**Файл**: `backend/availability_service.py` (316 строк)

**Причина удаления**:
- Полностью дублирует функциональность `services/inventory_service.py`
- Идентичные методы: `get_reserved_quantities()`, `calculate_available_quantity()`
- Используется только в комментарии inventory_service.py как "consolidated FROM..."
- Старая версия, которую забыли удалить

**Действие**:
```bash
git rm backend/availability_service.py
git commit -m "Remove duplicate availability_service (consolidated into inventory_service)"
```

**Время**: 5 минут
**Риск**: Нулевой (не импортируется)

---

### 3. Разделить монолитный orders/router.py 🔧 SPLIT
**Файл**: `backend/api/orders/router.py` (1558 строк, 26+ endpoints)

**Проблема**:
- Все операции с заказами в одном файле
- Сложно найти нужный endpoint
- Нарушает принцип единственной ответственности

**Решение**: Разделить на 5 файлов по функциональности

**Новая структура**:
```
backend/api/orders/
├── __init__.py              # Re-export всех роутов
├── crud.py                  # GET, POST, PUT, DELETE заказов (200 строк)
├── status.py                # Управление статусами (150 строк)
├── availability.py          # Проверки доступности, резервирование (200 строк)
├── photos.py                # Загрузка фото, feedback (250 строк)
├── assignments.py           # Назначение ответственных, курьеров (150 строк)
└── tracking.py              # Публичное отслеживание (100 строк)
```

**План миграции**:
1. Создать новые файлы
2. Перенести группы endpoints с зависимостями
3. Обновить импорты в main.py
4. Протестировать все endpoints
5. Удалить старый router.py

**Время**: 3-4 часа
**Риск**: Средний (требует тестирования)

---

### 4. Разделить монолитный frontend/services/api.js 🔧 SPLIT
**Файл**: `frontend/src/services/api.js` (1239 строк)

**Проблема**:
- Все API операции в одном файле
- Сложно навигироваться
- Дублирование паттернов

**Решение**: Разделить на 6 файлов по доменам

**Новая структура**:
```
frontend/src/services/
├── api-client.js           # Базовый fetch, auth handling (150 строк)
├── products-api.js         # Products API (200 строк)
├── orders-api.js           # Orders API (250 строк)
├── clients-api.js          # Clients API (150 строк)
├── warehouse-api.js        # Warehouse API (200 строк)
├── payments-api.js         # Kaspi Pay API (150 строк)
└── index.js                # Re-export всех API
```

**План миграции**:
1. Создать api-client.js с базовой логикой
2. Извлечь каждый домен в отдельный файл
3. Обновить импорты в компонентах
4. Протестировать UI

**Время**: 2-3 часа
**Риск**: Средний (много импортов)

---

### 5. Декомпозировать OrderDetail.jsx компонент 🔧 SPLIT
**Файл**: `frontend/src/OrderDetail.jsx` (1267 строк, 20+ useState)

**Проблема**:
- Слишком много ответственности в одном компоненте
- 20+ переменных состояния
- Сложно поддерживать

**Решение**: Разделить на 5+ компонентов

**Новая структура**:
```
frontend/src/components/orders/
├── OrderDetail.jsx          # Главный компонент-оркестратор (200 строк)
├── OrderInfo.jsx            # Информация о заказе (150 строк)
├── OrderStatus.jsx          # Управление статусом (150 строк)
├── OrderItems.jsx           # Список товаров в заказе (150 строк)
├── OrderPhotos.jsx          # Галерея фото (200 строк)
├── OrderHistory.jsx         # История изменений (150 строк)
└── OrderAssignments.jsx     # Назначения ответственных (150 строк)
```

**Использовать**:
- Custom hooks: `useOrderData()`, `useOrderPhotos()`, `useOrderStatus()`
- Context API для избежания prop drilling

**Время**: 4-5 часов
**Риск**: Средний

---

### 6. Декомпозировать Profile.jsx компонент 🔧 SPLIT
**Файл**: `frontend/src/Profile.jsx` (1088 строк)

**Проблема**:
- Смешивает профиль, платежи, настройки

**Решение**: Разделить на 3 компонента

**Новая структура**:
```
frontend/src/components/profile/
├── Profile.jsx              # Главный компонент с табами (150 строк)
├── ProfileInfo.jsx          # Информация профиля (250 строк)
├── PaymentSettings.jsx      # Настройки платежей (400 строк)
└── ShopSettings.jsx         # Настройки магазина (250 строк)
```

**Время**: 2-3 часа
**Риск**: Низкий

---

## 🟡 ВЫСОКАЯ ВАЖНОСТЬ (Week 2-3)

### 7. Объединить config_render.py + config_sqlite.py 🔧 MERGE
**Файлы**:
- `backend/config_render.py` (160 строк)
- `backend/config_sqlite.py` (150 строк)

**Проблема**:
- 80% дублирование кода
- Условный импорт в main.py (if DATABASE_URL...)
- Сложно тестировать

**Решение**: Единый config.py с автоопределением

**Новый config.py**:
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Автоопределение БД
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./test.db"
    )

    # Остальные настройки
    SECRET_KEY: str
    # ...

settings = Settings()
```

**Обновить main.py**:
```python
# Было:
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings

# Стало:
from config import settings
```

**Время**: 1 час
**Риск**: Низкий (проверить оба окружения)

---

### 8. Организовать backend директорию 📁 ORGANIZE
**Проблема**: 60 файлов в корне backend/

**Решение**: Создать поддиректории

**Создать структуру**:
```bash
mkdir -p backend/scripts backend/migrations
```

**Переместить файлы**:
```
backend/scripts/          # Утилиты и скрипты
├── analyze_shops.py
├── check_*.py (6 файлов)
├── create_test_*.py (2 файла)
├── delete_product*.py (2 файла)
├── fix_*.py (2 файла)
├── init_*.py (2 файла)
├── cleanup_expired_reservations.py
└── manual_check_and_refund.py

backend/migrations/       # Миграции данных
├── migrate_phone_numbers.py
├── migrate_sqlite_to_postgresql.py
├── migrate_product_images.py
├── migrate_sync.py
├── migrate_phase1.py
├── export_to_postgres.py
└── import_to_render.py
```

**Скрипт миграции**:
```bash
# Создать директории
mkdir -p backend/scripts backend/migrations

# Переместить скрипты
mv backend/{analyze_shops,check_*,create_test_*,delete_product*,fix_*,init_*,cleanup_*,manual_*}.py backend/scripts/

# Переместить миграции
mv backend/migrate_*.py backend/migrations/
mv backend/{export_to_postgres,import_to_render}.py backend/migrations/

git add backend/scripts backend/migrations
git commit -m "Organize backend scripts and migrations into subdirectories"
```

**Время**: 30 минут
**Риск**: Минимальный (обновить документацию)

---

### 9. Организовать frontend компоненты 📁 ORGANIZE
**Проблема**: 26 компонентов в плоской структуре

**Решение**: Группировка по функциональности

**Новая структура**:
```
frontend/src/components/
├── forms/                # Формы
│   ├── AddProduct.jsx
│   ├── EditProduct.jsx
│   ├── CreateOrder.jsx
│   └── CreateOrderCustomer.jsx
├── orders/               # Заказы
│   ├── OrderDetail/
│   ├── Orders.jsx
│   └── OrdersAdmin.jsx
├── products/             # Продукты
│   ├── ProductCatalog.jsx
│   ├── ProductDetail.jsx
│   └── ReadyProducts.jsx
├── warehouse/            # Склад
│   ├── WarehouseItemDetail.jsx
│   └── WarehouseOperations.jsx
├── clients/              # Клиенты
│   ├── ClientsList.jsx
│   └── ClientDetail.jsx
├── layout/               # Layout компоненты
│   ├── BottomNavBar.jsx
│   └── Toast.jsx
├── common/               # Переиспользуемые
│   ├── ToggleSwitch.jsx
│   └── Button.jsx
└── superadmin/           # Суперадмин
    └── ...
```

**Время**: 1-2 часа (переименование + обновление импортов)
**Риск**: Низкий (автоматизировать через IDE)

---

### 10. Извлечь custom hooks для форм 🎣 EXTRACT HOOKS
**Проблема**: Дублирование логики форм

**Файлы**:
- AddProduct.jsx / EditProduct.jsx - дублируют логику продуктов
- CreateOrder.jsx / CreateOrderCustomer.jsx - дублируют логику заказов

**Решение**: Создать переиспользуемые hooks

**Новые hooks**:
```
frontend/src/hooks/
├── useFormData.js        # Базовый hook для форм
├── useProductForm.js     # Логика форм продуктов
├── useOrderForm.js       # Логика форм заказов
└── useImageUpload.js     # Логика загрузки изображений
```

**Пример useProductForm.js**:
```javascript
export function useProductForm(initialData = null) {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    type: '',
    price: 0,
    photos: [],
    // ...
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validate = () => {
    // Общая валидация
  };

  const submit = async () => {
    // Общая отправка
  };

  return { formData, handleChange, validate, submit };
}
```

**Время**: 3-4 часа
**Риск**: Средний (тестирование)

---

### 11. Стандартизировать state management 🎯 STANDARDIZE
**Проблема**: Смешанные паттерны useState vs Context

**Рекомендация**: Выбрать единый подход

**Option A: useReducer для сложных компонентов** ⭐ (Рекомендуется)
```javascript
// Вместо 20+ useState
const [state, dispatch] = useReducer(orderReducer, initialState);

// Actions
dispatch({ type: 'SET_ORDER_DATA', payload: data });
dispatch({ type: 'UPDATE_STATUS', payload: newStatus });
```

**Option B: Context API для глобального состояния**
```javascript
// shop/ уже использует OrderFormContext
// Можно расширить на frontend/
```

**Действие**:
1. Выбрать паттерн (useReducer рекомендуется)
2. Обновить OrderDetail.jsx как пример
3. Применить к Profile.jsx
4. Документировать в CLAUDE.md

**Время**: 2-3 часа на компонент
**Риск**: Средний

---

## 🟢 СРЕДНЯЯ ВАЖНОСТЬ (Week 4+)

### 12. Разделить большие backend файлы 📄
**Цель**: Привести к лимиту 300 строк

**Файлы для разделения**:
- `services/inventory_service.py` (935 → 3 файла по 300)
- `api/superadmin.py` (848 → 3 файла)
- `services/order_service.py` (655 → 2 файла)
- `api/warehouse.py` (569 → 2 файла)
- `api/products/router.py` (548 → 2 файла)

**Время**: По 1-2 часа на файл

---

### 13. Удалить hardcoded Figma URLs ❌
**Файл**: `frontend/src/OrderDetail.jsx` (строки 11-14)

**Действие**:
```javascript
// Удалить строки 11-14
// const figmaUrl1 = "https://figma.com/..."
// const figmaUrl2 = "https://figma.com/..."
// ...
```

**Время**: 2 минуты
**Риск**: Нулевой

---

### 14. Улучшить структуру models/__init__.py 📦
**Файл**: `backend/models/__init__.py` (419 строк)

**Проблема**: 100+ re-exports создают путаницу

**Решение**: Добавить комментарии и группировку
```python
# Products domain
from .products import Product, ProductColor, ProductTag

# Orders domain
from .orders import Order, OrderItem, OrderStatusHistory

# Warehouse domain
from .warehouse import WarehouseItem, WarehouseOperation
# ...
```

**Время**: 30 минут
**Риск**: Нулевой

---

### 15. Разделить models/shop.py 📄
**Файл**: `backend/models/shop.py` (436 строк)

**Решение**: Разделить на 2 файла
```
models/
├── shop_models.py          # Shop, WorkingHours
└── shop_settings.py        # ShopSettings, PaymentConfig
```

**Время**: 1 час
**Риск**: Низкий (обновить импорты)

---

### 16. Создать README для scripts/ 📚
**Цель**: Документировать утилиты

**Создать**: `backend/scripts/README.md`
```markdown
# Backend Scripts

## Database Utilities
- `check_production_db.py` - Проверка production БД
- `analyze_shops.py` - Анализ магазинов

## Testing Utilities
- `create_test_user.py` - Создание тестовых пользователей
- `create_test_product.py` - Создание тестовых продуктов

## Maintenance
- `cleanup_expired_reservations.py` - Очистка истекших резервов
- `fix_admin_password.py` - Сброс пароля админа

...
```

**Время**: 30 минут
**Риск**: Нулевой

---

### 17. Переименовать компоненты для консистентности 🏷️
**Проблема**: Несогласованные имена

**Текущие проблемы**:
- ProductCatalog.jsx vs ProductCatalogFixed.jsx (почему "Fixed"?)
- Orders.jsx vs OrdersAdmin.jsx (путаница)

**Решение**: Единый паттерн
```
OrdersPage.jsx          # Список заказов
OrderDetailPage.jsx     # Детали заказа
ProductsPage.jsx        # Каталог продуктов
ProductDetailPage.jsx   # Детали продукта
```

**Время**: 1 час
**Риск**: Низкий

---

### 18. Переместить тесты в отдельную директорию 🧪
**Проблема**: .test.jsx файлы смешаны с компонентами

**Текущее**:
```
src/
├── Orders.jsx
├── Orders.test.jsx        ❌ Смешано
├── ClientsList.jsx
└── ClientsList.test.jsx   ❌ Смешано
```

**Решение**:
```
frontend/
├── src/
│   └── components/
└── tests/                  ✅ Отдельно
    ├── Orders.test.jsx
    └── ClientsList.test.jsx
```

**Время**: 15 минут
**Риск**: Минимальный (обновить vite.config.js)

---

## 📊 Метрики успеха

### До рефакторинга
- 35 файлов >лимита
- 60 файлов в backend root
- 517 строк мертвого кода
- 2 монолитных компонента >1000 строк
- 1 монолитный router >1500 строк

### После рефакторинга (цель)
- 0 файлов >лимита
- <20 файлов в backend root
- 0 строк мертвого кода
- Все компоненты <300 строк
- Все роутеры <300 строк

---

## 🗓️ График выполнения

### Week 1: Критические (Items 1-6)
- День 1: Удаление (items 1-2) - 10 минут
- День 2-3: Разделение orders/router.py (item 3) - 4 часа
- День 4: Разделение api.js (item 4) - 3 часа
- День 5: Разделение OrderDetail.jsx (item 5) - 5 часов

### Week 2-3: Высокие (Items 7-11)
- Week 2: Организация структуры (items 7-9) - 4 часа
- Week 3: Hooks и стандартизация (items 10-11) - 8 часов

### Week 4+: Средние (Items 12-18)
- Постепенная реализация по необходимости

---

## ⚠️ Риски и митигация

### Риск 1: Сломать импорты при разделении файлов
**Митигация**:
- Использовать IDE для автоматического обновления импортов
- Тестировать после каждого изменения
- Коммитить небольшими порциями

### Риск 2: Регрессия функциональности
**Митигация**:
- Запускать `./quick_test.sh` после каждого изменения backend
- Тестировать UI вручную после изменений frontend
- Использовать Git для быстрого отката

### Риск 3: Долгое время выполнения
**Митигация**:
- Фокус на критических items сначала
- Делать по 1-2 items в день
- Не браться за все сразу

---

## 📝 Чеклист выполнения

### Критические ✅
- [ ] Удалить worker*.py файлы
- [ ] Удалить availability_service.py
- [ ] Разделить orders/router.py
- [ ] Разделить services/api.js
- [ ] Разделить OrderDetail.jsx
- [ ] Разделить Profile.jsx

### Высокие ⚡
- [ ] Объединить config файлы
- [ ] Организовать backend директорию
- [ ] Организовать frontend компоненты
- [ ] Создать custom hooks
- [ ] Стандартизировать state management

### Средние 📌
- [ ] Разделить большие backend файлы
- [ ] Удалить Figma URLs
- [ ] Улучшить models/__init__.py
- [ ] Разделить models/shop.py
- [ ] Создать scripts/README.md
- [ ] Переименовать компоненты
- [ ] Переместить тесты

---

## 🎯 Следующие шаги

1. **Прочитать этот план полностью**
2. **Начать с items 1-2** (10 минут, нулевой риск)
3. **Создать feature branch**: `git checkout -b refactor/cleanup-obsolete-files`
4. **Выполнять по одному item за раз**
5. **Коммитить после каждого завершенного item**
6. **Повторный аудит через месяц**

---

## 📚 Полезные ссылки

- Полный отчет аудита: `/tmp/audit_report.md`
- Краткая сводка: `/tmp/AUDIT_SUMMARY.txt`
- Текущий CLAUDE.md: `/Users/alekenov/figma-product-catalog/CLAUDE.md`

---

**Версия документа**: 1.0
**Последнее обновление**: 23 октября 2025
**Автор**: Claude Code Architecture Audit
