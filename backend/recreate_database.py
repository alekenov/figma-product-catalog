#!/usr/bin/env python3
"""
Database Recreation Script for Production PostgreSQL

This script drops all tables from the production database to allow SQLModel
to recreate them with the correct schema on next backend startup.

CAUTION: This will DELETE ALL DATA in the production database!
Only run this if you understand the consequences.
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def recreate_database():
    """Drop all tables from production database"""

    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("   Export it first: export DATABASE_URL='<railway-postgres-url>'")
        sys.exit(1)

    # Convert to async URL (postgresql:// -> postgresql+asyncpg://)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        database_url = f"postgresql+asyncpg://{database_url}"

    print("🔌 Connecting to production database...")
    print(f"   URL: {database_url.split('@')[1]}")  # Hide credentials

    # Create async engine
    engine = create_async_engine(database_url, echo=False)

    try:
        async with engine.begin() as conn:
            # Get list of all tables
            result = await conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]

            if not tables:
                print("ℹ️  No tables found in database")
                return

            print(f"\n📋 Found {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   - {table}")

            # Confirm action
            print(f"\n⚠️  WARNING: This will DROP ALL {len(tables)} tables!")
            print("   All data will be permanently deleted.")
            print("   The backend will recreate them on next startup.")
            print("\n   Press Enter to continue, or Ctrl+C to cancel...")
            input()

            # Drop all tables CASCADE
            print("\n🗑️  Dropping all tables...")
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

            print("✅ All tables dropped successfully!")
            print("\n📝 Next steps:")
            print("   1. Enable seeds: railway variables --set RUN_SEEDS=true")
            print("   2. Restart backend: Railway will auto-deploy")
            print("   3. Backend will recreate all tables with correct schema")
            print("   4. Seeds will populate test data (shop_id=8)")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("  Production Database Recreation Script")
    print("=" * 60)
    asyncio.run(recreate_database())
