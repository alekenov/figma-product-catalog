#!/usr/bin/env python3
"""
Migration script to add image embedding support for visual search
Date: 2025-10-18
Description: Add pgvector extension and image_embedding column to products table
This enables visual similarity search using CLIP embeddings
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
    """Add image embedding support to products table"""
    detect_database_type()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("🔄 Adding image embedding support for visual search...")

        if DB_TYPE == "postgresql":
            # Enable pgvector extension
            print("📦 Enabling pgvector extension...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("✅ pgvector extension enabled")

            # Add image_embedding column (512 dimensions for CLIP ViT-B/32)
            print("📝 Adding image_embedding column...")
            cursor.execute("""
                ALTER TABLE product
                ADD COLUMN IF NOT EXISTS image_embedding vector(512)
            """)
            print("✅ Added image_embedding column")

            # Add embedding_generated_at timestamp for tracking
            print("📝 Adding embedding_generated_at column...")
            cursor.execute("""
                ALTER TABLE product
                ADD COLUMN IF NOT EXISTS embedding_generated_at TIMESTAMP NULL
            """)
            print("✅ Added embedding_generated_at column")

            # Create HNSW index for fast similarity search
            # HNSW (Hierarchical Navigable Small World) is better than IVFFlat for <10k vectors
            print("🔍 Creating HNSW index for fast similarity search...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS product_image_embedding_idx
                ON product
                USING hnsw (image_embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            print("✅ Created HNSW index")

        else:
            # SQLite doesn't support vector types natively
            # We'll just add BLOB column for storing embeddings as JSON
            print("⚠️  SQLite detected - using TEXT column for embeddings (PostgreSQL recommended for production)")
            cursor.execute("PRAGMA table_info(product)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'image_embedding' not in columns:
                cursor.execute("""
                    ALTER TABLE product
                    ADD COLUMN image_embedding TEXT
                """)
                print("✅ Added image_embedding column (as TEXT)")
            else:
                print("⚠️  Column image_embedding already exists")

            if 'embedding_generated_at' not in columns:
                cursor.execute("""
                    ALTER TABLE product
                    ADD COLUMN embedding_generated_at TIMESTAMP NULL
                """)
                print("✅ Added embedding_generated_at column")
            else:
                print("⚠️  Column embedding_generated_at already exists")

        conn.commit()
        print("✅ Migration completed successfully")
        print("\n📊 Next steps:")
        print("   1. Update models/products.py to include new fields")
        print("   2. Run: python scripts/generate_embeddings_batch.py")
        print("   3. Test visual search endpoint")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("Running migration: add_image_embeddings")
    run_migration()
