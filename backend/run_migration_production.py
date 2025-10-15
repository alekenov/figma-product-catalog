#!/usr/bin/env python3
"""Run Kaspi Pay migration on production database"""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Production DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:BrWQJSWSsYoJhVagWicsDJHMVRNDJUAj@postgres.railway.internal:5432/railway")

async def run_kaspi_migration():
    """Add Kaspi Pay columns to order table"""
    engine = create_async_engine(DATABASE_URL, echo=True)

    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        try:
            print("🔧 Adding Kaspi Pay columns to order table...")

            # Check which columns exist
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

            print(f"   Existing Kaspi columns: {existing_columns}")

            columns_to_add = [
                ("kaspi_payment_id", "VARCHAR(50)"),
                ("kaspi_payment_status", "VARCHAR(20)"),
                ("kaspi_payment_created_at", "TIMESTAMP"),
                ("kaspi_payment_completed_at", "TIMESTAMP")
            ]

            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    print(f"   Adding column: {column_name}")
                    await session.execute(text(
                        f'ALTER TABLE "order" ADD COLUMN {column_name} {column_type}'
                    ))
                else:
                    print(f"   Column already exists: {column_name}")

            await session.commit()
            print("✅ Kaspi Pay migration completed successfully!")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            await session.rollback()
            raise

        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_kaspi_migration())
