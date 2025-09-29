# Figma Product Catalog Backend

FastAPI + SQLModel backend for Kazakhstan flower shop catalog.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Database (Docker)

```bash
docker-compose up -d
```

This starts PostgreSQL on port 5432 and Redis on port 6379.

### 3. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Seed Database

```bash
python seed_data.py
```

### 5. Start API Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### Products

- `GET /api/v1/products/` - List products with filtering
- `GET /api/v1/products/{id}` - Get single product
- `POST /api/v1/products/` - Create product
- `PUT /api/v1/products/{id}` - Update product
- `PATCH /api/v1/products/{id}/status` - Toggle enabled/disabled
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/search/suggestions` - Search autocomplete
- `GET /api/v1/products/stats/summary` - Product statistics

### Orders

- `GET /api/v1/orders/` - List orders with filtering
- `GET /api/v1/orders/{id}` - Get single order
- `POST /api/v1/orders/` - Create order
- `PUT /api/v1/orders/{id}` - Update order
- `PATCH /api/v1/orders/{id}/status` - Update order status
- `POST /api/v1/orders/{id}/items` - Add item to order
- `DELETE /api/v1/orders/{id}` - Delete order
- `GET /api/v1/orders/stats/dashboard` - Order statistics

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 🏗️ Architecture

### Models (SQLModel)

- **Product**: Main product catalog
- **Order**: Customer orders
- **OrderItem**: Items within orders

### Key Features

- **SQLModel Integration**: Single model definition for DB and API
- **Async Operations**: Full async/await support with asyncpg
- **Automatic Validation**: Pydantic validation on all endpoints
- **Filtering & Search**: Advanced product and order filtering
- **CORS Support**: Frontend integration ready
- **Auto-generated Docs**: OpenAPI/Swagger documentation

### Database Schema

```
products
├── id (primary key)
├── name, price, type
├── description, image_url
├── manufacturing_time, dimensions
├── enabled, is_featured
├── colors, occasions, cities (JSON arrays)
└── created_at, updated_at

orders
├── id (primary key)
├── order_number (unique)
├── customer info (name, phone, email)
├── delivery info (address, date, notes)
├── financial (subtotal, delivery_cost, total)
├── status, notes
└── created_at, updated_at

order_items
├── id (primary key)
├── order_id, product_id (foreign keys)
├── product snapshot (name, price at time of order)
├── quantity, item_total
└── special_requests
```

## 🛠️ Development

### Database Migration

The app automatically creates tables on startup. For production, use proper migrations:

```bash
# Future: Alembic integration
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/figma_catalog

# Application
SECRET_KEY=your-secret-key
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🎯 Frontend Integration

The API is designed to work with the React frontend in `../frontend/src/`. Key integration points:

### Products Integration

```javascript
// Get products with filtering (ProductCatalogFixed.jsx)
fetch('/api/v1/products/?type=flowers&enabled_only=true')

// Toggle product status (ToggleSwitch.jsx)
fetch('/api/v1/products/1/status', {
  method: 'PATCH',
  body: JSON.stringify({enabled: true})
})

// Create product (AddProduct.jsx)
fetch('/api/v1/products/', {
  method: 'POST',
  body: JSON.stringify(productData)
})
```

### Orders Integration

```javascript
// Get orders (Orders.jsx, OrdersAdmin.jsx)
fetch('/api/v1/orders/?status=pending')

// Create order
fetch('/api/v1/orders/', {
  method: 'POST',
  body: JSON.stringify(orderData)
})

// Update order status (admin)
fetch('/api/v1/orders/1/status', {
  method: 'PATCH',
  body: JSON.stringify({status: 'accepted'})
})
```

## 🚨 Production Considerations

- [ ] Add authentication/authorization
- [ ] Implement proper error handling and logging
- [ ] Add rate limiting
- [ ] Setup database migrations
- [ ] Add monitoring and health checks
- [ ] Implement caching with Redis
- [ ] Add file upload for product images
- [ ] Setup CI/CD pipeline

## 📈 Next Steps

1. **Authentication**: Integrate Supabase Auth
2. **File Upload**: Image management for products
3. **Real-time Updates**: WebSocket for order status
4. **Payment Integration**: Kaspi Pay for Kazakhstan
5. **Notifications**: SMS/Email for order updates
6. **Analytics**: Advanced reporting and insights