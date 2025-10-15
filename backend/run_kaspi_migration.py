#!/usr/bin/env python3
"""Run Kaspi Pay migration before app startup"""
import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def run_migration():
    """Add Kaspi Pay columns to order table"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("⚠️  No DATABASE_URL found, skipping migration")
        return

    # Convert postgres:// to postgresql+asyncpg://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"🔧 Running Kaspi Pay database migration...")

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        try:
            # Check existing columns
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'order'
                AND column_name IN (
                    'kaspi_payment_id', 'kaspi_payment_status',
                    'kaspi_payment_created_at', 'kaspi_payment_completed_at'
                );
            """)

            result = await session.execute(check_query)
            existing_columns = {row[0] for row in result.fetchall()}

            columns_to_add = [
                ("kaspi_payment_id", "VARCHAR(50)"),
                ("kaspi_payment_status", "VARCHAR(20)"),
                ("kaspi_payment_created_at", "TIMESTAMP"),
                ("kaspi_payment_completed_at", "TIMESTAMP")
            ]

            added = []
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    await session.execute(text(
                        f'ALTER TABLE "order" ADD COLUMN {column_name} {column_type}'
                    ))
                    added.append(column_name)

            await session.commit()

            if added:
                print(f"✅ Added columns: {', '.join(added)}")
            else:
                print("✅ All Kaspi Pay columns already exist")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            await session.rollback()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
