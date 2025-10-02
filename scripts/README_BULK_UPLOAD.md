# 🌸 Bulk Upload Products - Инструкция

## Быстрый старт

### Шаг 1: Запустите backend

```bash
cd /Users/alekenov/figma-product-catalog/backend
python3 main.py
```

Дождитесь сообщения:
```
INFO:     Uvicorn running on http://0.0.0.0:8014
```

### Шаг 2: Запустите скрипт загрузки

В **новом терминале**:

```bash
cd /Users/alekenov/figma-product-catalog
python3 scripts/bulk_upload_products.py
```

---

## Что делает скрипт?

1. ✅ Загружает `products_data.json` с данными 10 букетов
2. ✅ Проверяет подключение к backend API
3. ✅ Для каждого букета:
   - Загружает фото в Cloudflare R2
   - Создает товар через API `/products`
   - Логирует результат
4. ✅ Выводит финальную статистику

---

## Структура данных

### products_data.json

Содержит 10 букетов с полными данными:

```json
{
  "filename": "2025-10-02 12.02.45.jpg",
  "name": "Нежная романтика",
  "price": 1300000,  // в копейках (13,000₸)
  "description": "...",
  "type": "flowers",
  "composition": [...],
  "colors": ["pink", "green"],
  "occasions": ["romantic", "birthday"],
  "cities": ["almaty", "astana"],
  "tags": ["roses", "premium"],
  "manufacturing_time": 30,
  "shelf_life": 7,
  "enabled": true,
  "is_featured": true
}
```

---

## Пример вывода

```
🌸 Bulk Upload Products to Cvety.kz
==================================================

📂 Загружаю данные из products_data.json...
   ✓ Найдено 10 букетов

🔍 Проверяю подключение к backend...
   ✓ Backend доступен: http://localhost:8014/api/v1

📸 Букет 1/10: Нежная романтика
   Цена: 13 000₸
   ⬆️  Загружаю фото в R2...
   ✓ Фото загружено: https://r2.cvety.kz/products/...
   📝 Создаю товар в каталоге...
   ✅ Товар создан! ID: 15

📸 Букет 2/10: Яркая осенняя композиция
   Цена: 17 000₸
   ⬆️  Загружаю фото в R2...
   ✓ Фото загружено: https://r2.cvety.kz/products/...
   📝 Создаю товар в каталоге...
   ✅ Товар создан! ID: 16

...

==================================================
📊 Результаты загрузки:

   ✅ Успешно: 9
   ❌ Ошибки: 0
   ⏭️  Пропущено: 1

🎉 Загрузка завершена!
```

---

## Возможные проблемы

### ❌ Backend недоступен

```
❌ Backend недоступен! Убедитесь что он запущен на http://localhost:8014/api/v1
   Запустите: cd backend && python3 main.py
```

**Решение:** Запустите backend в отдельном терминале.

### ❌ Фото не найдено

```
❌ Фото не найдено: /Users/alekenov/Downloads/demo/2025-10-02 12.02.45.jpg
```

**Решение:** Проверьте путь к фото в переменной `PHOTOS_DIR` в скрипте.

### ⚠️ Image upload failed: HTTP 404

**Решение:** Проверьте что endpoint `/upload/image` существует в backend API.

---

## Настройка

### Изменить API URL

В файле `bulk_upload_products.py`:

```python
API_BASE_URL = "http://localhost:8014/api/v1"  # Локальный
# или
API_BASE_URL = "https://api.cvety.kz/api/v1"  # Production
```

### Изменить путь к фото

```python
PHOTOS_DIR = "/Users/alekenov/Downloads/demo"
```

---

## После загрузки

1. Откройте админ-панель: http://localhost:5176
2. Войдите как Director (`+77015211545` / `password`)
3. Перейдите в Product Catalog
4. Проверьте загруженные товары

---

## Дополнительно

### Загрузить только 1 букет (для теста)

Отредактируйте `products_data.json` - оставьте только один объект в массиве.

### Добавить новые букеты

1. Добавьте фото в `/Users/alekenov/Downloads/demo/`
2. Добавьте данные в `products_data.json`
3. Запустите скрипт снова

---

## Что дальше?

После успешной загрузки:
- ✅ Проверьте товары в админке
- ✅ Подкорректируйте цены если нужно
- ✅ Добавьте дополнительные фото (через админку)
- ✅ Настройте featured products для главной страницы
