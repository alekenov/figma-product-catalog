# Figma Product Catalog

Каталог товаров для цветочного магазина с интеграцией Figma дизайна.

## 🚀 Быстрый старт

### Порты по умолчанию
- **Backend API**: http://localhost:8012
- **Frontend UI**: http://localhost:5176
- **API Documentation**: http://localhost:8012/docs

### Запуск проекта

#### Вариант 1: Один скрипт (рекомендуется)
```bash
./start.sh
```

#### Вариант 2: Раздельный запуск
В первом терминале:
```bash
./start-backend.sh
```

Во втором терминале:
```bash
./start-frontend.sh
```

#### Вариант 3: Ручной запуск
Backend:
```bash
cd backend
python3 main.py  # Запустится на порту 8012
```

Frontend:
```bash
npm run dev  # Запустится на порту 5176
```

## 📁 Структура проекта

```
figma-product-catalog/
├── backend/           # FastAPI backend (порт 8012)
│   ├── main.py       # Точка входа API
│   ├── models/       # SQLModel модели
│   └── api/          # API endpoints
├── src/              # React frontend (порт 5176)
│   ├── services/     # API клиент
│   └── components/   # React компоненты
├── start.sh          # Скрипт запуска всего проекта
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

Полная документация API доступна по адресу http://localhost:8012/docs после запуска backend.

## 🛠 Разработка

При изменении портов обновите:
1. `backend/main.py` - порт backend (строка 77)
2. `src/services/api.js` - URL backend (строка 2)
3. `vite.config.js` - порт frontend (строка 7)