"""
Payment Service - Main Application

Microservice for payment operations (Kaspi Pay + future providers).
Automatically routes payments to correct organization БИН based on shop_id.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from database import create_db_and_tables
from router import payment_router, admin_router
from kaspi_client import get_kaspi_client
from polling_service import PaymentPollingService


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

    # Initialize payment status polling
    scheduler = AsyncIOScheduler()

    # Phase 1: Recent payments (0-10 min) - check every 15 seconds
    scheduler.add_job(
        PaymentPollingService.poll_recent_payments,
        'interval',
        seconds=15,
        id='poll_recent_payments',
        name='Poll Recent Payments (0-10 min)',
        max_instances=1,  # Prevent overlapping runs
        coalesce=True,    # Merge missed runs into one
        misfire_grace_time=30  # Allow 30 seconds grace period
    )

    # Phase 2: Older payments (10 min - 24 hours) - check every 3 minutes
    scheduler.add_job(
        PaymentPollingService.poll_older_payments,
        'interval',
        minutes=3,
        id='poll_older_payments',
        name='Poll Older Payments (10 min - 24 hours)',
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60
    )

    scheduler.start()
    print("✅ Payment status polling started")
    print("   → Phase 1 (0-10 min): every 15 seconds")
    print("   → Phase 2 (10 min - 24h): every 3 minutes")

    yield

    # Shutdown
    print("🛑 Payment Service shutting down...")

    # Shutdown scheduler gracefully
    if scheduler.running:
        scheduler.shutdown(wait=True)
        print("✅ Polling scheduler stopped")

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
