# Phone Number Migration Guide

## Проблема

После внедрения автоматической нормализации телефонных номеров в формат `+7XXXXXXXXXX`, существующие данные в БД могут содержать:
- Номера в старом формате (8XXXXXXXXXX, 7XXXXXXXXXX, без +)
- Потенциальные дубли, которые станут идентичными после нормализации

## Уникальные ограничения в БД

**Критичные таблицы с unique constraints:**

1. **User.phone** - глобально уникальное поле
   - Проблема: Пользователи с номерами `87015211545` и `+77015211545` после нормализации станут дублями
   - Location: `backend/models/users.py:95`

2. **Client (phone + shop_id)** - уникальность в рамках магазина
   - Проблема: В одном магазине могут быть клиенты с разными форматами одного номера
   - Location: `backend/models/users.py:62`

**Некритичные таблицы (нет unique constraints):**
- Order.phone, Order.recipient_phone, Order.sender_phone
- Shop.phone

## Решение: Миграционный скрипт

Создан скрипт `migrate_phone_numbers.py` который:
1. ✅ Анализирует потенциальные дубли после нормализации
2. ✅ Нормализует все телефонные номера в формат `+7XXXXXXXXXX`
3. ✅ Обрабатывает невалидные номера (пропускает с предупреждением)
4. ✅ Поддерживает dry-run режим для тестирования

## Использование

### Шаг 1: Анализ дублей (без изменений)

```bash
cd backend
python3 migrate_phone_numbers.py --analyze-only
```

**Что делает:**
- Проверяет User таблицу на дубли
- Проверяет Client таблицу на дубли в рамках магазинов
- Проверяет Order и Shop на невалидные номера
- НЕ вносит изменений

**Пример вывода:**
```
ANALYZING PHONE NUMBER DUPLICATES
==========================================

1. Checking User table (globally unique phone)...
   ❌ Found 2 duplicate phone numbers after normalization:
      +77015211545:
         - User #1 (Иван): 87015211545 → +77015211545
         - User #5 (Петр): +77015211545 → +77015211545

2. Checking Client table (unique per shop)...
   ✅ No duplicates found
```

### Шаг 2: Предпросмотр изменений (dry-run)

```bash
python3 migrate_phone_numbers.py --dry-run
```

**Что делает:**
- Показывает какие номера будут изменены
- Подсчитывает количество обновлений
- НЕ сохраняет изменения в БД

**Пример вывода:**
```
MIGRATION MODE - Dry Run
==========================================

1. Migrating User table...
   User #1 (Иван): 87015211545 → +77015211545
   User #3 (Мария): 7015211545 → +77015211545
   Updated 2 users

2. Migrating Client table...
   Client #10 (Shop 8): 8 701 521 15 45 → +77015211545
   Updated 1 clients

📋 Dry run complete. Would update 5 records total
```

### Шаг 3: Применение миграции

⚠️ **ВАЖНО:** Сначала убедитесь, что дублей нет!

```bash
python3 migrate_phone_numbers.py
```

**Что делает:**
- Нормализует все номера
- Сохраняет изменения в БД
- Делает COMMIT или ROLLBACK при ошибке

## Обработка дублей

Если скрипт находит дубли, миграция **останавливается** с сообщением:

```
⚠️  CRITICAL: Duplicate phone numbers found!

You must manually resolve these duplicates before running migration:
1. Decide which records to keep
2. Merge or delete duplicate records
3. Re-run this script
```

### Как решить проблему с дублями:

#### Вариант 1: Объединение записей (User)
```sql
-- Найти дубли
SELECT phone, COUNT(*) as count
FROM "user"
GROUP BY phone
HAVING COUNT(*) > 1;

-- Вручную решить какую запись оставить
-- Перенести связанные данные (orders, shop ownership)
-- Удалить дубликат
DELETE FROM "user" WHERE id = 123;
```

#### Вариант 2: Изменение номера (если это реально разные люди)
```sql
-- Если один номер принадлежит двум разным людям
UPDATE "user"
SET phone = '+77012345678'  -- Реальный номер второго человека
WHERE id = 123;
```

#### Вариант 3: Объединение клиентов (Client)
```sql
-- Найти дубли в рамках магазина
SELECT shop_id, phone, COUNT(*) as count
FROM client
GROUP BY shop_id, phone
HAVING COUNT(*) > 1;

-- Объединить заказы клиента в одну запись
-- Удалить дубликат
DELETE FROM client WHERE id = 456;
```

## Production Deployment

### Railway (Production)

```bash
# 1. Подключиться к production окружению
railway link

# 2. Запустить анализ
railway run python3 migrate_phone_numbers.py --analyze-only

# 3. Если дублей нет, запустить dry-run
railway run python3 migrate_phone_numbers.py --dry-run

# 4. Применить миграцию
railway run python3 migrate_phone_numbers.py
```

### Local Development

```bash
# 1. Убедиться что DATABASE_URL в .env
echo $DATABASE_URL

# 2. Запустить анализ
python3 migrate_phone_numbers.py --analyze-only

# 3. Применить миграцию
python3 migrate_phone_numbers.py
```

## После миграции

После успешной миграции:

1. ✅ Все номера в БД будут в формате `+7XXXXXXXXXX`
2. ✅ Новые записи будут автоматически нормализоваться (Pydantic validators)
3. ✅ API будет принимать любой формат, но сохранять только `+7XXXXXXXXXX`

## Валидация результатов

Проверить что миграция прошла успешно:

```sql
-- Проверить что все номера начинаются с +7
SELECT COUNT(*) as invalid_phones
FROM "user"
WHERE phone NOT LIKE '+7__________';

-- Должно быть 0
```

```sql
-- Проверить клиентов
SELECT COUNT(*) as invalid_phones
FROM client
WHERE phone NOT LIKE '+7__________';

-- Должно быть 0
```

## Rollback Plan

Если что-то пошло не так:

```bash
# Восстановить из backup
railway backup restore <backup-id>
```

Или вручную через SQL:
```sql
-- Откатить конкретные изменения (если есть backup таблицы)
UPDATE "user" u
SET phone = b.phone
FROM user_backup b
WHERE u.id = b.id;
```

## Checklist перед миграцией

- [ ] Создан backup базы данных
- [ ] Запущен `--analyze-only` и дублей нет
- [ ] Запущен `--dry-run` и результат проверен
- [ ] Команда уведомлена о downtime (если требуется)
- [ ] Подготовлен rollback plan

## Частые вопросы

**Q: Нужно ли останавливать сервис для миграции?**
A: Не обязательно, но рекомендуется для production. Скрипт быстрый (< 1 минуты для тысяч записей).

**Q: Что если в БД есть номера не из Казахстана?**
A: Скрипт пропустит их с предупреждением. Нужно будет обработать вручную.

**Q: Можно ли запустить миграцию несколько раз?**
A: Да, скрипт идемпотентный - повторный запуск не сломает данные.

## Контакты

При проблемах: создать issue в репозитории или связаться с командой.
