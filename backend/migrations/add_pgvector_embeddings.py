#!/usr/bin/env python3
"""
Migration: Add pgvector extension and product_embeddings table

This migration adds support for vector similarity search using pgvector.
It creates:
- pgvector extension (if not exists)
- product_embeddings table for storing image/text embeddings
- Indexes for efficient vector search
- Trigger for auto-updating updated_at timestamp

Run manually:
    python migrations/add_pgvector_embeddings.py

Rollback:
    python migrations/add_pgvector_embeddings.py --rollback
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_session
from core.logging import get_logger

logger = get_logger(__name__)


async def migrate_up(session: AsyncSession):
    """Apply migration: Create pgvector extension and product_embeddings table."""

    logger.info("Starting pgvector embeddings migration...")

    # Step 1: Enable pgvector extension
    logger.info("Enabling pgvector extension...")
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    # Step 2: Create product_embeddings table
    logger.info("Creating product_embeddings table...")
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS product_embeddings (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            embedding vector(512) NOT NULL,
            embedding_type VARCHAR(20) NOT NULL DEFAULT 'image',
            model_version VARCHAR(50) NOT NULL DEFAULT 'vertex-multimodal-001',
            source_url TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),

            CONSTRAINT unique_product_embedding_type UNIQUE (product_id, embedding_type)
        );
    """))

    # Step 3: Create indexes
    logger.info("Creating indexes for product_embeddings...")

    # IVFFlat index for vector similarity search (cosine distance)
    # lists=100 is optimal for ~10k-100k vectors
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS product_embeddings_vector_idx
        ON product_embeddings
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """))

    # Regular indexes for filtering
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS product_embeddings_product_id_idx
        ON product_embeddings(product_id);
    """))

    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS product_embeddings_type_idx
        ON product_embeddings(embedding_type);
    """))

    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS product_embeddings_created_at_idx
        ON product_embeddings(created_at DESC);
    """))

    # Step 4: Create trigger function for auto-updating updated_at
    logger.info("Creating trigger for updated_at column...")
    await session.execute(text("""
        CREATE OR REPLACE FUNCTION update_product_embeddings_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    await session.execute(text("""
        DROP TRIGGER IF EXISTS update_product_embeddings_updated_at_trigger
        ON product_embeddings;
    """))

    await session.execute(text("""
        CREATE TRIGGER update_product_embeddings_updated_at_trigger
            BEFORE UPDATE ON product_embeddings
            FOR EACH ROW
            EXECUTE FUNCTION update_product_embeddings_updated_at();
    """))

    await session.commit()
    logger.info("✅ pgvector embeddings migration completed successfully!")

    # Verify installation
    result = await session.execute(text("""
        SELECT
            COUNT(*) as table_exists
        FROM information_schema.tables
        WHERE table_name = 'product_embeddings';
    """))
    row = result.first()

    if row and row[0] > 0:
        logger.info("✅ Verified: product_embeddings table exists")
    else:
        logger.error("❌ Verification failed: product_embeddings table not found")
        return False

    # Check pgvector extension
    result = await session.execute(text("""
        SELECT
            COUNT(*) as extension_exists
        FROM pg_extension
        WHERE extname = 'vector';
    """))
    row = result.first()

    if row and row[0] > 0:
        logger.info("✅ Verified: pgvector extension enabled")
    else:
        logger.error("❌ Verification failed: pgvector extension not found")
        return False

    return True


async def migrate_down(session: AsyncSession):
    """Rollback migration: Drop product_embeddings table and pgvector extension."""

    logger.warning("Rolling back pgvector embeddings migration...")

    # Drop trigger
    logger.info("Dropping trigger...")
    await session.execute(text("""
        DROP TRIGGER IF EXISTS update_product_embeddings_updated_at_trigger
        ON product_embeddings;
    """))

    await session.execute(text("""
        DROP FUNCTION IF EXISTS update_product_embeddings_updated_at();
    """))

    # Drop table (CASCADE will drop indexes)
    logger.info("Dropping product_embeddings table...")
    await session.execute(text("DROP TABLE IF EXISTS product_embeddings CASCADE;"))

    # Note: We don't drop the pgvector extension as it might be used by other tables
    logger.info("✅ Rollback completed (pgvector extension kept)")

    await session.commit()
    return True


async def main():
    """Run migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="pgvector embeddings migration")
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback migration'
    )
    args = parser.parse_args()

    async for session in get_session():
        try:
            if args.rollback:
                success = await migrate_down(session)
            else:
                success = await migrate_up(session)

            if success:
                logger.info("Migration completed successfully")
                return 0
            else:
                logger.error("Migration failed")
                return 1

        except Exception as e:
            logger.error(f"Migration error: {e}", exc_info=True)
            await session.rollback()
            return 1

        break

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
