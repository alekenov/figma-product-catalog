"""
Auto-migration utilities for adding new columns to existing tables
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import os


async def migrate_phase1_columns(session: AsyncSession):
    """
    Add Phase 1 columns to product table if they don't exist.
    This is safe to run multiple times - checks existence before adding.
    """
    try:
        # Check which columns already exist
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'product'
            AND column_name IN ('tags', 'cities', 'is_featured', 'manufacturing_time');
        """)

        result = await session.execute(check_query)
        existing_columns = {row[0] for row in result.fetchall()}

        migrations_applied = []

        # Add missing columns
        if 'tags' not in existing_columns:
            await session.execute(text(
                "ALTER TABLE product ADD COLUMN tags JSON DEFAULT '[]'::json"
            ))
            migrations_applied.append("tags")

        if 'cities' not in existing_columns:
            await session.execute(text(
                "ALTER TABLE product ADD COLUMN cities JSON DEFAULT '[]'::json"
            ))
            migrations_applied.append("cities")

        if 'is_featured' not in existing_columns:
            await session.execute(text(
                "ALTER TABLE product ADD COLUMN is_featured BOOLEAN DEFAULT false"
            ))
            migrations_applied.append("is_featured")

        if 'manufacturing_time' not in existing_columns:
            await session.execute(text(
                "ALTER TABLE product ADD COLUMN manufacturing_time INTEGER DEFAULT 2"
            ))
            migrations_applied.append("manufacturing_time")

        await session.commit()

        if migrations_applied:
            print(f"✅ Applied Phase 1 migrations: {', '.join(migrations_applied)}")
        else:
            print("✅ Phase 1 schema up to date")

    except Exception as e:
        print(f"⚠️  Migration warning: {e}")
        # Don't fail startup if migration has issues
        await session.rollback()


async def migrate_phase3_order_columns(session: AsyncSession):
    """
    Add Phase 3 columns to order table for checkout flow.
    Safe to run multiple times - uses SQLite-compatible column existence check.
    """
    try:
        # SQLite-compatible way to check if columns exist
        check_query = text("PRAGMA table_info(`order`)")
        result = await session.execute(check_query)
        existing_columns = {row[1] for row in result.fetchall()}

        migrations_applied = []

        # Add Phase 3 checkout flow columns
        columns_to_add = [
            ("recipient_name", "VARCHAR(100)"),
            ("recipient_phone", "VARCHAR(20)"),
            ("sender_phone", "VARCHAR(20)"),
            ("pickup_address", "VARCHAR(500)"),
            ("delivery_type", "VARCHAR(50)"),
            ("scheduled_time", "VARCHAR(100)"),
            ("payment_method", "VARCHAR(50)"),
            ("order_comment", "VARCHAR(1000)"),
            ("bonus_points", "INTEGER DEFAULT 0")
        ]

        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                await session.execute(text(
                    f"ALTER TABLE `order` ADD COLUMN {column_name} {column_type}"
                ))
                migrations_applied.append(column_name)

        await session.commit()

        if migrations_applied:
            print(f"✅ Applied Phase 3 migrations: {', '.join(migrations_applied)}")
        else:
            print("✅ Phase 3 Order schema up to date")

    except Exception as e:
        print(f"⚠️  Phase 3 migration warning: {e}")
        # Don't fail startup if migration has issues
        await session.rollback()


async def migrate_tracking_id(session: AsyncSession):
    """
    Add tracking_id column to order table and populate with random 9-digit IDs.
    Safe to run multiple times - checks if column exists and skips if already present.
    """
    try:
        import random

        # Check if tracking_id column exists
        check_query = text("PRAGMA table_info(`order`)")
        result = await session.execute(check_query)
        existing_columns = {row[1] for row in result.fetchall()}

        if 'tracking_id' in existing_columns:
            print("✅ tracking_id column already exists")
            return

        # Add tracking_id column
        await session.execute(text(
            "ALTER TABLE `order` ADD COLUMN tracking_id VARCHAR(9)"
        ))
        print("✅ Added tracking_id column")

        # Get all existing orders
        orders_result = await session.execute(text("SELECT id FROM `order`"))
        orders = orders_result.fetchall()

        if orders:
            print(f"   Populating tracking_id for {len(orders)} existing orders...")

            # Generate unique tracking IDs for existing orders
            used_ids = set()
            for order_row in orders:
                order_id = order_row[0]

                # Generate unique tracking ID
                while True:
                    tracking_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])
                    if tracking_id not in used_ids:
                        used_ids.add(tracking_id)
                        break

                # Update order with tracking ID
                await session.execute(text(
                    f"UPDATE `order` SET tracking_id = '{tracking_id}' WHERE id = {order_id}"
                ))

        # Add unique constraint and index
        await session.execute(text(
            "CREATE UNIQUE INDEX idx_order_tracking_id ON `order` (tracking_id)"
        ))

        await session.commit()
        print(f"✅ Populated tracking_id for {len(orders)} orders")

    except Exception as e:
        print(f"⚠️  tracking_id migration warning: {e}")
        # Don't fail startup if migration has issues
        await session.rollback()