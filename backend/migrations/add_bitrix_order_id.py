"""Migration: Add bitrix_order_id field to Order table for Bitrix sync"""

from sqlalchemy import Column, Integer, text
from alembic import op

async def migrate_add_bitrix_order_id():
    """Add bitrix_order_id column to order table"""
    try:
        # Add column if it doesn't exist
        op.add_column('order', Column('bitrix_order_id', Integer, nullable=True, index=True))
        print("✅ Added bitrix_order_id column to order table")
    except Exception as e:
        # Column might already exist
        if "already exists" in str(e) or "duplicate" in str(e).lower():
            print("⚠️ bitrix_order_id column already exists")
        else:
            raise


# For async/sync migrations in main.py
if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_add_bitrix_order_id())
