#!/usr/bin/env python3
"""
Migration script to add telegram_user_id to Order table
Date: 2025-10-05
Description: Add telegram_user_id field for Telegram bot integration
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Environment detection
DB_TYPE = None  # Will be set based on environment


def detect_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    global DB_TYPE

    # Check if DATABASE_URL is set (PostgreSQL on Railway)
    if os.getenv("DATABASE_URL"):
        DB_TYPE = "postgresql"
    else:
        DB_TYPE = "sqlite"

    print(f"Detected database type: {DB_TYPE}")
    return DB_TYPE


def get_db_connection():
    """Get database connection based on environment"""
    if DB_TYPE == "postgresql":
        import psycopg2
        from urllib.parse import urlparse

        database_url = os.getenv("DATABASE_URL")
        # Parse connection string
        result = urlparse(database_url)

        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    else:  # SQLite
        import sqlite3
        # Use figma_catalog.db in production
        db_file = "figma_catalog.db"
        return sqlite3.connect(db_file)


def run_migration():
    """Add telegram_user_id column to order table"""
    detect_database_type()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🔄 Adding telegram_user_id column to order table...")

        if DB_TYPE == "postgresql":
            # PostgreSQL syntax
            cursor.execute("""
                ALTER TABLE "order"
                ADD COLUMN IF NOT EXISTS telegram_user_id VARCHAR(50)
            """)

            # Add index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_order_telegram_user_id
                ON "order" (telegram_user_id)
            """)
        else:
            # SQLite syntax - check if column exists first
            cursor.execute("PRAGMA table_info(\"order\")")
            columns = [col[1] for col in cursor.fetchall()]

            if 'telegram_user_id' not in columns:
                cursor.execute("""
                    ALTER TABLE "order"
                    ADD COLUMN telegram_user_id VARCHAR(50)
                """)
                print("✅ Added telegram_user_id column")

                # SQLite doesn't support IF NOT EXISTS for indexes
                cursor.execute("""
                    CREATE INDEX idx_order_telegram_user_id
                    ON "order" (telegram_user_id)
                """)
                print("✅ Created index on telegram_user_id")
            else:
                print("⚠️  Column telegram_user_id already exists")

        conn.commit()
        print("✅ Migration completed successfully")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("Running migration: add_telegram_user_id")
    run_migration()
