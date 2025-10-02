#!/usr/bin/env python3
"""
Synchronous migration script to add shop_id column to user table
"""
import os
import psycopg2

def migrate():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return

    # For psycopg2, postgresql+asyncpg:// needs to be postgresql://
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    print(f"Connecting to database...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    try:
        print("Adding shop_id column to user table...")
        cursor.execute(
            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES shop(id);'
        )
        conn.commit()
        print("✅ Migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
