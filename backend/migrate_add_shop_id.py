#!/usr/bin/env python3
"""
Migration script to add shop_id column to user table
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def migrate():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return

    # Convert postgresql:// to postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Connecting to database...")
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        print("Adding shop_id column to user table...")
        await conn.execute(text(
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES shop(id);'
        ))
        print("✅ Migration completed successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
