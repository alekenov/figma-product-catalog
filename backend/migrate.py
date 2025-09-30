"""
Auto-migration utilities for adding new columns to existing tables
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


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