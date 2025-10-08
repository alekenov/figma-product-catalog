"""
Migration script to add client_address table for Phase 2.

Run: python add_client_address_table.py
"""
import asyncio
from sqlalchemy import text
from database import engine

async def create_client_address_table():
    """Create client_address table"""

    async with engine.begin() as conn:
        # Create table
        print("Creating client_address table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS client_address (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(500) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                shop_id INTEGER NOT NULL REFERENCES shop(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT idx_address_telegram_shop UNIQUE (telegram_user_id, shop_id, name)
            )
        """))
        print("✅ client_address table created")

        # Create index 1
        print("Creating telegram index...")
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_client_address_telegram
            ON client_address(telegram_user_id, shop_id)
        """))
        print("✅ telegram index created")

        # Create index 2
        print("Creating name index...")
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_client_address_name
            ON client_address(name)
        """))
        print("✅ name index created")

        # Add cancellation_reason to orders table
        print("Adding cancellation_reason to orders...")
        try:
            await conn.execute(text("""
                ALTER TABLE "order"
                ADD COLUMN cancellation_reason VARCHAR(200)
            """))
            print("✅ cancellation_reason column added")
        except Exception as e:
            # Column might already exist
            print(f"⚠️  cancellation_reason: {e}")

    print("\n🎉 Phase 2 migration completed!")

if __name__ == "__main__":
    asyncio.run(create_client_address_table())
