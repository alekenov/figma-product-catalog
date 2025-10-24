"""Migration: Add bitrix_order_id field to Order table for Bitrix sync"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def migrate_add_bitrix_order_id(session: AsyncSession):
    """Add bitrix_order_id column to order table"""
    try:
        # Try to add column - if it already exists, the error is silently caught
        try:
            await session.execute(
                text('ALTER TABLE "order" ADD COLUMN bitrix_order_id INTEGER')
            )
            print("✅ Added bitrix_order_id column to order table")
        except Exception as column_error:
            # Column likely already exists, skip
            if "already exists" in str(column_error) or "duplicate" in str(column_error).lower():
                print("⚠️  bitrix_order_id column already exists")
            else:
                raise

        # Try to create index - if it already exists, that's fine
        try:
            await session.execute(
                text("CREATE INDEX idx_order_bitrix_id ON \"order\"(bitrix_order_id)")
            )
        except Exception:
            # Index may already exist, that's okay
            pass

        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"⚠️  Migration warning: {e}")
        # Don't raise - let the app continue even if migration fails


# For async/sync migrations in main.py
if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_add_bitrix_order_id())
