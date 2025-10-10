from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Configure structured logging FIRST
from core.logging import configure_logging, get_logger

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Use Render config if DATABASE_URL is set, otherwise use SQLite for local dev
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings

from database import create_db_and_tables, get_session, run_migrations
from models import OrderCounter, WarehouseItem, ProductRecipe  # Import to register models for table creation
from migrate import migrate_phase1_columns, migrate_phase3_order_columns, migrate_tracking_id
from api.products import router as products_router  # Now imports from modular package
from api.orders import router as orders_router
from api.warehouse import router as warehouse_router
from api.recipes import router as recipes_router
from api.inventory import router as inventory_router  # Now imports from modular package
from api.clients import router as clients_router
from api.auth import router as auth_router
from api.profile import router as profile_router
from api.shop import router as shop_router
from api.shops import router as shops_router  # Public marketplace shops API
from api.reviews import router as reviews_router
from api.content import router as content_router
from api.superadmin import router as superadmin_router
from api.telegram_clients import router as telegram_clients_router
from api.delivery import router as delivery_router
from api.colors import router as colors_router
from api.chats import router as chats_router

# Import middleware
from core.middleware import RequestIDMiddleware
from core.metrics import PrometheusMiddleware, metrics_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("backend_starting",
                project_name=settings.project_name,
                database_configured=bool(os.getenv("DATABASE_URL")))

    await create_db_and_tables()
    logger.info("database_tables_created")

    # Run schema migrations
    await run_migrations()

    # Run data migrations
    async for session in get_session():
        await migrate_phase1_columns(session)
        await migrate_phase3_order_columns(session)
        await migrate_tracking_id(session)

        # Run seeds in local development or if RUN_SEEDS flag is set
        if not os.getenv("DATABASE_URL") or os.getenv("RUN_SEEDS") == "true":
            from seeds import seed_all
            await seed_all(session)
            logger.info("seeds_applied")

        break

    logger.info("backend_started_successfully")
    yield
    # Shutdown
    logger.info("backend_shutting_down")


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="Backend API for Kazakhstan flower shop catalog",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request ID tracking middleware (add FIRST for all requests)
app.add_middleware(RequestIDMiddleware)

# Prometheus metrics middleware (after RequestID for request_id in logs)
app.add_middleware(PrometheusMiddleware)

# CORS middleware
cors_origins = getattr(settings, 'cors_origins', [])
logger.info("cors_configured", origins_count=len(cors_origins) if cors_origins else 0)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
)


# API Routes
app.include_router(
    products_router,
    prefix=f"{settings.api_v1_prefix}/products",
    tags=["products"]
)

app.include_router(
    orders_router,
    prefix=f"{settings.api_v1_prefix}/orders",
    tags=["orders"]
)

app.include_router(
    warehouse_router,
    prefix=f"{settings.api_v1_prefix}/warehouse",
    tags=["warehouse"]
)

app.include_router(
    recipes_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["recipes"]
)

app.include_router(
    inventory_router,
    prefix=f"{settings.api_v1_prefix}/inventory",
    tags=["inventory"]
)

app.include_router(
    clients_router,
    prefix=f"{settings.api_v1_prefix}/clients",
    tags=["clients"]
)

app.include_router(
    auth_router,
    prefix=f"{settings.api_v1_prefix}/auth",
    tags=["authentication"]
)

app.include_router(
    profile_router,
    prefix=f"{settings.api_v1_prefix}/profile",
    tags=["profile", "team"]
)

app.include_router(
    shop_router,
    prefix=f"{settings.api_v1_prefix}/shop",
    tags=["shop settings"]
)

app.include_router(
    shops_router,
    prefix=f"{settings.api_v1_prefix}/shops",
    tags=["shops", "marketplace"]
)

app.include_router(
    reviews_router,
    prefix=f"{settings.api_v1_prefix}/reviews",
    tags=["reviews"]
)

app.include_router(
    content_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["content"]
)

app.include_router(
    superadmin_router,
    prefix=f"{settings.api_v1_prefix}/superadmin",
    tags=["superadmin"]
)

app.include_router(
    telegram_clients_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["telegram"]
)

app.include_router(
    delivery_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["delivery"]
)

app.include_router(
    colors_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["colors"]
)

app.include_router(
    chats_router,
    prefix=f"{settings.api_v1_prefix}/chats",
    tags=["chats", "ai-agent"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Figma Product Catalog API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway/monitoring systems.
    Checks database connectivity and overall service health.
    """
    from datetime import datetime

    db_status = "unknown"
    db_error = None

    try:
        # Test database connection with a simple query
        async for session in get_session():
            from sqlmodel import text
            await session.execute(text("SELECT 1"))
            db_status = "healthy"
            break
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)[:100]  # Limit error message length

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    response = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "backend",
        "version": "1.0.0",
        "checks": {
            "database": {
                "status": db_status,
                "error": db_error
            }
        }
    }

    # Return 503 if unhealthy (for load balancers)
    status_code = 200 if overall_status == "healthy" else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(content=response, status_code=status_code)


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Railway/Kubernetes.
    Returns 200 when service is ready to accept traffic, 503 otherwise.
    """
    checks = {
        "database": False
    }

    try:
        async for session in get_session():
            from sqlmodel import text
            await session.execute(text("SELECT 1"))
            checks["database"] = True
            break
    except Exception:
        pass

    all_ready = all(checks.values())

    response = {
        "ready": all_ready,
        "checks": checks
    }

    status_code = 200 if all_ready else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(content=response, status_code=status_code)


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Exposes application metrics in Prometheus text format:
    - http_requests_total: Total HTTP requests by method, endpoint, status
    - http_request_duration_seconds: HTTP request latency histogram
    - http_errors_total: HTTP errors by method, endpoint, error type

    Example Prometheus scrape config:
        scrape_configs:
          - job_name: 'flower-shop-backend'
            scrape_interval: 15s
            static_configs:
              - targets: ['localhost:8014']

    Example Grafana queries:
        # Request rate:
        rate(http_requests_total[5m])

        # P95 latency:
        histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

        # Error rate:
        rate(http_errors_total[5m])
    """
    return await metrics_handler()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.port,
        reload=settings.debug
    )