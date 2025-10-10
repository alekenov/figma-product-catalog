#!/usr/bin/env python3
"""
Migration script to add chat_session and chat_message tables
Date: 2025-10-10
Description: Add tables for AI agent chat monitoring
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
    """Create chat_session and chat_message tables"""
    detect_database_type()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🔄 Creating chat_session table...")

        if DB_TYPE == "postgresql":
            # PostgreSQL syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_session (
                    id SERIAL PRIMARY KEY,
                    shop_id INTEGER NOT NULL REFERENCES shop(id),
                    user_id VARCHAR(255) NOT NULL,
                    channel VARCHAR(50) NOT NULL,
                    customer_name VARCHAR(255),
                    customer_phone VARCHAR(50),
                    message_count INTEGER DEFAULT 0,
                    total_cost_usd DECIMAL(10, 6) DEFAULT 0.0,
                    created_order BOOLEAN DEFAULT FALSE,
                    order_id INTEGER REFERENCES "order"(id),
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_session_shop_id
                ON chat_session (shop_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_session_user_id
                ON chat_session (user_id)
            """)

            print("✅ Created chat_session table")

            print("🔄 Creating chat_message table...")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_message (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES chat_session(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    message_metadata JSONB,
                    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_message_session_id
                ON chat_message (session_id)
            """)

            print("✅ Created chat_message table")

        else:
            # SQLite syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shop_id INTEGER NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    channel VARCHAR(50) NOT NULL,
                    customer_name VARCHAR(255),
                    customer_phone VARCHAR(50),
                    message_count INTEGER DEFAULT 0,
                    total_cost_usd DECIMAL(10, 6) DEFAULT 0.0,
                    created_order BOOLEAN DEFAULT 0,
                    order_id INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (shop_id) REFERENCES shop(id),
                    FOREIGN KEY (order_id) REFERENCES "order"(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_session_shop_id
                ON chat_session (shop_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_session_user_id
                ON chat_session (user_id)
            """)

            print("✅ Created chat_session table")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    message_metadata TEXT,
                    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_session(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_message_session_id
                ON chat_message (session_id)
            """)

            print("✅ Created chat_message table")

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
    print("Running migration: add_chat_tables")
    run_migration()
