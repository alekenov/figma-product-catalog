# Figma Product Catalog

Каталог товаров для цветочного магазина с интеграцией Figma дизайна.

## 🚀 Быстрый старт

### Порты по умолчанию
- **Backend API**: http://localhost:8014
- **Frontend UI**: http://localhost:5176
- **API Documentation**: http://localhost:8014/docs

### Запуск проекта

#### Вариант 1: Один скрипт (рекомендуется)
```bash
./scripts/start.sh
```

#### Вариант 2: Раздельный запуск
В первом терминале:
```bash
./scripts/start-backend.sh
```

Во втором терминале:
```bash
./scripts/start-frontend.sh
```

#### Вариант 3: Ручной запуск
Backend:
```bash
cd backend
python3 main.py  # Запустится на порту 8014
```

Frontend:
```bash
cd frontend
npm run dev  # Запустится на порту 5176
```

## 📁 Структура проекта

```
figma-product-catalog/
├── frontend/          # React frontend (порт 5176)
│   ├── src/          # React компоненты
│   ├── package.json  # Frontend зависимости
│   └── vite.config.js # Vite конфигурация
├── backend/           # FastAPI backend (порт 8014)
│   ├── main.py       # Точка входа API
│   ├── models/       # SQLModel модели
│   ├── api/          # API endpoints
│   └── requirements.txt # Backend зависимости
└── scripts/           # Скрипты для запуска
    ├── start.sh      # Скрипт запуска всего проекта
    ├── start-backend.sh  # Скрипт запуска backend
    └── start-frontend.sh # Скрипт запуска frontend
```

## 🔧 Технологии

**Backend:**
- FastAPI
- SQLModel + SQLite
- Python 3.9+

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router

## 📝 API Endpoints

- `GET /api/v1/products` - Список товаров
- `POST /api/v1/products` - Создание товара
- `GET /api/v1/orders` - Список заказов
- `POST /api/v1/orders` - Создание заказа

Полная документация API доступна по адресу http://localhost:8014/docs после запуска backend.

## 🛠 Разработка

При изменении портов обновите:
1. Переменные окружения в `.env` или `.env.local`:
   - `PORT` - порт backend (по умолчанию 8014)
   - `VITE_FRONTEND_PORT` - порт frontend (по умолчанию 5176)
   - `VITE_API_BASE_URL` - URL backend API
2. При необходимости прямого изменения:
   - `backend/config_sqlite.py` или `backend/config_render.py` - настройки backend
   - `frontend/src/services/api.js` - URL backend API
   - `frontend/vite.config.js` - порт frontend