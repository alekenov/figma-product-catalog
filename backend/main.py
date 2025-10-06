from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
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
from api.shops import router as shops_router  # Public marketplace shops API
from api.reviews import router as reviews_router
from api.content import router as content_router
from api.superadmin import router as superadmin_router
from api.telegram_clients import router as telegram_clients_router


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
print(f"🌐 CORS Origins configured: {getattr(settings, 'cors_origins', 'NOT SET')}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'cors_origins', []),
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Figma Product Catalog API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/debug/db-stats")
async def get_db_stats(session: AsyncSession = Depends(get_session)):
    """Get database statistics for debugging"""
    from sqlalchemy import text, select, func
    from models import Shop, User, Product, Order

    async with session.begin():
        # Count records
        shop_count = (await session.execute(select(func.count()).select_from(Shop))).scalar()
        user_count = (await session.execute(select(func.count()).select_from(User))).scalar()
        product_count = (await session.execute(select(func.count()).select_from(Product))).scalar()
        order_count = (await session.execute(select(func.count()).select_from(Order))).scalar()

        # Get recent orders
        recent_orders = []
        result = await session.execute(
            select(Order.tracking_id, Order.orderNumber, Order.status)
            .order_by(Order.created_at.desc())
            .limit(5)
        )
        for row in result:
            recent_orders.append({
                "tracking_id": row[0],
                "order_number": row[1],
                "status": row[2]
            })

    return {
        "database": "connected",
        "counts": {
            "shops": shop_count,
            "users": user_count,
            "products": product_count,
            "orders": order_count
        },
        "recent_orders": recent_orders
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