# Payment Service - Railway Deployment Guide

## Option 1: Deploy via Railway Web UI (Recommended)

### Step 1: Create Service

1. Go to https://railway.app/project/positive-exploration
2. Click **"+ New"** → **"GitHub Repo"**
3. Select repository: `alekenov/figma-product-catalog`
4. **Root Directory**: `/payment-service`
5. **Service Name**: `payment-service`
6. Click **"Deploy"**

### Step 2: Add PostgreSQL Database

1. In the same project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically create `DATABASE_URL` variable
3. The payment-service will automatically detect it

### Step 3: Configure Environment Variables

In payment-service settings → Variables → Add:

```bash
PRODUCTION_API_URL=https://cvety.kz/api/v2/paymentkaspi
KASPI_ACCESS_TOKEN=<get from production>
CORS_ORIGINS=https://frontend-production-6869.up.railway.app
DEBUG=False
```

### Step 4: Seed Database

After successful deployment:

```bash
# Option A: Railway Web Terminal
# Go to service → Shell → Run:
python seed_data.py seed
python seed_data.py list

# Option B: Railway CLI
cd /Users/alekenov/figma-product-catalog/payment-service
railway run python seed_data.py seed
railway run python seed_data.py list
```

### Step 5: Verify Deployment

```bash
# Health check
curl https://payment-service-production.up.railway.app/health

# List configs
curl https://payment-service-production.up.railway.app/admin/configs
```

---

## Option 2: Deploy via Git Push (Automatic)

### Prerequisites
- Repository must be connected to Railway project
- Root directory detection configured

### Steps

1. **Commit code:**
```bash
cd /Users/alekenov/figma-product-catalog
git add payment-service/
git commit -m "feat: Add payment service microservice

- Automatic БИН routing by shop_id
- HTTP client to production API
- Admin UI for payment config management
- Audit logging for all operations"
git push origin main
```

2. **Railway will auto-detect** the new service if:
   - `railway.json` or `railway.toml` exists
   - Dockerfile exists
   - Or Nixpacks auto-detection succeeds

3. **Configure variables** in Web UI (see Step 3 above)

4. **Seed database** (see Step 4 above)

---

## Option 3: Manual Railway CLI (After Web UI Setup)

### Prerequisites
- Service must be created in Web UI first
- Railway CLI installed: `brew install railway`

### Link to Existing Service

```bash
cd /Users/alekenov/figma-product-catalog/payment-service

# Link to project (interactive)
railway link

# Or link with IDs
railway link <project-id>
```

### Deploy

```bash
# Deploy current directory
railway up --ci

# Set variables
railway variables --set KASPI_ACCESS_TOKEN="<token>"
railway variables --set PRODUCTION_API_URL="https://cvety.kz/api/v2/paymentkaspi"

# Seed database
railway run python seed_data.py seed

# View logs
railway logs --build
railway logs --deploy
```

---

## Environment Variables Reference

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection (auto) | `postgresql://...` |
| `PRODUCTION_API_URL` | Production PHP API base | `https://cvety.kz/api/v2/paymentkaspi` |
| `KASPI_ACCESS_TOKEN` | Access token for prod API | Get from .env or production |
| `CORS_ORIGINS` | Allowed origins | `https://frontend-production-6869.up.railway.app` |
| `PORT` | Service port (auto by Railway) | `8015` (local), `$PORT` (Railway) |
| `DEBUG` | Debug mode | `False` |

---

## Troubleshooting

### Service not building
- Check `railway.json` is present
- Verify `requirements.txt` has all dependencies
- Check logs: `railway logs --build`

### Database connection error
- Ensure PostgreSQL plugin is added
- Check `DATABASE_URL` is set correctly
- Verify database is running: Railway dashboard → Database

### KASPI_ACCESS_TOKEN missing
- Get from production: `ssh root@185.125.90.141 "cat /path/to/.env"`
- Or check backend config: `backend/config.py`
- Set in Railway: Variables → `KASPI_ACCESS_TOKEN`

### Seed script fails
- Ensure database tables are created (happens automatically on startup)
- Check DATABASE_URL is correct
- Try: `railway run python -c "from database import create_db_and_tables; create_db_and_tables()"`

---

## Next Steps After Deployment

1. ✅ Verify health: `curl <service-url>/health`
2. ✅ List configs: `curl <service-url>/admin/configs`
3. ✅ Test payment creation (see README.md for curl examples)
4. ✅ Integrate with main backend (see INTEGRATION.md)
5. ✅ Add monitoring/alerts

---

## Recommended: Web UI First, CLI Later

The easiest approach:
1. **Create service** in Railway Web UI
2. **Configure variables** in Web UI
3. **Use CLI** for deployments, logs, running commands

This avoids TTY/interactive issues with Railway CLI.
