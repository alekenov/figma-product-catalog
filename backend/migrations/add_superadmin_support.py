#!/usr/bin/env python3
"""
Migration script to add Superadmin support
This script adds is_superadmin field to User table and is_active field to Shop table.
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
        db_path = os.path.join(os.path.dirname(__file__), "..", "figma_catalog.db")
        conn = sqlite3.connect(db_path)
        return conn


def column_exists(cursor, table_name, column_name):
    """Check if column already exists in table"""
    if DB_TYPE == "postgresql":
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='{table_name}' AND column_name='{column_name}'
            );
        """)
        return cursor.fetchone()[0]
    else:  # SQLite
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns


def run_migration():
    """Run the migration to add superadmin support"""
    detect_database_type()

    print("\n" + "=" * 60)
    print("👑 SUPERADMIN MIGRATION: Add Superadmin Support")
    print("=" * 60 + "\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Add is_superadmin to User table
        print("Step 1: Adding is_superadmin field to User table...")

        user_table_name = '"user"' if DB_TYPE == "postgresql" else "user"

        if not column_exists(cursor, "user", "is_superadmin"):
            cursor.execute(f"""
                ALTER TABLE {user_table_name}
                ADD COLUMN is_superadmin BOOLEAN NOT NULL DEFAULT FALSE;
            """)
            print("✅ Added is_superadmin field to User table")
        else:
            print("ℹ️  is_superadmin field already exists in User table")

        # Step 2: Add is_active to Shop table
        print("\nStep 2: Adding is_active field to Shop table...")

        if not column_exists(cursor, "shop", "is_active"):
            cursor.execute("""
                ALTER TABLE shop
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
            """)
            print("✅ Added is_active field to Shop table")
        else:
            print("ℹ️  is_active field already exists in Shop table")

        # Step 3: Set superadmin for phone 77015211545
        print("\nStep 3: Setting superadmin flag for phone 77015211545...")

        cursor.execute(f"""
            UPDATE {user_table_name}
            SET is_superadmin = TRUE
            WHERE phone = '77015211545';
        """)

        if DB_TYPE == "postgresql":
            cursor.execute(f"""
                SELECT name, phone, is_superadmin
                FROM {user_table_name}
                WHERE phone = '77015211545';
            """)
        else:
            cursor.execute(f"""
                SELECT name, phone, is_superadmin
                FROM {user_table_name}
                WHERE phone = '77015211545';
            """)

        result = cursor.fetchone()
        if result:
            print(f"✅ Superadmin set: {result[0]} ({result[1]}) - is_superadmin={result[2]}")
        else:
            print("⚠️  Warning: User with phone 77015211545 not found")

        # Commit changes
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
