# Database Migrations

Эта директория содержит одноразовые скрипты для миграции данных между окружениями и форматами.

⚠️ **ВАЖНО**: Эти скрипты предназначены для единоразового выполнения и не должны запускаться повторно на одних и тех же данных.

---

## 📦 SQLite → PostgreSQL Migration

### `migrate_sqlite_to_postgresql.py`
**Назначение**: Полная миграция из локального SQLite в production PostgreSQL.

**Что делает**:
- Экспортирует все таблицы из SQLite
- Конвертирует типы данных SQLite → PostgreSQL
- Импортирует в PostgreSQL на Railway
- Сохраняет ID и relationships

**Использование**:
```bash
# 1. Backup production БД
pg_dump $DATABASE_URL > backup.sql

# 2. Запустить миграцию
python3 migrations/migrate_sqlite_to_postgresql.py

# 3. Проверить данные
python3 scripts/check_production_db.py
```

**Статус**: ✅ Выполнена (дата: ~2025-08)

---

## 🔄 Phased Migrations

### `migrate_phase1.py`
**Назначение**: Поэтапная миграция больших таблиц (часть 1).

**Мигрирует**:
- Products (1-1000)
- Orders (1-500)
- Users (все)

**Использование**:
```bash
python3 migrations/migrate_phase1.py
```

**Примечание**: Используется для тестирования процесса миграции на подмножестве данных.

**Статус**: ✅ Выполнена

---

## 🔢 Data Sync & Export

### `migrate_sync.py`
**Назначение**: Синхронизация данных между development и production.

**Функции**:
- Двунаправленная синхронизация
- Разрешение конфликтов по timestamp
- Dry-run mode для проверки

**Использование**:
```bash
# Dry run (только показать изменения)
python3 migrations/migrate_sync.py --dry-run

# Реальная синхронизация
python3 migrations/migrate_sync.py --from-dev-to-prod
```

**Статус**: 🔄 Может использоваться периодически

---

### `export_to_postgres.py`
**Назначение**: Экспорт конкретных таблиц в PostgreSQL.

**Использование**:
```bash
# Экспорт всех таблиц
python3 migrations/export_to_postgres.py --all

# Экспорт конкретных таблиц
python3 migrations/export_to_postgres.py --tables products,orders
```

**Статус**: ✅ Выполнена

---

### `import_to_render.py`
**Назначение**: Импорт данных в Render PostgreSQL (старый хостинг).

**Примечание**: Render был заменен на Railway. Скрипт оставлен для истории.

**Статус**: ⚠️ Устарел (Render → Railway)

---

## 📞 Specialized Migrations

### `migrate_phone_numbers.py`
**Назначение**: Нормализация форматов телефонных номеров.

**Что делает**:
- Конвертирует +77088888888 → 77088888888
- Удаляет пробелы и дефисы
- Валидирует казахстанские номера (+7 7XX)

**Затронутые таблицы**:
- `user` (phone)
- `order` (customer_phone, recipient_phone, sender_phone)
- `telegram_client` (phone)

**Использование**:
```bash
python3 migrations/migrate_phone_numbers.py
```

**Статус**: ✅ Выполнена (дата: 2025-09)

---

### `migrate_product_images.py`
**Назначение**: Миграция изображений продуктов в Cloudflare R2.

**Что делает**:
1. Загружает старые изображения (Figma/локальные пути)
2. Загружает в Cloudflare R2 Storage
3. Обновляет `product.image` и `productimage.url`
4. Сохраняет mapping старых → новых URL

**Использование**:
```bash
# С подтверждением на каждый upload
python3 migrations/migrate_product_images.py

# Batch режим
python3 migrations/migrate_product_images.py --batch
```

**Статус**: ✅ Выполнена (дата: 2025-09)

---

## 🔒 Safety Guidelines

### Перед выполнением миграции:

1. **Backup БД**:
   ```bash
   # PostgreSQL
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

   # SQLite
   cp figma_catalog.db figma_catalog_backup_$(date +%Y%m%d).db
   ```

2. **Проверить зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Тестировать на копии данных**:
   - Создать test database
   - Запустить миграцию на test
   - Проверить целостность

4. **Dry-run где возможно**:
   ```bash
   python3 migrations/script.py --dry-run
   ```

### После выполнения миграции:

1. **Проверить количество записей**:
   ```sql
   SELECT COUNT(*) FROM products;
   SELECT COUNT(*) FROM orders;
   ```

2. **Проверить целостность**:
   ```bash
   python3 scripts/check_production_db.py
   ```

3. **Протестировать API**:
   ```bash
   cd backend
   ./quick_test.sh
   ```

---

## 📊 Migration Log

| Дата | Миграция | Статус | Записей | Примечания |
|------|----------|--------|---------|------------|
| 2025-08-15 | SQLite → PostgreSQL | ✅ Успешно | ~500 products, ~200 orders | Начальная миграция |
| 2025-09-01 | Phone normalization | ✅ Успешно | 850 records updated | Убрали +7 префикс |
| 2025-09-10 | Product images → R2 | ✅ Успешно | 450 images uploaded | Cloudflare R2 |

---

## 🛠️ Troubleshooting

### Ошибка: "relation already exists"
**Решение**: БД уже содержит таблицы. Проверить, нужна ли миграция.

### Ошибка: "phone format invalid"
**Решение**: Запустить `migrate_phone_numbers.py` для нормализации.

### Ошибка: "foreign key constraint"
**Решение**: Мигрировать таблицы в правильном порядке (users → products → orders).

---

## 📝 Adding New Migration

При создании новой миграции:

1. **Имя файла**: `migrate_<description>.py` (например, `migrate_add_shop_settings.py`)

2. **Структура**:
   ```python
   """
   Migration: <Описание>
   Date: YYYY-MM-DD
   Author: <Имя>

   Changes:
   - <Изменение 1>
   - <Изменение 2>
   """

   def migrate():
       # Основная логика
       pass

   def rollback():
       # Откат изменений
       pass

   if __name__ == "__main__":
       migrate()
   ```

3. **Обновить этот README** с описанием новой миграции

4. **Добавить в Migration Log** после выполнения

---

**Последнее обновление**: 23 октября 2025
