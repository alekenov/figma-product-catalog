#!/usr/bin/env python3
"""
Migration script to add AI Agent clarification flags to Order table
Date: 2025-10-15
Description: Add ask_delivery_address and ask_delivery_time fields for AI bot integration
These flags allow the bot to create orders while marking that delivery address/time need clarification
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
    """Add ask_delivery_address and ask_delivery_time columns to order table"""
    detect_database_type()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🔄 Adding AI Agent clarification flags to order table...")

        if DB_TYPE == "postgresql":
            # PostgreSQL syntax
            cursor.execute("""
                ALTER TABLE "order"
                ADD COLUMN IF NOT EXISTS ask_delivery_address BOOLEAN DEFAULT false
            """)
            print("✅ Added ask_delivery_address column")

            cursor.execute("""
                ALTER TABLE "order"
                ADD COLUMN IF NOT EXISTS ask_delivery_time BOOLEAN DEFAULT false
            """)
            print("✅ Added ask_delivery_time column")

        else:
            # SQLite syntax - check if columns exist first
            cursor.execute("PRAGMA table_info(\"order\")")
            columns = [col[1] for col in cursor.fetchall()]

            if 'ask_delivery_address' not in columns:
                cursor.execute("""
                    ALTER TABLE "order"
                    ADD COLUMN ask_delivery_address BOOLEAN DEFAULT 0
                """)
                print("✅ Added ask_delivery_address column")
            else:
                print("⚠️  Column ask_delivery_address already exists")

            if 'ask_delivery_time' not in columns:
                cursor.execute("""
                    ALTER TABLE "order"
                    ADD COLUMN ask_delivery_time BOOLEAN DEFAULT 0
                """)
                print("✅ Added ask_delivery_time column")
            else:
                print("⚠️  Column ask_delivery_time already exists")

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
    print("Running migration: add_ai_agent_flags")
    run_migration()
