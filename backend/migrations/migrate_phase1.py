"""
Quick migration script to add Phase 1 columns to Railway Postgres
Run this once to update the production database schema
"""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Get DATABASE_URL from Railway
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Convert postgres:// to postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

async def migrate():
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        print("🔧 Adding Phase 1 columns to product table...")

        # Check if columns already exist
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'product'
            AND column_name IN ('tags', 'cities', 'is_featured', 'manufacturing_time');
        """)

        result = await conn.execute(check_query)
        existing_columns = {row[0] for row in result.fetchall()}

        # Add missing columns
        if 'tags' not in existing_columns:
            await conn.execute(text("ALTER TABLE product ADD COLUMN tags JSON DEFAULT '[]'::json"))
            print("✅ Added 'tags' column")

        if 'cities' not in existing_columns:
            await conn.execute(text("ALTER TABLE product ADD COLUMN cities JSON DEFAULT '[]'::json"))
            print("✅ Added 'cities' column")

        if 'is_featured' not in existing_columns:
            await conn.execute(text("ALTER TABLE product ADD COLUMN is_featured BOOLEAN DEFAULT false"))
            print("✅ Added 'is_featured' column")

        if 'manufacturing_time' not in existing_columns:
            await conn.execute(text("ALTER TABLE product ADD COLUMN manufacturing_time INTEGER DEFAULT 2"))
            print("✅ Added 'manufacturing_time' column")

        print("🎉 Migration completed successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())