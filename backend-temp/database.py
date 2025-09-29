from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
import os

# Use Render config if DATABASE_URL is set, otherwise use SQLite for local dev
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings

# Create async engine
# Use database_url_async for async PostgreSQL support
database_url = getattr(settings, 'database_url_async', settings.database_url)
engine = create_async_engine(
    database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    future=True
)

# Create session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_db_and_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()