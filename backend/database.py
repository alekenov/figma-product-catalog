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


async def drop_all_tables():
    """Drop all tables (use with caution!)"""
    from sqlalchemy import text
    async with engine.begin() as conn:
        print("🗑️  Dropping all tables CASCADE...")
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        print("✅ All tables dropped")


async def create_db_and_tables():
    """Create database tables"""
    # Temporary: Drop all tables if RECREATE_DATABASE flag is set
    if os.getenv("RECREATE_DATABASE") == "true":
        await drop_all_tables()

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def run_migrations():
    """Run database migrations"""
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Migration: Add shop_id column to user table if it doesn't exist
        try:
            await conn.execute(text(
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES shop(id);'
            ))
            await conn.execute(text(
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_superadmin BOOLEAN NOT NULL DEFAULT FALSE;'
            ))
            print("✅ Migration: shop_id and is_superadmin columns added to user table")
        except Exception as e:
            print(f"⚠️  Migration warning: {e}")

        # Migration: Fix user sequence after adding shop_id column
        try:
            await conn.execute(text(
                "SELECT setval('user_id_seq', COALESCE((SELECT MAX(id) FROM \"user\"), 1), true);"
            ))
            print("✅ Migration: user_id_seq reset to correct value")
        except Exception as e:
            print(f"⚠️  Sequence migration warning: {e}")

        # Migration: Add delivery settings columns to shop table
        try:
            # Check existing columns
            result = await conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'shop'
                AND column_name IN ('delivery_cost', 'free_delivery_amount', 'pickup_available', 'delivery_available', 'is_active', 'city')
            """))
            existing_columns = {row[0] for row in result}

            # Add missing columns
            if 'delivery_cost' not in existing_columns:
                await conn.execute(text("ALTER TABLE shop ADD COLUMN delivery_cost INTEGER NOT NULL DEFAULT 150000"))
            if 'free_delivery_amount' not in existing_columns:
                await conn.execute(text("ALTER TABLE shop ADD COLUMN free_delivery_amount INTEGER NOT NULL DEFAULT 1000000"))
            if 'pickup_available' not in existing_columns:
                await conn.execute(text("ALTER TABLE shop ADD COLUMN pickup_available BOOLEAN NOT NULL DEFAULT TRUE"))
            if 'delivery_available' not in existing_columns:
                await conn.execute(text("ALTER TABLE shop ADD COLUMN delivery_available BOOLEAN NOT NULL DEFAULT TRUE"))
            if 'is_active' not in existing_columns:
                await conn.execute(text("ALTER TABLE shop ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))
            if 'city' not in existing_columns:
                # Create ENUM type if needed
                await conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'city') THEN
                            CREATE TYPE city AS ENUM ('almaty', 'astana', 'shymkent', 'aktobe', 'taraz');
                        END IF;
                    END $$;
                """))
                await conn.execute(text("ALTER TABLE shop ADD COLUMN city city"))

            print("✅ Migration: shop delivery settings columns added")
        except Exception as e:
            print(f"⚠️  Shop migration warning: {e}")

        # Migration: Add assignment columns to order table
        try:
            await conn.execute(text('ALTER TABLE "order" ADD COLUMN IF NOT EXISTS assigned_to_id INTEGER REFERENCES "user"(id);'))
            await conn.execute(text('ALTER TABLE "order" ADD COLUMN IF NOT EXISTS courier_id INTEGER REFERENCES "user"(id);'))
            await conn.execute(text('ALTER TABLE "order" ADD COLUMN IF NOT EXISTS assigned_by_id INTEGER REFERENCES "user"(id);'))
            await conn.execute(text('ALTER TABLE "order" ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP;'))
            print("✅ Migration: assignment columns added to order table")
        except Exception as e:
            print(f"⚠️  Order assignment migration warning: {e}")


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()