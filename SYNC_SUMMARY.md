# Синхронизация Bitrix ↔ Railway: Реализовано ✅

## Краткий обзор

Реализована полная синхронизация товаров и статусов заказов между Production Bitrix (shop_id=17008) и Railway backend (shop_id=8).

---

## 📦 Что было сделано

### Railway Backend (Python/FastAPI)

#### 1. Model Changes
```python
# /backend/models/orders.py
bitrix_order_id: Optional[int] = Field(default=None, index=True)
```
- Добавлено поле для связи с Bitrix заказами
- Миграция: `/backend/migrations/add_bitrix_order_id.py`

#### 2. Webhook для статусов заказов
```
POST /api/v1/webhooks/order-status-sync
Headers: X-Webhook-Secret: {token}

Body:
{
  "order_id": 123456,
  "status": "AP",
  "changed_by_id": 42,
  "notes": "..."
}
```

**Функциональность:**
- ✅ Маппирует Bitrix статусы → Railway OrderStatus enum
- ✅ Сохраняет историю изменений в `OrderHistory`
- ✅ Поддерживает все статусы: N, PD, AP, CO, DE, F, RF, UN

**Файл:** `/backend/api/webhooks.py` (новый endpoint)

#### 3. HTTP Client для Bitrix
```python
# /backend/services/bitrix_sync_service.py
BitrixSyncService:
  - sync_product_to_bitrix()
  - Отправляет обновления товаров в Bitrix via HTTP
```

**Поля для синхронизации:**
- name (название)
- price (цена в ₸)
- image (фото)
- enabled (доступность)
- description (описание)

#### 4. Интеграция в Product Updates
**Файл:** `/backend/api/products/router.py`

Добавлены вызовы `BitrixSyncService` в:
- `PUT /products/{id}` - обновление товара
- `PATCH /products/{id}/status` - включение/отключение товара

**Условие:** Синхронизация работает только для shop_id=17008 (Production)

---

### Bitrix Configuration (PHP)

#### 1. Webhook для статусов заказов
**Файл:** `BITRIX_WEBHOOK_SETUP.md` - подробные инструкции

Что нужно:
1. Добавить Event Handler в `/home/bitrix/www/local/php_interface/init.php`
2. Handler слушает событие `OnSaleStatusOrderChange`
3. При изменении статуса отправляет HTTP POST в Railway

**Пример:**
```php
EventManager::getInstance()->registerEventHandler(
    "sale",
    "OnSaleStatusOrderChange",
    "cvety_modules",
    "CvetyOrderStatusWebhook",
    "onOrderStatusChange"
);
```

#### 2. Endpoint для приема товаров
**Файл:** `BITRIX_PRODUCT_UPDATE_ENDPOINT.php`

Как использовать:
1. Скопировать в `/home/bitrix/www/api/v2/products/update-from-railway/index.php`
2. Railway отправляет: `PUT /api/v2/products/update-from-railway`
3. Bitrix получает и обновляет товар

---

## 🔄 Поток синхронизации

### Заказы: Bitrix → Railway (One-way)

```
Production Bitrix CRM
  ↓ (Флорист меняет статус)
Event Handler слышит OnSaleStatusOrderChange
  ↓
HTTP POST → Railway /webhooks/order-status-sync
  ↓
Railway получает и обновляет Order.status
  ↓
Сохраняет в OrderHistory (changed_by: "bitrix")
```

### Товары: Bidirectional

```
Production Bitrix                Railway Backend
     ↓                                ↓
Товар обновлен         Товар обновлен через API
     ↓                                ↓
Webhook: /product-sync  ← (уже работает)
     ↓                                ↓
Update Railway DB       Вызов BitrixSyncService
                               ↓
                        HTTP PUT → Bitrix API
                               ↓
                        Update Bitrix товар
```

---

## 📁 Новые/изменённые файлы

### Railway Backend
```
✅ backend/models/orders.py
   ├─ Добавлено: bitrix_order_id field

✅ backend/migrations/add_bitrix_order_id.py
   ├─ Новый файл: миграция БД

✅ backend/api/webhooks.py
   ├─ Добавлено: POST /webhooks/order-status-sync
   ├─ Добавлено: BX_TO_RAILWAY_STATUS маппинг
   ├─ Обновлено: импорты

✅ backend/services/bitrix_sync_service.py
   ├─ Новый файл: BitrixSyncService class
   ├─ Метод: sync_product_to_bitrix()
   ├─ HTTP client для Bitrix API

✅ backend/api/products/router.py
   ├─ Обновлено: update_product() - интеграция Bitrix sync
   ├─ Обновлено: toggle_product_status() - интеграция Bitrix sync
   ├─ Добавлено: импорты BitrixSyncService
```

### Bitrix Configuration
```
✅ BITRIX_WEBHOOK_SETUP.md
   ├─ Полные инструкции по настройке event handler
   ├─ Код для /local/php_interface/init.php
   ├─ Troubleshooting и отладка

✅ BITRIX_PRODUCT_UPDATE_ENDPOINT.php
   ├─ Полный код PHP endpoint
   ├─ Место: /api/v2/products/update-from-railway/index.php
   ├─ Аутентификация через Bearer token
```

### Documentation
```
✅ SYNC_IMPLEMENTATION_GUIDE.md
   ├─ Пошаговые инструкции развертывания
   ├─ 3 теста для проверки функциональности
   ├─ Маппинг статусов
   ├─ Troubleshooting гайд

✅ SYNC_SUMMARY.md
   ├─ Этот файл: краткий обзор
```

---

## 🧪 Тестирование

### Тест 1: Синхронизация статуса заказа
```bash
# На Bitrix: Измените статус заказа N → AP
# На Railway: Проверьте логи
railway logs --deploy | grep "order-status-sync"
```

### Тест 2: Синхронизация товара
```bash
# На Railway: Обновите товар
curl -X PUT https://.../api/v1/products/668826 \
  -d '{"price": 500000}'

# На Bitrix: Проверьте что цена обновилась
```

### Тест 3: Webhook аутентификация
```bash
# Должен вернуть 401 без secret
curl -X POST https://.../webhooks/order-status-sync
# 401 Unauthorized

# Должен вернуть 200 с верным secret
curl -X POST https://.../webhooks/order-status-sync \
  -H "X-Webhook-Secret: $WEBHOOK_SECRET"
# 200 OK
```

---

## 🚀 Развертывание

### Быстрый старт (5 шагов)

1. **Развернуть код на Railway**
   ```bash
   git add -A && git commit -m "Implement Bitrix sync"
   git push origin main
   # или: railway deploy --ci
   ```

2. **Запустить миграцию**
   - Автоматически при старте backend
   - Или: `python3 migrations/add_bitrix_order_id.py`

3. **Создать Bitrix endpoint**
   ```bash
   scp BITRIX_PRODUCT_UPDATE_ENDPOINT.php \
       root@185.125.90.141:/api/v2/products/update-from-railway/
   ```

4. **Настроить webhook в Bitrix**
   - Следовать `BITRIX_WEBHOOK_SETUP.md`
   - Добавить event handler в init.php

5. **Протестировать**
   - Выполнить все 3 теста из `SYNC_IMPLEMENTATION_GUIDE.md`

**Подробные инструкции:** см. `SYNC_IMPLEMENTATION_GUIDE.md`

---

## ✨ Ключевые особенности

✅ **Безопасность**
- Webhook аутентификация через X-Webhook-Secret
- Bearer token для Bitrix API
- Обработка исключений везде

✅ **Надежность**
- Не блокируем запросы если sync падает
- Все логируется для отладки
- Idempotent операции (можно пересланать без дубликатов)

✅ **Масштабируемость**
- Работает только для shop_id=17008 (Production)
- Легко добавить еще shops в будущем
- Асинхронный HTTP client

✅ **Отладка**
- Подробные логи с emoji для легкого чтения
- Маппинг статусов четкий и видимый
- Все webhook запросы логируются

---

## 📊 Маппинг статусов

| Bitrix | Railway | Описание |
|--------|---------|----------|
| N | NEW | Новый заказ |
| PD | PAID | Оплачен |
| AP | ACCEPTED | Принят флористом |
| CO | IN_PRODUCTION | Собран |
| DE | IN_DELIVERY | В доставке |
| F | DELIVERED | Доставлен |
| RF | CANCELLED | Возврат |
| UN | CANCELLED | Не реализован |

---

## 🎯 Результат

После развертывания:

1. **При изменении статуса в Bitrix** → автоматически обновляется в Railway
2. **При изменении товара в Railway** → автоматически обновляется в Bitrix
3. **История всех изменений** → сохраняется в OrderHistory для аудита
4. **Конфликты** → Bitrix данные всегда побеждают (как требовали)

---

## 🔗 Дальнейшее развитие

### Уже реализовано
- ✅ Двусторонняя синхронизация товаров
- ✅ Односторонняя синхронизация статусов заказов (Bitrix → Railway)
- ✅ История изменений
- ✅ Аутентификация и безопасность

### Опционально в будущем
- ⏳ Двусторонняя синхронизация статусов (если нужно)
- ⏳ Синхронизация клиентов
- ⏳ Синхронизация инвентаря
- ⏳ Полная миграция с Bitrix (если потребуется)

---

## 📞 Поддержка

**Если что-то не работает:**
1. Посмотрите `SYNC_IMPLEMENTATION_GUIDE.md` → Troubleshooting
2. Проверьте логи Railway: `railway logs --deploy`
3. Проверьте логи Bitrix: `/home/bitrix/www/bitrix/logs/error_log`
4. Убедитесь что все токены совпадают: `railway variables --kv`

---

## ✅ Чек-лист Production

- [ ] Migration запущена
- [ ] Bitrix endpoint создан
- [ ] Event handler добавлен в init.php
- [ ] Токены установлены верно
- [ ] Все 3 теста пройдены
- [ ] Логи проверены на ошибки
- [ ] Готово! 🚀

---

**Дата реализации:** 24 октября 2025
**Статус:** ✅ Готово к production
**Тестирование:** ⏳ Нужно выполнить перед deploys
