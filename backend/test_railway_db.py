#!/usr/bin/env python3
"""Test Railway PostgreSQL connection"""

import asyncio
import os
import sys

# Set test DATABASE_URL to ensure we use Railway config
os.environ["DATABASE_URL"] = "postgresql://postgres:BrWQJSWSsYoJhVagWicsDJHMVRNDJUAj@postgres.railway.internal:5432/railway"

try:
    from config_render import settings
    print(f"✓ Config loaded successfully")
    print(f"  Database URL: {settings.database_url}")
    print(f"  Async URL: {settings.database_url_async}")
    print(f"  CORS origins: {settings.cors_origins}")
except Exception as e:
    print(f"✗ Failed to load config: {e}")
    sys.exit(1)

async def test_connection():
    """Test database connection"""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    print("\n🔍 Testing database connection...")

    # Try to connect using internal Railway URL
    internal_url = settings.database_url_async
    print(f"  Using internal URL: {internal_url}")

    try:
        engine = create_async_engine(internal_url, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected successfully!")
            print(f"  PostgreSQL version: {version}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")

        # Try with public URL
        public_url = "postgresql+asyncpg://postgres:BrWQJSWSsYoJhVagWicsDJHMVRNDJUAj@yamanote.proxy.rlwy.net:35081/railway"
        print(f"\n🔍 Trying public URL: {public_url}")

        try:
            engine = create_async_engine(public_url, echo=False)
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"✓ Connected via public URL!")
                print(f"  PostgreSQL version: {version}")
                print(f"\n⚠️  Note: Backend on Railway should use internal URL for better performance")
        except Exception as e2:
            print(f"✗ Public URL also failed: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())