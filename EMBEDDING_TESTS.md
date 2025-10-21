# 🧪 Тесты Embedding System

## ✅ Что работает сейчас:

1. **Embedding Service** - Микросервис для генерации 512D векторов через Vertex AI
2. **PostgreSQL + pgvector** - База данных с расширением для vector similarity search
3. **Webhook Integration** - Автоматическая генерация embeddings при создании/обновлении продуктов
4. **Background Tasks** - Асинхронная обработка без блокировки HTTP запросов

---

## 🧪 Готовые тесты:

### 1. Проверка Embedding Service

```bash
./test_embedding_service.sh
```

**Что тестирует:**
- Генерация embedding для изображения (1.2 секунды)
- Health check сервиса
- Статистика запросов
- Сохраненные embeddings в базе

**Ожидаемый результат:**
```json
{
  "success": true,
  "dimensions": 512,
  "model": "vertex-multimodal-001",
  "duration_ms": 1227
}
```

---

### 2. Webhook Integration Test

```bash
./test_webhook_integration.sh
```

**Что тестирует:**
- Webhook с int значениями (price, height, width)
- Создание/обновление продукта
- Автоматическая генерация embedding
- Сохранение в PostgreSQL

**Ожидаемый результат:**
```json
{
  "status": "success",
  "action": "updated",
  "product_id": 999888,
  "reindex_triggered": true,
  "embedding_generated": true
}
```

---

### 3. Проверка базы данных

```bash
PGPASSWORD=ua4k2kfhzypqpqlolvtsfx382w4ravqw psql \
  -h maglev.proxy.rlwy.net -p 49800 -U postgres -d railway \
  -c "SELECT product_id, embedding_type, vector_dims(embedding) as dims, created_at
      FROM product_embeddings
      ORDER BY created_at DESC
      LIMIT 10;"
```

**Что проверяет:**
- Таблица `product_embeddings` создана
- Embeddings сохраняются с корректными размерностями (512D)
- pgvector extension работает

---

## 🔄 Полный Integration Test Flow:

```
1. Webhook от Production Bitrix
   POST /api/v1/webhooks/product-sync
   ↓
2. Backend создает/обновляет продукт
   ↓
3. Background Task запускается
   ↓
4. Embedding Service:
   - Скачивает изображение
   - Отправляет в Vertex AI
   - Возвращает 512D вектор
   ↓
5. Backend сохраняет embedding в PostgreSQL
   INSERT INTO product_embeddings (product_id, embedding, ...)
   ↓
6. ✅ Готово для similarity search!
```

---

## 📊 Текущая статистика:

- **Total requests**: 3
- **Successful**: 2 (66.7%)
- **Failed**: 1 (33.3% - из-за невалидного URL)
- **Average duration**: 1523ms (~1.5 секунды)
- **Embeddings в базе**: 1 продукт (999888)

---

## 🎯 Следующий шаг: Visual Search Endpoint

Нужно создать endpoint для поиска похожих продуктов:

```
POST /api/v1/products/search/similar
{
  "image_url": "https://...",
  "shop_id": 8,
  "limit": 5
}

→ Returns top 5 similar products using cosine distance
```

**SQL Query для similarity search:**
```sql
SELECT
  p.id,
  p.name,
  p.image,
  1 - (pe.embedding <=> :query_vector) AS similarity
FROM products p
JOIN product_embeddings pe ON p.id = pe.product_id
WHERE p.shop_id = :shop_id
  AND p.enabled = true
ORDER BY pe.embedding <=> :query_vector ASC
LIMIT :limit;
```

---

## 📝 Исправленные баги:

1. ✅ **Type guards** - `parse_price()` и `parse_dimension()` теперь принимают int и string
2. ✅ **Redirect following** - httpx теперь следует 301 редиректам от cvety.kz
3. ✅ **pgvector extension** - Используется Railway template `pgvector-pg17`
4. ✅ **Migration order** - `run_migrations()` вызывается ПЕРЕД `create_db_and_tables()`

---

## 🚀 Production URLs:

- **Backend**: https://figma-product-catalog-production.up.railway.app
- **Embedding Service**: https://embedding-service-production-4aaa.up.railway.app
- **Database**: pgvector.railway.internal:5432

---

## 🔐 Секреты:

- `WEBHOOK_SECRET`: cvety-webhook-2025-secure-key
- `DATABASE_URL`: postgresql://postgres:ua4k2kfhzypqpqlolvtsfx382w4ravqw@...
- `VERTEX_PROJECT_ID`: cvetykz
- `VERTEX_LOCATION`: europe-west4
