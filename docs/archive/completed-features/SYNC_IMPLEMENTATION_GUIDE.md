# Bitrix ↔ Railway Синхронизация: Руководство по развертыванию

Это руководство описывает полную реализацию двусторонней синхронизации товаров и синхронизации статусов заказов между Production Bitrix и Railway backend.

---

## 📋 Что было реализовано

### ✅ Railway Backend (Этап 1)

**Файлы:**
- `/backend/models/orders.py` - Добавлено поле `bitrix_order_id`
- `/backend/migrations/add_bitrix_order_id.py` - Миграция для DB
- `/backend/api/webhooks.py` - Новый endpoint `POST /webhooks/order-status-sync`
- `/backend/services/bitrix_sync_service.py` - HTTP client для Bitrix
- `/backend/api/products/router.py` - Интеграция BitrixSyncService

**Функциональность:**
1. Webhook для приема обновлений статусов заказов из Bitrix
2. Автоматическое маппирование Bitrix статусов → Railway статусы
3. Сохранение истории изменений в `OrderHistory` таблице
4. HTTP client для отправки обновлений товаров в Bitrix
5. Интеграция с product update endpoints

### ✅ Bitrix Configuration (Этап 2-3)

**Файлы:**
- `/BITRIX_WEBHOOK_SETUP.md` - Инструкции по настройке webhook для статусов заказов
- `/BITRIX_PRODUCT_UPDATE_ENDPOINT.php` - PHP endpoint для приема обновлений товаров

---

## 🚀 Пошаговое развертывание

### Шаг 1: Развернуть Migration на Railway

```bash
cd /Users/alekenov/figma-product-catalog/backend

# Migration автоматически запустится при старте backend
# Если нужно запустить вручную:
python3 migrations/add_bitrix_order_id.py
```

### Шаг 2: Создать endpoint в Bitrix для приема товаров

```bash
# На Production Bitrix сервере:
mkdir -p /home/bitrix/www/api/v2/products/update-from-railway

# Скопировать PHP файл:
scp /Users/alekenov/figma-product-catalog/BITRIX_PRODUCT_UPDATE_ENDPOINT.php \
    root@185.125.90.141:/home/bitrix/www/api/v2/products/update-from-railway/index.php

# Или вручную создать файл с содержимым из BITRIX_PRODUCT_UPDATE_ENDPOINT.php
```

### Шаг 3: Настроить Webhook в Bitrix для статусов заказов

**Следуйте инструкциям в `/BITRIX_WEBHOOK_SETUP.md`:**

```bash
# 1. Получить WEBHOOK_SECRET из Railway:
railway variables --kv | grep WEBHOOK_SECRET

# 2. SSH в Bitrix сервер и отредактировать init.php:
ssh root@185.125.90.141

# 3. Следовать инструкциям в документе
```

### Шаг 4: Установить переменные окружения в Railway (если не установлены)

```bash
# Backend должен знать:
# - WEBHOOK_SECRET для аутентификации webhook'ов
# - RAILWAY_API_TOKEN для Bitrix

railway variables --set \
  WEBHOOK_SECRET="super-secret-key-12345" \
  RAILWAY_API_TOKEN="ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"
```

### Шаг 5: Развернуть обновленный код на Railway

```bash
cd /Users/alekenov/figma-product-catalog

# Commit изменений
git add -A
git commit -m "Implement Bitrix sync: orders status and products"

# Push на GitHub (Railway автоматически развернет)
git push origin main

# Или развернуть вручную:
railway deploy --ci
```

---

## 🧪 Тестирование

### Тест 1: Синхронизация статуса заказа (Bitrix → Railway)

**На Production Bitrix:**
1. Откройте заказ (например, #123456)
2. Измените статус: `Новый (N)` → `Принят (AP)`
3. Сохраните

**На Railway:**
```bash
# Проверьте логи
railway logs --deploy | grep "order-status-sync"

# Ожидаемый результат:
# INFO: Received order status webhook: order_id=123456, status=AP
# INFO: Updated order 789 (bitrix_id=123456): new → accepted
```

**Проверьте данные:**
```bash
# Get order
curl -H "Authorization: Bearer $TOKEN" \
  https://figma-product-catalog-production.up.railway.app/api/v1/orders/789

# Проверьте status: "accepted"

# Get history
curl -H "Authorization: Bearer $TOKEN" \
  https://figma-product-catalog-production.up.railway.app/api/v1/orders/789/history

# Должна быть запись с changed_by: "bitrix"
```

### Тест 2: Синхронизация товара (Railway → Bitrix)

**На Railway:**
```bash
# Обновить товар (например, цену)
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  https://figma-product-catalog-production.up.railway.app/api/v1/products/668826 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Эустомы (Updated)",
    "price": 500000,
    "enabled": true
  }'
```

**На Railway Logs:**
```bash
railway logs --deploy | grep "Synced product"

# Ожидаемый результат:
# INFO: Synced product 668826 to Bitrix
# ✅ Product 668826 synced to Bitrix
```

**На Production Bitrix:**
1. Откройте товар в Bitrix
2. Проверьте что цена обновилась на "5 000 ₸"
3. Проверьте что имя изменилось

### Тест 3: Webhook аутентификация

**Попытка отправить webhook с неверным secret:**
```bash
curl -X POST \
  https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/order-status-sync \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: wrong-secret" \
  -d '{
    "order_id": 123456,
    "status": "AP"
  }'

# Ожидаемый результат:
# HTTP 401 Unauthorized
# {"detail": "Invalid webhook secret"}
```

**С верным secret:**
```bash
WEBHOOK_SECRET=$(railway variables --kv | grep WEBHOOK_SECRET | cut -d= -f2)

curl -X POST \
  https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/order-status-sync \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: $WEBHOOK_SECRET" \
  -d '{
    "order_id": 123456,
    "status": "AP"
  }'

# Ожидаемый результат:
# HTTP 200 OK
# {"status": "success", ...}
```

---

## 📊 Маппинг статусов

Статусы автоматически конвертируются по таблице:

| Bitrix Code | Railway Enum | Описание |
|-------------|--------------|----------|
| N | NEW | Новый заказ |
| PD | PAID | Оплачен |
| AP | ACCEPTED | Принят флористом |
| CO | IN_PRODUCTION | В процессе сборки |
| DE | IN_DELIVERY | В доставке |
| F | DELIVERED | Доставлен |
| RF | CANCELLED | Возврат |
| UN | CANCELLED | Не реализован |

---

## 🔍 Мониторинг и отладка

### Логи Railway

```bash
# Все логи
railway logs --deploy

# Только ошибки
railway logs --deploy --filter "@level:error"

# Только webhook логи
railway logs --deploy | grep -i webhook

# Только product sync логи
railway logs --deploy | grep -i "product\|bitrix"
```

### Логи Bitrix

```bash
# SSH в сервер
ssh root@185.125.90.141

# Смотрите логи webhook
tail -f /home/bitrix/www/bitrix/logs/error_log | grep "Railway Webhook"

# Или поищите определенный заказ
grep "123456" /home/bitrix/www/bitrix/logs/error_log
```

### Проверить в Database

**Railway PostgreSQL:**
```bash
# Получить последние обновления заказов
SELECT * FROM "order"
WHERE bitrix_order_id IS NOT NULL
ORDER BY updated_at DESC
LIMIT 10;

# Получить историю изменений
SELECT * FROM order_history
WHERE changed_by = 'bitrix'
ORDER BY changed_at DESC
LIMIT 20;
```

---

## ⚠️ Обработка конфликтов

**Правило:** Bitrix данные всегда побеждают

**Сценарий:**
1. Товар изменили в Railway (цена = 5000₸)
2. Одновременно изменили в Bitrix (цена = 6000₸)
3. Railway отправляет 5000₸ → Bitrix
4. Bitrix webhook отправляет 6000₸ → Railway
5. **Результат:** 6000₸ везде (Bitrix победил)

**Реализация:**
- Не блокируем при конфликтах
- Просто применяем последнее изменение из Bitrix
- Логируем все конфликты в логи

---

## 🛠️ Troubleshooting

### Webhook не срабатывает из Bitrix

**Проверка 1: Event handler зарегистрирован?**
```bash
ssh root@185.125.90.141
grep -n "CvetyOrderStatusWebhook" /home/bitrix/www/local/php_interface/init.php
# Должна быть строка с регистрацией
```

**Проверка 2: WEBHOOK_SECRET совпадает?**
```bash
# На Railway
railway variables --kv | grep WEBHOOK_SECRET

# На Bitrix - должен совпадать в init.php
```

**Проверка 3: Логи Bitrix**
```bash
tail -f /home/bitrix/www/bitrix/logs/error_log
# Посмотрите ошибки типа "[Railway Webhook]"
```

### Товар не синхронизируется в Bitrix

**Проверка 1: Endpoint создан?**
```bash
curl -I -H "Authorization: Bearer {token}" \
  https://cvety.kz/api/v2/products/update-from-railway
# Должен вернуть 200 или 405 (если не PUT)
```

**Проверка 2: Логи Railway**
```bash
railway logs --deploy | grep "Bitrix\|product.*sync"
# Посмотрите ошибки синхронизации
```

**Проверка 3: Token верный?**
```bash
# Проверить RAILWAY_API_TOKEN в env
railway variables --kv | grep RAILWAY_API_TOKEN

# Должен совпадать с токеном в BITRIX_PRODUCT_UPDATE_ENDPOINT.php
```

### Order не найден при синхронизации статуса

**Причина:** `bitrix_order_id` не установлен при создании заказа

**Решение:**
```bash
# При создании заказа из Railway, убедитесь что вы сохраняете:
# bitrix_order_id = ID заказа, который вернул Bitrix

# Проверить в БД:
SELECT id, tracking_id, bitrix_order_id FROM "order" LIMIT 10;
# bitrix_order_id должны быть заполнены
```

---

## 📝 Чек-лист перед production

- [ ] Migration запущена и таблица обновлена (`bitrix_order_id` поле существует)
- [ ] Bitrix endpoint создан и доступен: `PUT /api/v2/products/update-from-railway`
- [ ] Event handler добавлен в `/home/bitrix/www/local/php_interface/init.php`
- [ ] WEBHOOK_SECRET установлен одинаково везде (Railway env и Bitrix code)
- [ ] RAILWAY_API_TOKEN установлен в Railway env
- [ ] Логирование включено на обеих сторонах
- [ ] Протестированы все три сценария (из чек-листа выше)
- [ ] Логи проверены на ошибки
- [ ] Готово к production!

---

## 📞 Контакты и ссылки

- **Railway Backend:** https://figma-product-catalog-production.up.railway.app
- **Production Bitrix:** https://cvety.kz
- **API Documentation:**
  - Webhook: `POST /api/v1/webhooks/order-status-sync`
  - Products: `PUT /api/v1/products/{id}`
  - Orders: `GET /api/v1/orders/{id}`

---

## 🎉 Success!

Когда все работает правильно, вы должны видеть:

**Railway Logs:**
```
✅ Received order status webhook: order_id=123456, status=AP
✅ Updated order 789 (bitrix_id=123456): new → accepted
✅ Synced product 668826 to Bitrix
```

**Bitrix Logs:**
```
[Railway Webhook] ✅ Order 123456 status synced: AP
[Railway Webhook] ✅ Product 668826 updated from Railway
```

Поздравляем! Синхронизация работает отлично! 🚀
