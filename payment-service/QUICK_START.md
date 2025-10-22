# Payment Service - Quick Start (5 минут)

## ✅ Код уже в GitHub: commit `f85ee17`

---

## 🚀 Создание через Railway Web UI (самый простой способ)

### 1. Откройте Railway Project
https://railway.app/project/positive-exploration

### 2. Создайте Payment Service

```
1. Нажмите [+ New] в правом верхнем углу
2. Выберите "GitHub Repo"
3. Select: alekenov/figma-product-catalog
4. Configure Service:
   ✓ Root Directory: payment-service
   ✓ Service Name: payment-service
5. Click "Deploy"
```

Railway автоматически:
- Обнаружит `railway.json` и `requirements.txt`
- Установит Python dependencies
- Запустит `uvicorn main:app`

### 3. Добавьте PostgreSQL (в том же проекте)

```
1. Нажмите [+ New]
2. Выберите "Database" → "PostgreSQL"
3. Railway автоматически создаст $DATABASE_URL
```

### 4. Настройте Environment Variables

В payment-service → Settings → Variables → Raw Editor:

```env
PRODUCTION_API_URL=https://cvety.kz/api/v2/paymentkaspi
KASPI_ACCESS_TOKEN=<нужно получить>
CORS_ORIGINS=https://frontend-production-6869.up.railway.app,http://localhost:5176
DEBUG=False
```

**KASPI_ACCESS_TOKEN получить:**
```bash
# Вариант 1: Из production сервера
ssh root@185.125.90.141 "grep KASPI_ACCESS backend/.env"

# Вариант 2: Из backend config
cat /Users/alekenov/figma-product-catalog/backend/config.py | grep kaspi_access_token
```

### 5. Подождите Deploy (~2-3 минуты)

Проверьте Build Logs:
```
Installing packages...
✓ fastapi
✓ uvicorn
✓ sqlmodel
...
Starting server on port 8015
✅ Database tables created
🚀 Payment Service starting...
```

### 6. Seed Database

**Option A: Railway Web Terminal**
```
1. В Railway dashboard → payment-service
2. Click "Shell" (иконка терминала)
3. Run:
   python seed_data.py seed
   python seed_data.py list
```

**Option B: Railway CLI** (из локальной машины)
```bash
cd /Users/alekenov/figma-product-catalog/payment-service
railway link  # выбрать positive-exploration → payment-service
railway run python seed_data.py seed
railway run python seed_data.py list
```

### 7. Verify Deployment ✅

```bash
# Получить URL сервиса
# Railway dashboard → payment-service → Settings → Public Domain
# Или:
railway domain

# Health check
curl https://payment-service-production.up.railway.app/health

# Должен вернуть:
{
  "status": "ok",
  "service": "payment-service",
  "version": "1.0.0"
}

# List configs
curl https://payment-service-production.up.railway.app/admin/configs

# Должен вернуть 8 БИН configurations
```

---

## 🧪 Test Payment Creation

```bash
# Create test payment for shop_id=8
curl -X POST https://payment-service-production.up.railway.app/payments/kaspi/create \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 8,
    "amount": 100,
    "phone": "77015211545",
    "message": "Test payment from payment-service"
  }'

# Expected response:
{
  "success": true,
  "external_id": "12345678901",
  "status": "Wait",
  "organization_bin": "891027350515"
}
```

---

## 📊 Monitoring

### View Logs
```bash
# Railway Web UI
Dashboard → payment-service → Deployments → View Logs

# Railway CLI
railway logs --deploy
railway logs --build
```

### View Metrics
```
Dashboard → payment-service → Metrics
- CPU usage
- Memory usage
- Request count
- Response times
```

---

## 🔥 Что дальше?

После успешного деплоя payment-service:

1. ✅ Интегрировать с main backend
   - Создать `PaymentServiceClient` в backend
   - Модифицировать `create_order()` для использования payment-service

2. ✅ Создать Admin UI
   - CRUD для payment_config
   - Просмотр payment_log
   - Статистика по БИН

3. ✅ Тестирование
   - Создать заказы с разными shop_id
   - Проверить что используется правильный БИН
   - Тест refund операций

---

## 🆘 Troubleshooting

### Build fails
**Check:** `railway logs --build`
**Common issues:**
- Missing dependencies in requirements.txt
- Python version mismatch
- Syntax errors

**Fix:** Update code → `git push` → Railway auto-redeploys

### Database connection error
**Check:** Environment variables
```bash
railway variables --kv | grep DATABASE_URL
```

**Fix:** Ensure PostgreSQL plugin is added to project

### KASPI_ACCESS_TOKEN error
**Check:** Variable is set
```bash
railway variables --kv | grep KASPI_ACCESS_TOKEN
```

**Fix:** Set variable in Railway UI or:
```bash
railway variables --set KASPI_ACCESS_TOKEN="<token>"
```

---

## 📱 Quick Access Links

- **Railway Project**: https://railway.app/project/positive-exploration
- **GitHub Repo**: https://github.com/alekenov/figma-product-catalog/tree/main/payment-service
- **API Docs** (after deploy): `https://<service-url>/docs`

---

## ⏱️ Time Estimate

- Create service: 1 min
- Add PostgreSQL: 30 sec
- Set variables: 1 min
- Deploy wait: 2-3 min
- Seed database: 30 sec
- Verify: 1 min

**Total: ~5-7 minutes** ⚡
