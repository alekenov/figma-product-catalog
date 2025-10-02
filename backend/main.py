from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
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
from api.reviews import router as reviews_router
from api.content import router as content_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Figma Product Catalog API...")
    await create_db_and_tables()
    print("📊 Database tables created")

    # Run schema migrations
    await run_migrations()

    # Run data migrations
    async for session in get_session():
        await migrate_phase1_columns(session)
        await migrate_phase3_order_columns(session)
        await migrate_tracking_id(session)

        # Run seeds in local development only
        if not os.getenv("DATABASE_URL"):
            from seeds import seed_all
            await seed_all(session)

        break

    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="Backend API for Kazakhstan flower shop catalog",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
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
    reviews_router,
    prefix=f"{settings.api_v1_prefix}/reviews",
    tags=["reviews"]
)

app.include_router(
    content_router,
    prefix=f"{settings.api_v1_prefix}",
    tags=["content"]
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
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.port,
        reload=settings.debug
    )