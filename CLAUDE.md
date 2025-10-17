# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start (Recommended)
- `./scripts/start.sh` - Start both frontend and backend
- `./scripts/start-frontend.sh` - Start admin frontend only
- `./scripts/start-backend.sh` - Start backend only
- `./scripts/start-shop.sh` - Start customer-facing shop (port 5180)

### Shop Development (from shop/ directory) - Customer-Facing
- `npm run dev` - Start development server on port 5180
- `npm run build` - Build production bundle
- `npm run preview` - Preview production build locally
- **Note**: Modern storefront with Radix UI components

### Frontend Development (from frontend/ directory) - Admin Panel
- `npm run dev` - Start development server on port 5176
- `npm run build` - Build production bundle
- `npm run preview` - Preview production build locally

### Backend Development (from backend/ directory)
- `python3 main.py` - Start FastAPI server on port 8014
- `uvicorn main:app --reload` - Start with auto-reload

### Backend Testing (from backend/ directory)
- `pytest` - Run unit/integration tests
- `pytest tests/test_models_structure.py` - Test modular models structure
- `./quick_test.sh` - Quick smoke test (12 critical endpoints, ~2 seconds)
- `./test_api_endpoints.sh` - Comprehensive API test (147 endpoints, all modules)

### MCP Server Development (from mcp-server/ directory)
- `./start.sh` - Start MCP server with default settings
- `python test_server.py` - Test server configuration
- `python -m fastmcp dev server.py` - Start with MCP Inspector (interactive testing)
- **Purpose**: Model Context Protocol server exposing backend API as LLM tools

### Telegram Bot Development (from telegram-bot/ directory)
- `python bot.py` - Start Telegram bot (polling mode for local dev)
- `./start-railway.sh` - Start bot for Railway deployment (webhook mode)
- **Purpose**: AI-powered Telegram bot with Claude Sonnet 4.5 for natural language ordering
- **Requires**: MCP server running, TELEGRAM_TOKEN, CLAUDE_API_KEY
- **See**: `telegram-bot/README.md` for detailed setup and deployment

### Architecture Overview

This is a multi-frontend flower shop application with separate interfaces for customers and administrators:

- **Shop** (`/shop`): Customer-facing storefront (port 5180)
- **Frontend** (`/frontend`): Admin panel for managing products, inventory, and orders (port 5176)
- **Backend** (`/backend`): Shared FastAPI service providing REST API for both frontends (port 8014)

All frontends implement a design system approach with Tailwind CSS and are structured as single-page applications with client-side routing.

## How The System Works

### Complete Order Flow (Customer → Database → Admin)

#### 1. Customer Creates Order (Shop Frontend)

**State Management:**
- `OrderFormContext` centralizes all form data:
  - Recipient data (name, phone)
  - Customer data (phone)
  - Delivery address (address, floor, apartment, additionalInfo, askRecipient flag)
  - Pickup location (locationId, address)
  - Delivery time (selectedDate, selectedTimeSlot, selectedTimeLabel)

**Components:**
- `RecipientDataForm` - Connected to context via `useOrderForm()`
- `CustomerDataForm` - Connected to context via `useOrderForm()`
- `AddressSelector` - Both DeliveryAddressForm and PickupAddressSelector connected
- `DeliveryTimeSelector` - Connected to context

**Checkout Process:**
1. User fills forms → All data stored in OrderFormContext
2. User clicks "Оформить заказ" → CheckoutButton validates:
   - Customer phone required
   - Recipient name required (delivery only)
   - Delivery address required (unless "Узнать у получателя" checked)
3. CheckoutButton builds order payload with REAL form data
4. POST to `/api/v1/orders/public/create?shop_id=8`
5. Backend creates order with status=NEW, generates tracking_id
6. Frontend clears cart and navigates to order status page

**Example Order Data:**
```json
{
  "customerName": "+77015211545",
  "phone": "+77015211545",
  "delivery_address": "ул. Кабанбай батыра 87, ЖК Royal Palace, этаж 25, кв/офис 305, Домофон 9999, позвонить за 10 мин",
  "recipient_name": "Мария Петрова",
  "recipient_phone": "+77778889900",
  "delivery_type": "delivery",
  "delivery_cost": 150000,
  "items": [
    {"product_id": 3, "quantity": 1},
    {"product_id": 5, "quantity": 1}
  ]
}
```

#### 2. Authentication & Multi-Tenancy

**Phone Normalization:**
```python
# backend/auth_utils.py:97-114
def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to consistent format.
    +77088888888 -> 77088888888
    77088888888 -> 77088888888
    """
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    if cleaned.startsWith('+7'):
        cleaned = '7' + cleaned[2:]
    return cleaned
```

**JWT Token Structure:**
```json
{
  "sub": "1",  // user_id as string
  "phone": "77088888888",
  "role": "DIRECTOR",
  "shop_id": 8,
  "exp": 1234567890
}
```

**Multi-Tenancy Enforcement:**
- All authenticated endpoints automatically filter by `shop_id` from JWT
- Public endpoints require explicit `?shop_id=8` query parameter
- Database queries use `WHERE shop_id = ?` to isolate data

#### 3. Order Management (Admin Frontend)

**View Orders:**
- GET `/api/v1/orders/` with JWT token
- Backend filters by `shop_id` from token
- Returns only orders for user's shop
- Order statuses: NEW, PAID, ACCEPTED, IN_PRODUCTION, READY, IN_DELIVERY, DELIVERED, CANCELLED

**Change Order Status:**
- PATCH `/api/v1/orders/{order_id}/status`
- Validates shop_id matches
- Updates order.status
- Creates OrderStatusHistory record

**Track Order (Public):**
- GET `/api/v1/orders/track/{tracking_id}`
- No authentication required
- Returns order status and details

#### 4. Product Images System

**Upload Flow (Admin):**
1. User uploads image in `ProductImageUpload` component
2. POST to `https://flower-shop-images.alekenov.workers.dev/upload`
3. Cloudflare Worker:
   - Validates file type and size (max 10MB)
   - Generates unique ID: `${timestamp}-${random}.png`
   - Uploads to R2 bucket
   - Returns URL: `https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png`
4. Frontend stores URL in `formData.photos[]`
5. On product creation:
   - POST `/api/v1/products/` with `image` field
   - POST `/api/v1/products/{id}/images` for each photo
   - Creates `ProductImage` records with `is_primary=true` for first

**Display Flow (Shop):**
1. GET `/api/v1/products/?shop_id=8`
2. Backend returns products with:
   - `image` field (single URL for backward compatibility)
   - `images[]` array with all ProductImage records
3. Frontend displays images from Cloudflare CDN
4. Cloudflare serves with:
   - `Cache-Control: public, max-age=31536000, immutable`
   - Automatic CDN caching

**Image Storage Structure:**
```
Cloudflare R2 Bucket: flower-shop-images
├── mg6684nq-0y61rde1owm.png (1.4MB)
├── mg67xybu-q7yboowkco.png (1.4MB)
├── mg681krk-yqytaiexroo.png (1.4MB)
└── ...

Database:
product.image -> Full Cloudflare URL
productimage.url -> Full Cloudflare URL
```

#### 5. Key Data Flows

**Customer Order Creation:**
```
Shop UI → OrderFormContext → CheckoutButton → POST /orders/public/create
→ Backend creates Order + OrderItems → Returns tracking_id
→ Frontend navigates to /order-status/{tracking_id}
```

**Admin Order Management:**
```
Admin UI → GET /orders/ (with JWT) → Backend filters by shop_id
→ Returns orders list → Admin selects order → PATCH /orders/{id}/status
→ Backend updates status → Returns updated order
```

**Product with Images:**
```
Admin uploads → Cloudflare Worker → R2 Storage → Returns URL
→ Admin saves product → Backend creates Product + ProductImage records
→ Shop fetches products → Backend includes image URLs
→ Shop displays → Cloudflare CDN serves images
```

#### 6. Critical Implementation Details

**Kopecks Pricing:**
- All prices stored in kopecks (100 kopecks = 1 tenge)
- Frontend converts: `Math.floor(price / 100)` for display
- Backend stores: `price_tenge * 100` in database

**Order Status Enum:**
- Database stores uppercase: NEW, PAID, ACCEPTED, etc.
- All lowercase values are invalid and cause 500 errors
- Fixed via: `UPDATE 'order' SET status='NEW' WHERE status='new'`

**Phone Format:**
- Database stores: `77088888888` (without +7 prefix)
- Frontend may send: `+77088888888` or `77088888888`
- Backend normalizes before lookup

**Common Bugs Fixed:**
1. Mock data substitution → OrderFormContext solved
2. Invalid enum values → Database cleanup solved
3. Phone format mismatch → normalize_phone() solved
4. Missing product images → Cloudflare R2 integration solved

## Project Structure

```
figma-product-catalog/
├── shop/             # Customer-facing storefront (port 5180)
│   ├── src/          # Redesigned pages and components
│   │   ├── pages/   # Updated page components
│   │   ├── components/  # New UI components (Radix UI)
│   │   └── services/    # API integration
│   ├── package.json      # Dependencies
│   ├── vite.config.js    # Vite config (port 5180)
│   └── .env.development  # Environment variables
├── frontend/         # Admin panel (port 5176)
│   ├── src/          # Product management, inventory
│   ├── package.json  # Admin dependencies
│   └── vite.config.js # Vite config (port 5176)
├── backend/          # FastAPI backend (SHARED API)
│   ├── main.py      # API entry point
│   ├── api/         # REST endpoints for both frontends
│   │   ├── auth.py, products/, orders/, warehouse.py
│   │   ├── recipes.py, inventory.py, clients.py
│   │   ├── shop.py, profile.py, reviews.py
│   │   └── content.py, superadmin.py (12 modules, 147 endpoints)
│   ├── models/      # SQLAlchemy models (modular structure)
│   │   ├── __init__.py    # Re-exports for backward compatibility
│   │   ├── enums.py       # All enum types
│   │   ├── products.py    # Product models
│   │   ├── orders.py      # Order models
│   │   ├── warehouse.py   # Inventory models
│   │   ├── users.py       # User/auth models
│   │   ├── shop.py        # Shop settings
│   │   ├── reviews.py     # Reviews/FAQ/CMS
│   │   └── schemas.py     # Response schemas
│   ├── tests/       # API and model tests
│   ├── quick_test.sh         # Quick API smoke test (12 endpoints)
│   ├── test_api_endpoints.sh # Comprehensive test (147 endpoints)
│   └── requirements.txt # Python dependencies
├── mcp-server/      # Model Context Protocol server
│   ├── server.py           # MCP server with 15 API tools
│   ├── start.sh            # Quick start script
│   ├── test_server.py      # Test script
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml      # Project configuration
│   └── README.md           # Full MCP documentation
└── scripts/         # Development helper scripts
    ├── start.sh            # Start admin + backend
    ├── start-frontend.sh   # Admin only
    ├── start-backend.sh    # Backend only
    └── start-shop.sh       # Shop only
```

## Technical Stack & Architecture

### Shop (Customer-Facing)
**Framework**: React 18.2.0 + Vite 5.0.8
**Port**: 5180 (development)
**Styling**: Tailwind CSS 3.4.1 + Radix UI components
**Routing**: React Router DOM 7.9.2
**Target**: Mobile-first responsive design
**Backend**: FastAPI backend (`http://localhost:8014/api/v1`)

### Frontend (Admin Panel)
**Framework**: React 18.2.0 + Vite 6.4.0
**Port**: 5176 (development)
**Styling**: Tailwind CSS 3.3.2 with admin-specific tokens
**Routing**: React Router DOM 7.9.2
**Target**: Desktop-first (320px mobile constraint for product views)

### Backend (Shared API)
**Framework**: FastAPI + SQLAlchemy
**Port**: 8014 (development)
**Database**: PostgreSQL on Railway
**Deployment**: Railway with Nixpacks builder (auto-deploy on GitHub push)

### MCP Server (AI Integration)
**Framework**: FastMCP (Model Context Protocol)
**Python**: 3.10+ required
**Tools**: 15 API operations (auth, products, orders, inventory, shop settings)
**Purpose**: Expose backend API as LLM-callable tools for AI assistants
**Transport**: stdio (local), can support HTTP/SSE
**Key Features**:
- Authentication tools (login, get user)
- Product management (CRUD operations)
- Order management (create, track, update status)
- Inventory operations (warehouse management)
- Shop configuration (settings)

**Backend Architecture:**

#### Modular Models Structure
The backend uses a domain-driven modular architecture with models organized into 8 specialized files:

```
backend/models/
├── __init__.py          # Re-exports all models for backward compatibility
├── enums.py            # All enum types (UserRole, OrderStatus, ProductType, etc.)
├── products.py         # Product, ProductColor, ProductTag, ProductStats
├── orders.py           # Order, OrderItem, OrderStatusHistory
├── warehouse.py        # WarehouseItem, WarehouseOperation, Recipe, InventoryCheck
├── users.py            # User (authentication and team management)
├── shop.py             # Shop, ShopSettings, WorkingHours
├── reviews.py          # Review, ReviewPhoto, FAQ, Page (CMS)
└── schemas.py          # Complex response schemas (ClientWithStats, ProductAvailability)
```

**Benefits:**
- Each file <300 lines (maintainable size)
- Clear domain separation
- Easy to find and modify specific models
- Backward compatibility via `__init__.py` re-exports

#### Multi-Tenancy Design
All data is isolated by `shop_id`:
- JWT tokens include `shop_id` claim
- All authenticated endpoints automatically filter by `shop_id`
- Public endpoints require explicit `shop_id` query parameter
- Database foreign keys enforce referential integrity within shops

**Testing Multi-Tenancy:**
```bash
# User A (shop_id=8) cannot access User B's data (shop_id=9)
curl -H "Authorization: Bearer $TOKEN_SHOP_8" \
  http://localhost:8014/api/v1/products/admin
# Returns only shop_id=8 products
```

#### API Testing Infrastructure
- **147 endpoints** across 12 modules (auth, products, orders, warehouse, etc.)
- **Comprehensive test**: `./test_api_endpoints.sh` (all endpoints)
- **Quick smoke test**: `./quick_test.sh` (12 critical endpoints, ~2 seconds)
- **Test coverage**: Authentication, CRUD operations, filters, stats, public/admin endpoints
- **Documentation**: `API_TESTING_GUIDE.md` with examples and troubleshooting

### Design System Implementation

#### Admin Panel Design System (`/frontend/tailwind.config.js`)
Internal product management interface:
```javascript
colors: {
  'purple-primary': '#8A49F3',    // Admin brand primary
  'green-success': '#34C759',     // Success states
  'gray-disabled': '#6B6773',     // Disabled text
  'gray-placeholder': '#828282',  // Placeholder text
  'gray-neutral': '#C4C4C4',      // Neutral backgrounds
  'gray-border': '#E0E0E0',       // Border colors
  'gray-input': '#F2F2F2',        // Input backgrounds
  'gray-input-alt': '#EEEDF2'     // Alternative input backgrounds
}
```

**Critical Rule**: Always use design tokens (e.g., `bg-purple-primary` for admin) rather than hardcoded hex values.

### Component Architecture

#### Admin Components (`/frontend/src/`)
Internal product management interface:

- **Pages**: Main route components in `/src/` root (ProductCatalogFixed, ReadyProducts, AddProduct, etc.)
- **Reusable Components**: Located in `/src/components/` (ToggleSwitch)
- **Styling**: Custom mobile container via `.figma-container` class (320px width constraint)

### Key Architectural Patterns

#### Mobile Container Constraint
All pages must use the `.figma-container` class which enforces:
```css
.figma-container {
  width: 320px;
  min-height: 100vh;
  margin: 0 auto;
  background: white;
}
```

#### State Management Pattern
Uses local React state with useState hooks. Product states are managed per-page with this pattern:
```javascript
const [productStates, setProductStates] = useState(
  products.reduce((acc, product) => ({ ...acc, [product.id]: product.enabled }), {})
);
```

#### Toggle Switch Component
Extracted reusable component supporting multiple sizes (sm/md/lg) with accessibility features:
- Uses design tokens for colors
- Implements proper ARIA attributes (`role="switch"`, `aria-checked`)
- Supports disabled state

#### Routing Structure
- `/` - Main products catalog (ProductCatalogFixed)
- `/ready-products` - Ready products variant (ReadyProducts)
- `/add-product` - Product creation form
- `/edit-product/:id` - Product editing
- `/filters` - Filter interface

### Asset Management Strategy

**Current Approach**: Direct Figma signed URLs (temporary solution)
**Image Specifications**: 88x88px product thumbnails
**Critical Issue**: Figma URLs expire and need asset optimization system

### Icon System Standards

Icons are implemented as inline SVG with standardized dimensions:
- **Search icons**: `viewBox="0 0 24 24"`, `w-4 h-4` classes
- **UI icons**: `viewBox="0 0 20 20"`, `w-4 h-4` classes
- **Colors**: Use `currentColor` or `#828282` for neutral icons
- **Stroke width**: `strokeWidth="1.5"` or `strokeWidth="2"`

### Spacing Consistency Rules

**Standardized Values**:
- Section spacing: `mt-6` (24px) - used for consistent vertical rhythm
- Component gaps: `gap-3` for product card layouts
- Horizontal padding: `px-4` for page-level content

**Critical**: Avoid mixing `mt-4` and `mt-6` - use `mt-6` for section-level spacing consistency.

### Form Input Patterns

Forms use controlled components with validation patterns:
- Price inputs: `inputMode="numeric"` with thousand-separator formatting
- Search inputs: Include SVG search icon positioned absolutely
- Color tags: Predefined array of color objects with id/name/color properties

### Component Extraction Guidelines

When identifying repeated patterns, extract to `/src/components/` with these naming conventions:
- PascalCase component names
- Props interface supporting size variants where applicable
- Accessibility features included by default
- Design token usage enforced

## Design System Integration

### Figma MCP Integration Rules

When converting Figma designs:
1. Map colors to existing design tokens or create new semantic tokens
2. Use established spacing scale (`mt-6`, `gap-3`, `px-4`)
3. Follow mobile-first 320px container constraint
4. Extract reusable patterns into components
5. Maintain consistent icon sizing and viewBox standards

### Token Extension Process

Add new design tokens to `/tailwind.config.js` under `theme.extend.colors` with semantic naming:
```javascript
'semantic-name': '#HEX_VALUE',  // Usage description
```

## Development Patterns

### State Management Approach
- Use local state for component-specific data
- Implement reducer pattern for complex state (products with enable/disable toggles)
- Persist filter state in localStorage when needed

### Navigation Patterns
Use React Router's `useNavigate` hook consistently:
```javascript
const navigate = useNavigate();
navigate('/path'); // Programmatic navigation
```

### Component Import Structure
```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ComponentName from './components/ComponentName';
import './App.css';
```

This architecture supports systematic design system implementation while maintaining development velocity and consistent user experience across the mobile catalog interface.

## Production Deployment (Railway)

### Service Architecture

The application is deployed on Railway with automatic GitHub integration:

**Project**: `positive-exploration`
**GitHub Repo**: `alekenov/figma-product-catalog`
**Branch**: `main`
**Auto-deploy**: Enabled on push to main

### Services Configuration

#### Frontend Service
- **Service Name**: `Frontend`
- **Builder**: NIXPACKS
- **Root Directory**: `/frontend`
- **Start Command**: `npm run start` (serves built dist/ folder)
- **Public URL**: https://frontend-production-6869.up.railway.app
- **Key Environment Variables**:
  - `VITE_API_BASE_URL` = `https://figma-product-catalog-production.up.railway.app/api/v1`
  - `PORT` = Auto-assigned by Railway

**Build Process**:
1. Nixpacks detects Node.js project
2. Runs `npm ci` to install dependencies
3. Runs `npm run build` to create production bundle
4. Injects `VITE_API_BASE_URL` during build time
5. Serves with `serve -s dist` on Railway-assigned port

#### Backend Service
- **Service Name**: `figma-product-catalog`
- **Builder**: NIXPACKS
- **Root Directory**: `/backend`
- **Start Command**: `./start.sh` (expands PORT variable correctly)
- **Public URL**: https://figma-product-catalog-production.up.railway.app
- **Key Environment Variables**:
  - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` (reference variable)
  - `CORS_ORIGINS` = `https://frontend-production-6869.up.railway.app,http://localhost:5176,http://localhost:5173,http://localhost:3000`
  - `SECRET_KEY` = Production secret key
  - `DEBUG` = `false`

**Build Process**:
1. Nixpacks detects Python project
2. Installs dependencies from `requirements.txt`
3. Makes `start.sh` executable
4. Runs `./start.sh` which executes: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Database Service
- **Service Name**: `Postgres`
- **Type**: PostgreSQL
- **Connection**: Available via `${{Postgres.DATABASE_URL}}` reference variable
- **Shared Access**: Both backend services can reference this database

### Railway Configuration Files

#### frontend/railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run start",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### backend/railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
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

**Note**: `start.sh` is required because Nixpacks doesn't perform shell expansion for `$PORT` in `startCommand`. The script properly expands the PORT environment variable.

#### backend/start.sh
```bash
#!/bin/sh
PORT=${PORT:-8000}
echo "Starting server on port $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Deployment Workflow

1. **Local Development**: Make changes and commit to `main` branch
2. **Push to GitHub**: `git push origin main`
3. **Railway Detects Changes**: Webhook triggers automatic build
4. **Parallel Builds**: Frontend and Backend build simultaneously
5. **Health Checks**: Railway verifies services start successfully
6. **Zero-Downtime Deploy**: New version replaces old without interruption
7. **Rollback Available**: Can revert to previous deployment if needed

### Railway CLI Commands

```bash
# Check current status
railway status

# View logs (build or deploy)
railway logs --build
railway logs --deploy

# Link to specific service
railway service <service-name>

# Deploy manually (usually auto-deploy handles this)
railway up --ci

# Manage environment variables
railway variables --set KEY=value
railway variables --kv  # View all variables
```

### Monitoring & Debugging

**Health Endpoints**:
- Backend: https://figma-product-catalog-production.up.railway.app/health
- Frontend: https://frontend-production-6869.up.railway.app/ (should load UI)

**Common Issues**:

1. **PORT variable not expanding**: Use `./start.sh` instead of direct uvicorn command in `startCommand`
2. **CORS errors**: Ensure `CORS_ORIGINS` includes frontend domain
3. **Build-time env vars**: Frontend needs `VITE_API_BASE_URL` available during `npm run build` (Nixpacks handles this automatically)
4. **Database connection**: Use reference variable `${{Postgres.DATABASE_URL}}` not hardcoded connection string

### Why Nixpacks over Docker?

**Advantages**:
- ✅ Automatic build-time environment variable injection
- ✅ Auto-detects language and framework
- ✅ No need for manual Dockerfile maintenance
- ✅ Optimized caching and faster builds
- ✅ Consistent with Railway best practices

**Trade-offs**:
- Less control over exact build process
- Must use workarounds for shell expansion (hence `start.sh`)

### Migration Notes (2025-09-29)

Successfully migrated from mixed Docker/Nixpacks architecture to pure Nixpacks:
- **Old Setup**: Backend used Dockerfile with Docker Hub, Frontend used Nixpacks
- **New Setup**: Both services use Nixpacks with GitHub auto-deploy
- **Key Fix**: Changed backend `startCommand` from `uvicorn main:app --host 0.0.0.0 --port $PORT` to `./start.sh` to properly expand PORT variable
- **Result**: Unified deployment strategy, faster iteration, automatic deploys on every push