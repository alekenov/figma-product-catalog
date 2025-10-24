"""Migration: Add bitrix_order_id field to Order table for Bitrix sync"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def migrate_add_bitrix_order_id(session: AsyncSession):
    """Add bitrix_order_id column to order table"""
    try:
        # Check if column already exists
        result = await session.execute(
            text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name='order' AND column_name='bitrix_order_id'
            """)
        )

        if result.fetchone():
            print("⚠️  bitrix_order_id column already exists")
            return

        # Add column if it doesn't exist
        await session.execute(
            text("ALTER TABLE \"order\" ADD COLUMN bitrix_order_id INTEGER")
        )
        await session.execute(
            text("CREATE INDEX idx_order_bitrix_id ON \"order\"(bitrix_order_id)")
        )
        await session.commit()
        print("✅ Added bitrix_order_id column to order table")
    except Exception as e:
        await session.rollback()
        print(f"❌ Migration failed: {e}")
        raise


# For async/sync migrations in main.py
if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_add_bitrix_order_id())
