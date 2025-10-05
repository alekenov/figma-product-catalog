# Shop - Customer-Facing Storefront (New Version)

New version of the customer-facing flower shop website.

## Quick Start

```bash
# From project root
./scripts/start-shop.sh

# Or from this directory
npm install
npm run dev
```

Server will start on: **http://localhost:5180**

## Key Differences from /website

This is a completely redesigned version of the customer-facing storefront with:
- Updated UI/UX on every page
- Same backend API (http://localhost:8014/api/v1)
- Same shop_id (can be configured in .env.development)
- Different port (5180 vs 5179)

## Directory Structure

After you unpack your archive, the structure should look like:

```
shop/
├── src/
│   ├── pages/          # Page components
│   ├── components/     # Reusable UI components
│   ├── services/       # API integration
│   ├── contexts/       # React contexts
│   └── assets/         # Images, icons
├── public/             # Static assets
├── package.json        # Dependencies
├── vite.config.js      # Vite configuration (port 5180)
├── .env.development    # Development environment variables
└── README.md           # This file
```

## Configuration

### Environment Variables (.env.development)

```env
VITE_API_BASE_URL=http://localhost:8014/api/v1
VITE_SHOP_ID=8
VITE_ENV=development
```

### API Integration

Use the same API as the old website:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Example: Get products
const products = await api.get('/products/', {
  params: { shop_id: import.meta.env.VITE_SHOP_ID }
});
```

## Available Scripts

- `npm run dev` - Start development server (port 5180)
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Backend Connection

This frontend connects to the shared FastAPI backend running on port 8014.

**Make sure backend is running:**
```bash
# Terminal 1: Start backend
cd backend
python3 main.py

# Terminal 2: Start shop
cd shop
npm run dev
```

## Port Configuration

- **Shop (new)**: http://localhost:5180
- **Website (old)**: http://localhost:5179
- **Admin Frontend**: http://localhost:5176
- **Backend API**: http://localhost:8014

All ports are configured in CORS - you can run all frontends simultaneously.

## Deployment

For production deployment, update Railway environment variables:

```env
VITE_API_BASE_URL=https://figma-product-catalog-production.up.railway.app/api/v1
VITE_SHOP_ID=8
```

## Migration from /website

You can run both versions in parallel:
1. Old version (`/website`) on port 5179
2. New version (`/shop`) on port 5180

Compare, test, and switch when ready.

## Troubleshooting

### CORS errors
Make sure backend is running and includes port 5180 in CORS config.

### API connection failed
Check that `VITE_API_BASE_URL` in `.env.development` is correct.

### Port already in use
Kill process using port 5180:
```bash
lsof -ti:5180 | xargs kill
```
