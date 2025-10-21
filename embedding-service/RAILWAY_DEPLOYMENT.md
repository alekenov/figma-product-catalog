# Railway Deployment Guide - Embedding Service

Пошаговая инструкция по деплою Embedding Service на Railway через Dashboard.

---

## Шаг 1: Открыть Railway Project

1. Перейти на: https://railway.app/project/311bb135-7712-402e-aacf-14ce8b0b80df
2. Убедиться что видишь все существующие сервисы (telegram-bot, mcp-server, figma-product-catalog, Frontend, Postgres)

---

## Шаг 2: Создать новый Service

1. Нажать кнопку **"+ New"** в правом верхнем углу
2. Выбрать **"GitHub Repo"**
3. Выбрать репозиторий **`alekenov/figma-product-catalog`**
4. Railway автоматически обнаружит Nixpacks builder

---

## Шаг 3: Настроить Root Directory

1. В настройках нового сервиса перейти в **Settings** (шестеренка)
2. Найти секцию **"Build"**
3. В поле **"Root Directory"** указать: `/embedding-service`
4. Нажать **"Save"**

---

## Шаг 4: Настроить Environment Variables

1. Перейти в **Variables** (вкладка слева)
2. Нажать **"+ New Variable"**
3. Добавить следующие переменные:

### VERTEX_PROJECT_ID
```
VERTEX_PROJECT_ID=cvetykz
```

### VERTEX_LOCATION
```
VERTEX_LOCATION=europe-west4
```

### VERTEX_SERVICE_ACCOUNT_KEY
**ВАЖНО**: Вставить минифицированный JSON из буфера обмена (уже скопирован!)

```
VERTEX_SERVICE_ACCOUNT_KEY={"type":"service_account","project_id":"cvetykz",...}
```

Полное значение уже скопировано в буфер обмена - просто нажми **Cmd+V**!

### LOG_LEVEL
```
LOG_LEVEL=INFO
```

### ENV
```
ENV=production
```

4. Нажать **"Save"** после добавления всех переменных

---

## Шаг 5: Настроить Start Command (уже готов!)

Railway автоматически обнаружит `railway.json` в папке `embedding-service/`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "./start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Ничего не нужно менять - всё уже настроено! ✅

---

## Шаг 6: Генерировать Public Domain

1. Перейти в **Settings** → **Networking**
2. В секции **"Public Networking"** нажать **"Generate Domain"**
3. Railway создаст URL вида: `https://embedding-service-production-xxxx.up.railway.app`
4. **Скопировать этот URL** - он понадобится для backend!

---

## Шаг 7: Запустить Deploy

1. Вернуться в главный экран сервиса
2. Нажать **"Deploy"** (если не началось автоматически)
3. Дождаться успешного деплоя (~2-3 минуты)

---

## Шаг 8: Проверить логи

1. Открыть **Deployments** → Latest deployment
2. Перейти в **View Logs**
3. Искать строки:

```
✅ Embedding Service initialized (project: cvetykz, location: europe-west4)
Starting Embedding Service on port 8001
```

Если видишь эти строки - сервис успешно запустился! 🎉

---

## Шаг 9: Протестировать Health Check

Открыть в браузере или через curl:

```bash
curl https://embedding-service-production-xxxx.up.railway.app/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "service": "embedding-service",
  "vertex_ai_configured": true
}
```

---

## Шаг 10: Обновить Backend Service

1. Открыть сервис **figma-product-catalog** в Railway
2. Перейти в **Variables**
3. Найти или создать переменную `EMBEDDING_SERVICE_URL`
4. Установить значение: `https://embedding-service-production-xxxx.up.railway.app` (URL из шага 6)
5. Сохранить и **Redeploy** backend сервис

---

## Troubleshooting

### Ошибка: "Missing Vertex AI credentials"

**Причина**: VERTEX_SERVICE_ACCOUNT_KEY не установлен или некорректный

**Решение**:
1. Проверить что JSON минифицирован (без переносов строк внутри private_key)
2. Убедиться что вставлен полный JSON (начинается с `{"type":"service_account"` и заканчивается на `}`)

### Ошибка: "Failed to get access token: invalid_grant"

**Причина**: Service account не имеет прав на Vertex AI

**Решение**:
```bash
# В GCP Console добавить роль:
gcloud projects add-iam-policy-binding cvetykz \
  --member="serviceAccount:cloudflare-worker-visual-searc@cvetykz.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Ошибка: "Connection refused" при вызове из backend

**Причина**: Backend не может достучаться до Embedding Service

**Решение**:
1. Проверить что EMBEDDING_SERVICE_URL установлен в backend
2. Проверить что Public Domain сгенерирован в Embedding Service
3. Проверить что оба сервиса задеплоены

---

## Следующие шаги

После успешного деплоя:

1. ✅ Протестировать генерацию embeddings
2. ✅ Отправить тестовый webhook
3. ✅ Проверить что embedding сохранился в PostgreSQL
4. ✅ Запустить полный integration test

См. **INTEGRATION_TESTING.md** для деталей.

---

**Создано**: 2025-01-21
**Автор**: Cvety.kz Team
