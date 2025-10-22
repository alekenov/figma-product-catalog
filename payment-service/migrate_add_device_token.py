"""
Migration: Add device_token column to paymentconfig table
"""
import asyncio
from sqlalchemy import text
from database import engine

async def migrate():
    """Add device_token column"""
    async with engine.begin() as conn:
        # Add column if not exists
        await conn.execute(text("""
            ALTER TABLE paymentconfig
            ADD COLUMN IF NOT EXISTS device_token VARCHAR(20);
        """))

        print("✅ Migration completed: device_token column added")

if __name__ == "__main__":
    asyncio.run(migrate())
