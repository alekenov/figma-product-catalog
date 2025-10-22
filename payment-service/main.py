"""
Payment Service - Main Application

Microservice for payment operations (Kaspi Pay + future providers).
Automatically routes payments to correct organization БИН based on shop_id.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import create_db_and_tables
from router import payment_router, admin_router
from kaspi_client import get_kaspi_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    # Startup
    print("🚀 Payment Service starting...")
    print(f"📊 Database: {settings.database_url}")
    print(f"🏦 Production API: {settings.production_api_url}")

    # Create database tables
    create_db_and_tables()
    print("✅ Database tables created")

    yield

    # Shutdown
    print("🛑 Payment Service shutting down...")
    kaspi_client = get_kaspi_client()
    await kaspi_client.close()
    print("✅ Kaspi client closed")


# Create FastAPI app
app = FastAPI(
    title="Payment Service",
    description="Microservice for payment operations with automatic БИН routing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payment_router)
app.include_router(admin_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "payment-service",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Payment Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "payments": "/payments/kaspi",
            "admin": "/admin"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
