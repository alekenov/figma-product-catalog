#!/usr/bin/env python3
"""
Migration script to add Telegram integration fields to Client table
Date: 2025-10-05
Description: Add telegram_user_id, telegram_username, telegram_first_name for Telegram bot authorization
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
    """Add Telegram fields to client table"""
    detect_database_type()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🔄 Adding Telegram fields to client table...")

        if DB_TYPE == "postgresql":
            # PostgreSQL syntax
            cursor.execute("""
                ALTER TABLE client
                ADD COLUMN IF NOT EXISTS telegram_user_id VARCHAR(50)
            """)

            cursor.execute("""
                ALTER TABLE client
                ADD COLUMN IF NOT EXISTS telegram_username VARCHAR(100)
            """)

            cursor.execute("""
                ALTER TABLE client
                ADD COLUMN IF NOT EXISTS telegram_first_name VARCHAR(100)
            """)

            # Add index for fast telegram_user_id lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_client_telegram_user_id
                ON client (telegram_user_id)
            """)

            # Add composite index for telegram_user_id + shop_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_client_telegram_user_shop
                ON client (telegram_user_id, shop_id)
            """)

            print("✅ Added Telegram fields and indexes (PostgreSQL)")

        else:
            # SQLite syntax - check if columns exist first
            cursor.execute("PRAGMA table_info(client)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'telegram_user_id' not in columns:
                cursor.execute("""
                    ALTER TABLE client
                    ADD COLUMN telegram_user_id VARCHAR(50)
                """)
                print("✅ Added telegram_user_id column")

            if 'telegram_username' not in columns:
                cursor.execute("""
                    ALTER TABLE client
                    ADD COLUMN telegram_username VARCHAR(100)
                """)
                print("✅ Added telegram_username column")

            if 'telegram_first_name' not in columns:
                cursor.execute("""
                    ALTER TABLE client
                    ADD COLUMN telegram_first_name VARCHAR(100)
                """)
                print("✅ Added telegram_first_name column")

            # Add indexes (SQLite doesn't support IF NOT EXISTS for CREATE INDEX before 3.32.0)
            try:
                cursor.execute("""
                    CREATE INDEX idx_client_telegram_user_id
                    ON client (telegram_user_id)
                """)
                print("✅ Created idx_client_telegram_user_id index")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("⚠️  Index idx_client_telegram_user_id already exists")
                else:
                    raise

            try:
                cursor.execute("""
                    CREATE INDEX idx_client_telegram_user_shop
                    ON client (telegram_user_id, shop_id)
                """)
                print("✅ Created idx_client_telegram_user_shop index")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("⚠️  Index idx_client_telegram_user_shop already exists")
                else:
                    raise

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
    print("Running migration: add_telegram_to_client")
    run_migration()
