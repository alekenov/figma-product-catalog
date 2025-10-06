#!/usr/bin/env python3
"""
Migration: Add delivery settings columns to shop table
Date: 2025-10-06

Adds the following columns to shop table:
- delivery_cost (INTEGER, default 150000)
- free_delivery_amount (INTEGER, default 1000000)
- pickup_available (BOOLEAN, default TRUE)
- delivery_available (BOOLEAN, default TRUE)
- is_active (BOOLEAN, default TRUE)
- city (VARCHAR with ENUM constraint, nullable)

Run with: railway run python migrations/add_shop_delivery_settings.py
"""
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def run_migration():
    """Add delivery settings columns to shop table"""

    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return

    # Convert to async URL
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    print(f"🔗 Connecting to database...")

    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.begin() as conn:
            print("\n🔄 Starting migration: add_shop_delivery_settings")

            # Check if columns already exist
            result = await conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'shop'
                AND column_name IN ('delivery_cost', 'free_delivery_amount', 'pickup_available', 'delivery_available', 'is_active', 'city')
            """))
            existing_columns = {row[0] for row in result}

            # Add delivery_cost column if missing
            if 'delivery_cost' not in existing_columns:
                await conn.execute(text("""
                    ALTER TABLE shop
                    ADD COLUMN delivery_cost INTEGER NOT NULL DEFAULT 150000
                """))
                print("  ✅ Added delivery_cost column")
            else:
                print("  ⏭️  delivery_cost column already exists")

            # Add free_delivery_amount column if missing
            if 'free_delivery_amount' not in existing_columns:
                await conn.execute(text("""
                    ALTER TABLE shop
                    ADD COLUMN free_delivery_amount INTEGER NOT NULL DEFAULT 1000000
                """))
                print("  ✅ Added free_delivery_amount column")
            else:
                print("  ⏭️  free_delivery_amount column already exists")

            # Add pickup_available column if missing
            if 'pickup_available' not in existing_columns:
                await conn.execute(text("""
                    ALTER TABLE shop
                    ADD COLUMN pickup_available BOOLEAN NOT NULL DEFAULT TRUE
                """))
                print("  ✅ Added pickup_available column")
            else:
                print("  ⏭️  pickup_available column already exists")

            # Add delivery_available column if missing
            if 'delivery_available' not in existing_columns:
                await conn.execute(text("""
                    ALTER TABLE shop
                    ADD COLUMN delivery_available BOOLEAN NOT NULL DEFAULT TRUE
                """))
                print("  ✅ Added delivery_available column")
            else:
                print("  ⏭️  delivery_available column already exists")

            # Add is_active column if missing
            if 'is_active' not in existing_columns:
                await conn.execute(text("""
                    ALTER TABLE shop
                    ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE
                """))
                print("  ✅ Added is_active column")
            else:
                print("  ⏭️  is_active column already exists")

            # Add city column if missing (nullable, with ENUM type)
            if 'city' not in existing_columns:
                # First create the ENUM type if it doesn't exist
                await conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'city') THEN
                            CREATE TYPE city AS ENUM ('almaty', 'astana', 'shymkent', 'aktobe', 'taraz');
                        END IF;
                    END $$;
                """))

                await conn.execute(text("""
                    ALTER TABLE shop
                    ADD COLUMN city city
                """))
                print("  ✅ Added city column")
            else:
                print("  ⏭️  city column already exists")

            print("\n✅ Migration complete!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
