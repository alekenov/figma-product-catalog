# Developer Onboarding Guide

Welcome to the Flower Shop Platform (cvety.kz) project! This guide will get you from zero to productive in **30 minutes**.

**Target Audience**: New developers joining the project
**Time to Complete**: 30 minutes for setup + first contribution
**Last Updated**: 2025-10-28

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup (15 minutes)](#quick-setup-15-minutes)
3. [Architecture Overview](#architecture-overview)
4. [Development Workflows](#development-workflows)
5. [Key Files and Directories](#key-files-and-directories)
6. [Troubleshooting](#troubleshooting)
7. [Additional Resources](#additional-resources)

---

## Prerequisites

Before starting, ensure you have these tools installed:

### Required Tools

- [ ] **Python 3.10+** - Backend and bots
  ```bash
  python3 --version  # Should be 3.10 or higher
  ```

- [ ] **Node.js 18+** - Frontend applications
  ```bash
  node --version  # Should be 18.x or higher
  ```

- [ ] **Git** - Version control
  ```bash
  git --version
  ```

- [ ] **Code Editor** - VS Code recommended
  - Install Python extension
  - Install ESLint extension

### Optional Tools

- [ ] **PostgreSQL** - For local database (or use Railway)
- [ ] **Docker** - For containerized development (optional)
- [ ] **Railway CLI** - For deployment management
  ```bash
  npm install -g @railway/cli
  railway login
  ```

### Access Requirements

- [ ] GitHub access to `alekenov/figma-product-catalog` repository
- [ ] Railway account (for production deployment)
- [ ] Telegram account (for bot testing)
- [ ] @BotFather token (for creating test bots)

---

## Quick Setup (15 minutes)

### Step 1: Clone Repository (1 min)

```bash
git clone https://github.com/alekenov/figma-product-catalog.git
cd figma-product-catalog
```

### Step 2: Install Backend Dependencies (3 min)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Copy environment variables:**
```bash
cp .env.example .env
# Edit .env with your local configuration
```

**Key variables to set:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS` - Frontend URLs

### Step 3: Install Frontend Dependencies (3 min)

```bash
# Admin Panel
cd ../frontend
npm install

# Customer-Facing Shop
cd ../shop
npm install
```

### Step 4: Install Bot Dependencies (2 min)

```bash
# Customer Bot
cd ../customer-bot
pip install -r requirements.txt
cp .env.example .env.development
# Add your Telegram bot token

# Admin Bot
cd ../admin-bot
pip install -r requirements.txt
cp .env.example .env.development
# Add your Telegram bot token
```

### Step 5: Start All Services (2 min)

**Option A: Using Helper Scripts (Recommended)**
```bash
cd figma-product-catalog
./scripts/start.sh  # Starts backend + admin frontend
```

**Option B: Manual Start (for development)**
```bash
# Terminal 1: Backend API
cd backend
python3 main.py  # http://localhost:8014

# Terminal 2: Admin Frontend
cd frontend
npm run dev  # http://localhost:5176

# Terminal 3: Customer Shop
cd shop
npm run dev  # http://localhost:5180

# Terminal 4: Customer Bot (optional)
cd customer-bot
ENVIRONMENT=development python bot.py

# Terminal 5: Admin Bot (optional)
cd admin-bot
ENVIRONMENT=development python bot.py
```

### Step 6: Verify Installation (2 min)

**Check Backend:**
```bash
curl http://localhost:8014/health
# Should return: {"status":"ok"}
```

**Check API Docs:**
- Open: http://localhost:8014/docs
- You should see Swagger UI with all endpoints

**Check Frontend:**
- Admin Panel: http://localhost:5176
- Shop: http://localhost:5180

**Check Bots:**
- Send `/start` to your bot in Telegram
- Should receive welcome message

### Step 7: Run Tests (2 min)

```bash
cd backend
./quick_test.sh  # Runs 12 critical endpoints (~2 seconds)
```

✅ **You're ready to develop!**

---

## Architecture Overview

### System Diagram

```
┌─────────────────┐
│   Customers     │
└────────┬────────┘
         │
    ┌────▼─────────────────────────────┐
    │  Customer Channels               │
    │  • Shop (port 5180)              │
    │  • Customer Bot (Telegram)       │
    │  • WhatsApp (future)             │
    └────┬─────────────────────────────┘
         │
         │ HTTP API
         │
    ┌────▼─────────────────────────────┐
    │  Backend API (port 8014)         │
    │  • FastAPI + SQLAlchemy          │
    │  • JWT Authentication            │
    │  • Multi-tenancy (shop_id)       │
    └────┬────────┬────────────────────┘
         │        │
         │        └──────────────┐
         │                       │
    ┌────▼─────────┐     ┌──────▼────────────┐
    │  PostgreSQL  │     │  External Services│
    │  (Railway)   │     │  • Cloudflare R2  │
    │              │     │  • Kaspi Pay      │
    │  • Products  │     │  • Bitrix CMS     │
    │  • Orders    │     │  • Visual Search  │
    │  • Users     │     └───────────────────┘
    └──────────────┘
         ▲
         │
    ┌────┴─────────────────────────────┐
    │  Staff Channels                  │
    │  • Admin Panel (port 5176)       │
    │  • Admin Bot (Telegram)          │
    └──────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose | Tech Stack | Port |
|-----------|---------|------------|------|
| **Backend** | REST API, business logic, database | FastAPI, SQLAlchemy, PostgreSQL | 8014 |
| **Frontend (Admin)** | Product management, orders, inventory | React, Vite, Tailwind CSS | 5176 |
| **Shop** | Customer-facing storefront | React, Vite, Radix UI | 5180 |
| **Customer Bot** | AI-powered order placement | Python, telegram-bot, Claude AI | N/A |
| **Admin Bot** | Staff order management | Python, telegram-bot, MCP | N/A |
| **MCP Server** | Model Context Protocol tools | FastMCP, Python | 8000 |
| **AI Agent Service** | Claude AI integration | Python, httpx | 8002 |
| **Visual Search** | Image similarity search | Cloudflare Worker, pgvector | N/A |

### Key Architectural Patterns

#### 1. Multi-Tenancy (shop_id Isolation)

All data is isolated by `shop_id`:

```python
# JWT token includes shop_id
{
  "sub": "user_id",
  "phone": "77012345678",
  "role": "DIRECTOR",
  "shop_id": 8,  # Isolates data by shop
  "exp": 1234567890
}

# All queries filter by shop_id automatically
products = db.query(Product).filter(Product.shop_id == current_user.shop_id).all()
```

**Environments:**
- **Development**: shop_id=8, Railway PostgreSQL
- **Production**: shop_id=17008, Bitrix MySQL

#### 2. Phone Normalization

Phones stored without +7 prefix:

```python
# Input: +77012345678 or 77012345678
# Stored: 77012345678
# Display: +7 (701) 234-56-78
```

#### 3. Kopecks Pricing

All prices in kopecks (100 kopecks = 1 tenge):

```python
# Database: 150000 (kopecks)
# Display: 1,500 ₸ (tenge)
# Calculation: price / 100
```

#### 4. Shared Telegram Modules

Both bots import from `/shared-telegram`:

```python
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared-telegram'))

from mcp_client import create_mcp_client
from formatters import format_price, extract_product_images
from logging_config import configure_logging, get_logger
```

---

## Development Workflows

### Adding a New API Endpoint

**Example**: Add `/api/v1/analytics/daily-stats` endpoint

**Step 1: Create router file**
```python
# backend/api/analytics/router.py
from fastapi import APIRouter, Depends
from backend.models import User
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/daily-stats")
async def get_daily_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get daily statistics for current shop.

    Returns order count, revenue, and popular products.
    """
    shop_id = current_user.shop_id
    # Implementation...
    return {"date": "2025-10-28", "orders": 15, "revenue": 450000}
```

**Step 2: Register router**
```python
# backend/main.py
from backend.api.analytics.router import router as analytics_router

app.include_router(analytics_router, prefix="/api/v1")
```

**Step 3: Test locally**
```bash
# Get auth token first
curl -X POST http://localhost:8014/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "77015211545", "password": "1234"}'

# Use token to test endpoint
curl http://localhost:8014/api/v1/analytics/daily-stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Step 4: Write tests**
```python
# backend/tests/test_analytics.py
def test_daily_stats(client, auth_headers):
    response = client.get("/api/v1/analytics/daily-stats", headers=auth_headers)
    assert response.status_code == 200
    assert "orders" in response.json()
```

**Step 5: Deploy**
```bash
git add .
git commit -m "feat: Add daily statistics endpoint"
git push origin main  # Auto-deploys to Railway
```

### Creating a Telegram Bot Command

**Example**: Add `/stats` command to admin-bot

**Step 1: Add command handler**
```python
# admin-bot/bot.py or admin_handlers.py
async def handle_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show shop statistics"""
    user_phone = update.effective_user.id

    # Call MCP tool
    mcp_client = create_mcp_client(os.getenv('MCP_SERVER_URL'))
    stats = await mcp_client.call_tool("get_shop_stats", {
        "shop_id": int(os.getenv('DEFAULT_SHOP_ID'))
    })

    # Format response
    message = f"""
📊 Shop Statistics

Orders Today: {stats['orders_today']}
Revenue: {format_price(stats['revenue'])}
Popular Product: {stats['top_product']}
    """

    await update.message.reply_text(message)
```

**Step 2: Register handler**
```python
# admin-bot/bot.py in __init__ or main setup
application.add_handler(CommandHandler("stats", handle_stats_command))
```

**Step 3: Test locally**
```bash
cd admin-bot
ENVIRONMENT=development python bot.py

# In Telegram, send: /stats
```

**Step 4: Deploy**
```bash
git commit -m "feat: Add /stats command to admin bot"
git push  # Auto-deploys to Railway
```

### Database Migration

**Step 1: Update model**
```python
# backend/models/products.py
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: int  # Kopecks
    stock_count: int = Field(default=0)  # NEW FIELD
    shop_id: int
```

**Step 2: Create migration script**
```python
# backend/migrations/add_stock_count_to_products.py
"""
Migration: Add stock_count field to products table
Date: 2025-10-28
"""
from sqlalchemy import text

def upgrade(db_session):
    """Add stock_count column"""
    db_session.execute(text("""
        ALTER TABLE product
        ADD COLUMN stock_count INTEGER DEFAULT 0
    """))
    db_session.commit()

def downgrade(db_session):
    """Remove stock_count column"""
    db_session.execute(text("""
        ALTER TABLE product
        DROP COLUMN stock_count
    """))
    db_session.commit()
```

**Step 3: Run migration locally**
```bash
cd backend
python3 migrations/add_stock_count_to_products.py
```

**Step 4: Verify**
```bash
# Check schema
psql $DATABASE_URL -c "\d product"
```

**Step 5: Deploy**
```bash
git commit -m "migration: Add stock_count to products"
git push  # Run migration on Railway manually or via script
```

### Testing Changes Locally

**Backend Tests:**
```bash
cd backend
pytest tests/test_products.py  # Specific module
pytest  # All tests
./quick_test.sh  # Quick smoke test (12 endpoints, 2 seconds)
```

**Frontend Tests:**
```bash
cd frontend
npm run build  # Verify build succeeds
npm run preview  # Test production build locally
```

**Integration Test:**
```bash
# 1. Start all services
./scripts/start.sh

# 2. Test full flow
curl http://localhost:8014/api/v1/products/?shop_id=8
# Should return products list

# 3. Test frontend can fetch
curl http://localhost:5176
# Should return HTML
```

---

## Key Files and Directories

### Project Structure

```
figma-product-catalog/
├── backend/                 # FastAPI backend (port 8014)
│   ├── main.py             # API entry point
│   ├── api/                # REST endpoints (12 modules, 147 endpoints)
│   │   ├── auth.py         # Authentication
│   │   ├── products/       # Product CRUD
│   │   ├── orders/         # Order management
│   │   └── ...
│   ├── models/             # SQLAlchemy models (modular)
│   │   ├── enums.py        # All enum types
│   │   ├── products.py     # Product models
│   │   ├── orders.py       # Order models
│   │   └── ...
│   ├── auth_utils.py       # JWT authentication
│   ├── tests/              # Pytest tests
│   └── migrations/         # Database migrations
│
├── frontend/               # Admin panel (port 5176)
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable UI components
│   │   └── services/       # API client
│   └── package.json
│
├── shop/                   # Customer storefront (port 5180)
│   ├── src/
│   │   ├── pages/          # Shop pages
│   │   ├── components/     # Radix UI components
│   │   └── services/       # API integration
│   └── package.json
│
├── customer-bot/           # Customer Telegram bot
│   ├── bot.py              # Main bot logic
│   ├── .env.development    # Dev environment (shop_id=8)
│   ├── .env.production     # Prod environment (shop_id=17008)
│   └── requirements.txt
│
├── admin-bot/              # Admin Telegram bot
│   ├── bot.py              # Bot with admin commands
│   ├── admin_handlers.py   # Command handlers
│   └── requirements.txt
│
├── shared-telegram/        # Shared bot modules
│   ├── mcp_client.py       # MCP HTTP client
│   ├── logging_config.py   # Logging setup
│   ├── formatters.py       # Utility formatters
│   └── README.md
│
├── mcp-server/             # Model Context Protocol server
│   ├── server.py           # MCP tools (40+ operations)
│   └── README.md
│
├── scripts/                # Helper scripts
│   ├── start.sh            # Start backend + frontend
│   ├── start-backend.sh    # Backend only
│   ├── start-frontend.sh   # Frontend only
│   └── start-shop.sh       # Shop only
│
└── docs/                   # Documentation
    ├── DEVELOPER_ONBOARDING.md  # This file
    ├── API_TESTING_GUIDE.md
    └── archive/            # Historical docs
```

### Important Configuration Files

| File | Purpose |
|------|---------|
| `backend/.env` | Backend environment variables (DATABASE_URL, SECRET_KEY) |
| `frontend/.env.development` | Frontend API base URL (localhost) |
| `shop/.env.development` | Shop API base URL |
| `customer-bot/.env.development` | Bot token, MCP URL, shop_id=8 |
| `customer-bot/.env.production` | Prod bot token, shop_id=17008 |
| `railway.json` | Railway deployment configuration |
| `CLAUDE.md` | Main project documentation (850+ lines) |

### Where to Find Things

**Need to...** | **Look in...**
---|---
Add API endpoint | `backend/api/{module}/router.py`
Add database model | `backend/models/{domain}.py`
Add frontend page | `frontend/src/pages/` or `shop/src/pages/`
Add bot command | `{bot}/bot.py` or `admin_handlers.py`
See API endpoints | http://localhost:8014/docs (Swagger UI)
Check tests | `backend/tests/test_*.py`
See deployment config | `railway.json`, `.github/workflows/`

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Bot Not Responding

**Symptoms**: Telegram bot doesn't reply to messages

**Diagnosis:**
```bash
# Check webhook status (production)
curl "https://api.telegram.org/bot{YOUR_TOKEN}/getWebhookInfo"

# Check if bot is running (development)
ps aux | grep "python bot.py"

# Check environment
echo $ENVIRONMENT  # Should be "development" or "production"
```

**Solutions:**

1. **Wrong environment loaded:**
   ```bash
   # Correct way
   ENVIRONMENT=development python bot.py

   # Wrong way (uses default .env)
   python bot.py
   ```

2. **Webhook conflict (production mode running locally):**
   ```bash
   # Delete webhook
   curl "https://api.telegram.org/bot{TOKEN}/deleteWebhook"

   # Restart bot in polling mode
   ENVIRONMENT=development python bot.py
   ```

3. **Check logs:**
   ```bash
   tail -f customer-bot/logs/bot_*.log
   # Look for errors, MCP connection issues
   ```

#### Issue: Wrong shop_id Data Showing

**Symptoms**: Seeing orders/products from different shop

**Diagnosis:**
```bash
# Check JWT token shop_id
# Decode token at https://jwt.io

# Check database directly
psql $DATABASE_URL
SELECT id, shop_id, name FROM product LIMIT 5;
SELECT id, shop_id, status FROM "order" LIMIT 5;
```

**Solutions:**

1. **Login with correct credentials:**
   ```bash
   # Development: shop_id=8
   curl -X POST http://localhost:8014/api/v1/auth/login \
     -d '{"phone": "77015211545", "password": "1234"}'
   ```

2. **Verify API requests include shop_id:**
   ```bash
   # Public endpoints require shop_id parameter
   curl "http://localhost:8014/api/v1/products/?shop_id=8"
   ```

3. **Check environment variables:**
   ```bash
   # Bot should have DEFAULT_SHOP_ID
   echo $DEFAULT_SHOP_ID  # Should be 8 or 17008
   ```

#### Issue: CORS Errors in Frontend

**Symptoms**: Browser console shows CORS policy errors

**Diagnosis:**
```bash
# Check CORS configuration
grep CORS_ORIGINS backend/.env

# Check if backend is running
curl http://localhost:8014/health
```

**Solutions:**

1. **Add frontend URL to CORS_ORIGINS:**
   ```bash
   # backend/.env
   CORS_ORIGINS=http://localhost:5176,http://localhost:5180,http://localhost:3000
   ```

2. **Restart backend:**
   ```bash
   cd backend
   # Kill existing process
   pkill -f "python3 main.py"
   # Start again
   python3 main.py
   ```

3. **Check frontend API base URL:**
   ```bash
   # frontend/.env.development
   VITE_API_BASE_URL=http://localhost:8014/api/v1
   ```

#### Issue: Database Connection Failed

**Symptoms**: Backend crashes with connection error

**Diagnosis:**
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/database
```

**Solutions:**

1. **Use Railway PostgreSQL:**
   ```bash
   # Link to Railway database
   railway link
   railway variables
   # Copy DATABASE_URL to backend/.env
   ```

2. **Use local PostgreSQL:**
   ```bash
   # Install PostgreSQL
   brew install postgresql  # macOS

   # Create database
   createdb flower_shop_dev

   # Update .env
   DATABASE_URL=postgresql://localhost/flower_shop_dev
   ```

#### Issue: Import Errors in Bots

**Symptoms**: `ModuleNotFoundError: No module named 'mcp_client'`

**Solutions:**

1. **Check shared-telegram directory exists:**
   ```bash
   ls shared-telegram/
   # Should show: mcp_client.py, logging_config.py, formatters.py
   ```

2. **Check import path:**
   ```python
   # Both bots should have this
   import sys
   sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared-telegram'))
   ```

3. **Install bot dependencies:**
   ```bash
   cd customer-bot  # or admin-bot
   pip install -r requirements.txt
   ```

#### Issue: Railway Deployment Failed

**Symptoms**: Push succeeds but service doesn't start

**Diagnosis:**
```bash
# Check Railway logs
railway logs --service backend

# Check build logs
railway logs --build
```

**Solutions:**

1. **Check railway.json:**
   ```json
   {
     "build": {"builder": "NIXPACKS"},
     "deploy": {
       "startCommand": "./start.sh",
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

2. **Verify environment variables:**
   ```bash
   railway variables --kv
   # Check DATABASE_URL, SECRET_KEY, CORS_ORIGINS
   ```

3. **Check start.sh is executable:**
   ```bash
   chmod +x backend/start.sh
   git add backend/start.sh
   git commit -m "fix: Make start.sh executable"
   ```

---

## Additional Resources

### Documentation

- **Main Project Documentation**: [CLAUDE.md](../CLAUDE.md) - Comprehensive 850+ line guide
- **API Testing Guide**: [API_TESTING_GUIDE.md](../backend/API_TESTING_GUIDE.md)
- **Production Setup**: [PRODUCTION_SETUP_RU.md](../PRODUCTION_SETUP_RU.md) (Russian)
- **System Architecture**: [SYSTEM_ARCHITECTURE_DIAGRAMS.md](../SYSTEM_ARCHITECTURE_DIAGRAMS.md)

### Component Documentation

- **Backend API**: http://localhost:8014/docs (Swagger UI)
- **Customer Bot**: [customer-bot/README.md](../customer-bot/README.md)
- **Admin Bot**: [admin-bot/README.md](../admin-bot/README.md)
- **MCP Server**: [mcp-server/README.md](../mcp-server/README.md)
- **Shared Telegram Modules**: [shared-telegram/README.md](../shared-telegram/README.md)

### External Services

- **Railway Dashboard**: https://railway.app/project/positive-exploration
- **Cloudflare R2** (Images): https://dash.cloudflare.com
- **GitHub Repository**: https://github.com/alekenov/figma-product-catalog
- **Kaspi Pay Docs**: https://developers.kaspi.kz

### Development Tools

**Recommended VS Code Extensions:**
- Python (ms-python.python)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- REST Client (humao.rest-client)
- SQLite Viewer (alexcvzz.vscode-sqlite)

**Useful Commands:**
```bash
# Backend
cd backend && ./quick_test.sh              # Quick API test
cd backend && pytest                        # Run all tests
cd backend && python3 -m fastapi dev main.py  # Dev server with reload

# Frontend
cd frontend && npm run dev                  # Dev server
cd frontend && npm run build                # Production build

# Bots
cd customer-bot && python3 bot.py           # Test bot locally
railway logs --service customer-bot         # View production logs

# Database
psql $DATABASE_URL                          # Connect to database
railway run psql                            # Connect via Railway

# Git
git log --oneline -10                       # Recent commits
git diff origin/main                        # Compare with remote
```

### Getting Help

**Internal Resources:**
1. Read [CLAUDE.md](../CLAUDE.md) for detailed architecture
2. Check [API_TESTING_GUIDE.md](../backend/API_TESTING_GUIDE.md) for endpoint examples
3. Review recent git commits: `git log --oneline -20`

**External Resources:**
1. FastAPI Docs: https://fastapi.tiangolo.com
2. React Docs: https://react.dev
3. Telegram Bot API: https://core.telegram.org/bots/api

**Ask Questions:**
- Team Chat: [Your team communication channel]
- GitHub Issues: https://github.com/alekenov/figma-product-catalog/issues

---

## Next Steps

Now that you're set up, here are recommended first contributions:

**Easy (1-2 hours):**
- [ ] Fix a typo in documentation
- [ ] Add a simple API endpoint (e.g., `/health-detailed`)
- [ ] Write a test for an existing endpoint
- [ ] Add a new bot command (e.g., `/help`)

**Medium (4-6 hours):**
- [ ] Add a new product filter in shop
- [ ] Implement order status email notifications
- [ ] Create admin dashboard statistics page
- [ ] Add new MCP tool for inventory management

**Hard (1-2 days):**
- [ ] Implement automatic product sync from Bitrix
- [ ] Add real-time order tracking with WebSockets
- [ ] Create comprehensive E2E test suite
- [ ] Implement role-based access control in admin bot

**Explore the Codebase:**
```bash
# Read recent changes
git log --since="2 weeks ago" --oneline

# Find examples of API endpoints
ls backend/api/*/router.py

# See how models are structured
cat backend/models/products.py

# Check bot commands
grep -r "CommandHandler" customer-bot/ admin-bot/
```

---

## Feedback

This onboarding guide is a living document. If you:
- Found something confusing
- Discovered a missing step
- Have suggestions for improvement

Please update this file and submit a PR!

**Last Updated**: 2025-10-28
**Contributors**: Development Team

---

**Welcome to the team! 🎉**
