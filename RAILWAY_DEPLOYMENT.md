# Railway Deployment Guide

This guide explains how to deploy the Figma Product Catalog application to Railway.

## Project Structure

This is a full-stack application with:
- **Frontend**: React + Vite application (port 5175)
- **Backend**: FastAPI Python application (port 8014)

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository with your code
3. Railway CLI installed (optional, for CLI deployment)

## Deployment Options

### Option 1: Deploy via GitHub (Recommended)

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

#### Step 2: Deploy Backend Service
1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select your repository
5. Railway will detect it's a Python app
6. Set the root directory to `/backend`
7. Add environment variables:
   ```
   DATABASE_URL=<your-postgres-url>
   SECRET_KEY=<generate-a-secure-key>
   DEBUG=false
   CORS_ORIGINS=<your-frontend-url>
   PORT=8014
   ```

#### Step 3: Deploy Frontend Service
1. In the same Railway project, click "New" → "Empty Service"
2. Connect the same GitHub repo
3. Set the root directory to `/` (project root)
4. Railway will detect it's a Node.js app
5. Add environment variable:
   ```
   VITE_API_URL=<your-backend-railway-url>
   PORT=5175
   ```

### Option 2: Deploy via Railway CLI

#### Backend Deployment
```bash
cd backend
railway login
railway init
railway up
railway domain  # Get your backend URL
```

#### Frontend Deployment
```bash
cd ..  # Back to project root
railway init
railway up
railway domain  # Get your frontend URL
```

### Option 3: One-Click Deploy Template

Use Railway's FastAPI template:
1. Go to https://railway.com/deploy/-NvLj4
2. Click "Deploy Now"
3. Modify the deployed service with your code

## Configuration Files

### Backend Configuration
- `backend/railway.json` - Railway configuration
- `backend/Procfile` - Process definition
- `backend/runtime.txt` - Python version (3.11)
- `backend/requirements.txt` - Python dependencies

### Frontend Configuration
- `railway.json` - Railway configuration for frontend
- `package.json` - Node.js dependencies

## Environment Variables

### Backend Environment Variables
```env
# Database (Railway provides PostgreSQL)
DATABASE_URL=postgresql://...

# Application
SECRET_KEY=your-secret-key-here
DEBUG=false
CORS_ORIGINS=https://your-frontend.railway.app

# Port (Railway sets this automatically)
PORT=$PORT
```

### Frontend Environment Variables
```env
# API endpoint
VITE_API_URL=https://your-backend.railway.app

# Port (Railway sets this automatically)
PORT=$PORT
```

## Post-Deployment Steps

1. **Database Setup**: Railway provides PostgreSQL. The backend will automatically create tables on startup.

2. **CORS Configuration**: Update the backend's CORS_ORIGINS to include your frontend URL.

3. **Domain Setup**:
   - Railway provides default domains
   - You can add custom domains in project settings

4. **Monitoring**: Use Railway's dashboard to monitor:
   - Deployment logs
   - Resource usage
   - Error tracking

## Troubleshooting

### Common Issues

1. **Port binding errors**
   - Ensure using `$PORT` environment variable
   - Backend: `--port $PORT`
   - Frontend: `--port $PORT`

2. **CORS errors**
   - Update CORS_ORIGINS in backend environment
   - Include full frontend URL with protocol

3. **Database connection**
   - Railway automatically provides DATABASE_URL
   - Ensure using asyncpg for async connections

4. **Build failures**
   - Check runtime.txt for correct Python version
   - Verify all dependencies in requirements.txt

## Service URLs

After deployment, your services will be available at:
- Backend: `https://your-backend.railway.app`
- Frontend: `https://your-frontend.railway.app`

## Useful Commands

```bash
# Check deployment status
railway status

# View logs
railway logs

# Open dashboard
railway open

# Redeploy
railway up

# Environment variables
railway variables
```

## Cost Considerations

Railway offers:
- $5 free credit monthly for new users
- Pay-as-you-go pricing
- Resource-based billing

Estimate for this app:
- Backend: ~$3-5/month
- Frontend: ~$2-3/month
- Database: ~$5/month

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: For app-specific issues