# CRM Bitrix - Управление заказами и товарами

CRM админка для управления production данными из cvety.kz через Bitrix API v2. Деплоится на Cloudflare Workers.

## ✨ Возможности

- 📦 **Управление заказами**: просмотр списка, детали, смена статуса
- 🛍️ **Управление товарами**: просмотр каталога, создание, редактирование товаров
- 🚀 **Production API**: прямое подключение к cvety.kz/api/v2/
- ☁️ **Cloudflare Workers**: глобальное распределение, высокая скорость
- 📱 **Responsive**: работает на всех устройствах
- 🎨 **Tailwind CSS**: современный UI

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Установить зависимости
npm install

# Запустить dev сервер (порт 5177)
npm run dev

# Open http://localhost:5177
```

### Production Build

```bash
# Собрать для production
npm run build

# Проверить build локально
npm run preview
```

## 📁 Структура проекта

```
crm-bitrix/
├── src/
│   ├── pages/
│   │   ├── OrdersAdmin.jsx      # Список заказов
│   │   ├── OrderDetail.jsx      # Детали заказа + смена статуса
│   │   ├── ProductCatalog.jsx   # Каталог товаров
│   │   └── ProductDetail.jsx    # Детали товара
│   ├── services/
│   │   ├── bitrix-client.js     # HTTP клиент для Bitrix API
│   │   ├── bitrix-adapters.js   # Преобразование данных v2 → v1
│   │   ├── orders-api.js        # API методы для заказов
│   │   └── products-api.js      # API методы для товаров
│   ├── components/              # UI компоненты
│   │   ├── LoadingSpinner.jsx
│   │   ├── Toast.jsx
│   │   ├── StatusBadge.jsx
│   │   └── PriceFormatter.jsx
│   ├── App.jsx                  # Главный компонент с роутингом
│   ├── main.jsx                 # React entry point
│   └── index.css                # Tailwind стили
├── public/
│   └── index.html               # HTML template
├── package.json
├── vite.config.js
├── tailwind.config.js
├── wrangler.toml                # Cloudflare Workers config
├── .env.development             # Dev переменные окружения
└── .env.production              # Production переменные окружения
```

## 🔌 Bitrix API Интеграция

### Endpoints

**Orders:**
- `GET /orders/` - список заказов
- `GET /orders/{id}/` - детали заказа
- `PATCH /orders/{id}/status/` - смена статуса

**Products:**
- `GET /products/` - список товаров
- `GET /products/{id}/` - детали товара
- `POST /products/` - создание товара
- `PUT /products/{id}/` - обновление товара
- `DELETE /products/{id}/` - удаление товара

### Data Adapters

Данные из v2 API преобразуются в унифицированный формат:

**Orders:**
- `number` → `order_number`
- `status_key` → `status` (с маппингом: accepted → ACCEPTED)
- `paymentAmount` ("6 450 ₸") → `total_price` (645000 kopecks)

**Products:**
- `title` → `name`
- `price` ("15 000 ₸") → `price` (1500000 kopecks)
- `isAvailable` → `enabled`
- `createdAt` → `created_at`

### Environment Variables

**`.env.development`:**
```
VITE_CRM_PORT=5177
VITE_BITRIX_API_URL=https://cvety.kz/api/v2
VITE_BITRIX_TOKEN=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144
```

**`.env.production`:**
```
VITE_BITRIX_API_URL=https://cvety.kz/api/v2
VITE_BITRIX_TOKEN=ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144
```

## 🛠️ Технологический стек

- **Frontend**: React 18.2 + React Router 7.9
- **Styling**: Tailwind CSS 3.4
- **Icons**: Lucide React
- **Build Tool**: Vite 6.3
- **Deployment**: Cloudflare Workers
- **Package Manager**: npm

## 📊 Доступные статусы заказов

| Статус | Русский | Код |
|--------|---------|-----|
| NEW | Новый | `NEW` |
| ACCEPTED | Принят | `ACCEPTED` |
| IN_PRODUCTION | В производстве | `IN_PRODUCTION` |
| IN_DELIVERY | В доставке | `IN_DELIVERY` |
| DELIVERED | Доставлен | `DELIVERED` |
| CANCELLED | Отменен | `CANCELLED` |

## 🚀 Деплой на Cloudflare Workers

### Требования

- Cloudflare аккаунт
- Wrangler CLI установлен

### Деплой

```bash
# Собрать project
npm run build

# Деплоить на Cloudflare Workers
npx wrangler deploy

# Или через npm скрипт
npm run deploy
```

После деплоя приложение будет доступно на:
- Production: `https://crm-bitrix.workers.dev`
- Custom domain (если настроен)

## 🔐 Безопасность

⚠️ **Важно**: Bitrix API token хранится в .env файлах.

**Production checklist:**
- ✅ Никогда не коммитьте `.env.production` с реальным токеном в Git
- ✅ Используйте Cloudflare Wrangler secrets для хранения токенов
- ✅ Ограничьте доступ по IP адресам если возможно
- ✅ Регулярно ротируйте токены

### Использование Wrangler Secrets

```bash
# Установить secret
wrangler secret put BITRIX_TOKEN

# Использовать в коде
const token = env.BITRIX_TOKEN;
```

## 🐛 Troubleshooting

### Проблема: "Bitrix API error: 401"

**Решение**: Проверьте что VITE_BITRIX_TOKEN в .env файлах установлен правильно

### Проблема: "CORS error"

**Решение**: Убедитесь что запросы идут напрямую на cvety.kz/api/v2/ (CORS настроена на сервере)

### Проблема: Пусто товары/заказы

**Решение**: Проверьте сетевой запрос в DevTools -> Network, убедитесь что API возвращает 200 и данные

## 📝 Логирование

```javascript
// В bitrix-client.js
console.error(`Bitrix API Error [${endpoint}]:`, error);
```

Все ошибки логируются в браузерную консоль. Для production используйте Sentry или аналогичный сервис.

## 🔄 API Response Format

Bitrix v2 API возвращает:

```json
{
  "success": true,
  "data": [
    { /* объекты */ }
  ],
  "pagination": {
    "total": 33,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

Все методы автоматически проверяют `success` флаг и обрабатывают ошибки.

## 📚 Дополнительные ресурсы

- [Bitrix API Documentation](https://bitrix.info)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [React Router Docs](https://reactrouter.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/)

## 📞 Поддержка

Проблемы или вопросы? Свяжитесь с разработчиком.

---

**Создано**: 2025-10-23
**Версия**: 1.0.0
**API Version**: v2
