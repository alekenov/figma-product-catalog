from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config_sqlite import settings
from database import create_db_and_tables
from api.products import router as products_router
from api.orders import router as orders_router
from api.warehouse import router as warehouse_router
from api.recipes import router as recipes_router
from api.inventory import router as inventory_router
from api.clients import router as clients_router
from api.auth import router as auth_router
from api.profile import router as profile_router
from api.shop import router as shop_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Figma Product Catalog API...")
    await create_db_and_tables()
    print("📊 Database tables created")
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
        host="0.0.0.0",
        port=8014,  # Default port changed to 8014
        reload=settings.debug
    )