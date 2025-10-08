# Быстрая инструкция: Миграция телефонных номеров

## TL;DR

```bash
# 1. Проверить дубли
railway run python3 migrate_phone_numbers.py --analyze-only

# 2. Если дублей нет - применить миграцию
railway run python3 migrate_phone_numbers.py

# 3. Проверить результат
railway run python3 -c "
from sqlmodel import Session, create_engine, select
from models.users import User
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with Session(engine) as s:
    users = s.exec(select(User)).all()
    print(f'✅ Всего пользователей: {len(users)}')
    print(f'✅ Примеры номеров: {[u.phone for u in users[:3]]}')
"
```

## Что делает миграция

- ✅ Нормализует все номера в `+7XXXXXXXXXX`
- ✅ Обрабатывает 4 таблицы: User, Client, Order, Shop
- ✅ Проверяет дубли перед миграцией
- ✅ Откатывает изменения при ошибках

## Если нашлись дубли

Вручную решить через SQL:

```sql
-- Найти дубли пользователей
SELECT
  REGEXP_REPLACE(phone, '[^0-9+]', '', 'g') as normalized,
  COUNT(*) as count,
  STRING_AGG(CAST(id AS TEXT), ', ') as ids
FROM "user"
GROUP BY normalized
HAVING COUNT(*) > 1;

-- Удалить дубликат (выбрать нужный ID)
DELETE FROM "user" WHERE id = 123;
```

Подробнее: см. `PHONE_MIGRATION_GUIDE.md`
