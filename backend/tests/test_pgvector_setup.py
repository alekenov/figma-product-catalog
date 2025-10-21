"""
Test pgvector setup and vector similarity search.

This test verifies:
1. pgvector extension is enabled
2. product_embeddings table exists with correct schema
3. Vector insertion works
4. Cosine similarity search works
5. Indexes are created correctly

Run:
    pytest tests/test_pgvector_setup.py -v
"""

import pytest
import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Product, ProductEmbedding


@pytest.mark.asyncio
async def test_pgvector_extension_enabled():
    """Test that pgvector extension is enabled."""
    async for session in get_session():
        result = await session.execute(text("""
            SELECT COUNT(*) as count
            FROM pg_extension
            WHERE extname = 'vector';
        """))
        row = result.first()

        assert row is not None, "Query returned no results"
        assert row[0] == 1, "pgvector extension not enabled"
        break


@pytest.mark.asyncio
async def test_product_embeddings_table_exists():
    """Test that product_embeddings table exists with correct schema."""
    async for session in get_session():
        # Check table exists
        result = await session.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_name = 'product_embeddings';
        """))
        row = result.first()
        assert row[0] == 1, "product_embeddings table does not exist"

        # Check columns
        result = await session.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'product_embeddings'
            ORDER BY ordinal_position;
        """))
        columns = {row[0]: row[1] for row in result}

        # Verify required columns
        assert 'id' in columns, "Missing id column"
        assert 'product_id' in columns, "Missing product_id column"
        assert 'embedding' in columns, "Missing embedding column"
        assert 'embedding_type' in columns, "Missing embedding_type column"
        assert 'model_version' in columns, "Missing model_version column"
        assert 'created_at' in columns, "Missing created_at column"
        assert 'updated_at' in columns, "Missing updated_at column"

        break


@pytest.mark.asyncio
async def test_vector_indexes_exist():
    """Test that vector similarity indexes exist."""
    async for session in get_session():
        result = await session.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'product_embeddings'
            ORDER BY indexname;
        """))
        indexes = [row[0] for row in result]

        # Check for vector index
        assert any('vector' in idx for idx in indexes), \
            "Vector similarity index not found"

        # Check for product_id index
        assert any('product_id' in idx for idx in indexes), \
            "Product ID index not found"

        break


@pytest.mark.asyncio
async def test_insert_and_query_vector():
    """Test inserting and querying vectors."""
    async for session in get_session():
        # Create test product first
        test_product = Product(
            shop_id=8,
            name="Test Product for Vector Search",
            price=100000,
            enabled=True,
            product_type="flowers"
        )
        session.add(test_product)
        await session.flush()

        # Generate random 512D vector (normalized)
        random_vector = np.random.randn(512).astype(float)
        random_vector = random_vector / np.linalg.norm(random_vector)  # L2 normalize
        random_vector = random_vector.tolist()

        # Insert embedding
        embedding = ProductEmbedding(
            product_id=test_product.id,
            embedding=random_vector,
            embedding_type="image",
            model_version="test-model",
            source_url="https://test.com/image.png"
        )
        session.add(embedding)
        await session.commit()

        # Query back
        result = await session.execute(
            text("""
                SELECT id, product_id, embedding, embedding_type
                FROM product_embeddings
                WHERE product_id = :product_id
            """),
            {"product_id": test_product.id}
        )
        row = result.first()

        assert row is not None, "Embedding not inserted"
        assert row[1] == test_product.id, "Wrong product_id"
        assert row[3] == "image", "Wrong embedding_type"

        # Verify vector dimensions
        stored_vector = row[2]  # pgvector returns as string "[0.1, 0.2, ...]"
        if isinstance(stored_vector, str):
            # Parse vector string
            import json
            stored_vector = json.loads(stored_vector.replace('[', '[').replace(']', ']'))

        assert len(stored_vector) == 512, f"Wrong vector dimensions: {len(stored_vector)}"

        # Cleanup
        await session.delete(embedding)
        await session.delete(test_product)
        await session.commit()

        break


@pytest.mark.asyncio
async def test_cosine_similarity_search():
    """Test cosine similarity search with pgvector."""
    async for session in get_session():
        # Create 3 test products with embeddings
        products = []
        embeddings_data = []

        for i in range(3):
            product = Product(
                shop_id=8,
                name=f"Test Product {i}",
                price=100000 * (i + 1),
                enabled=True,
                product_type="flowers"
            )
            session.add(product)
            await session.flush()
            products.append(product)

            # Create similar but different vectors
            base_vector = np.random.randn(512).astype(float)
            # Add small perturbation to make them similar but not identical
            perturbed = base_vector + np.random.randn(512) * 0.1
            normalized = perturbed / np.linalg.norm(perturbed)

            embedding = ProductEmbedding(
                product_id=product.id,
                embedding=normalized.tolist(),
                embedding_type="image",
                model_version="test-model"
            )
            session.add(embedding)
            embeddings_data.append(normalized.tolist())

        await session.commit()

        # Query vector (use first embedding as query)
        query_vector = embeddings_data[0]

        # Perform cosine similarity search
        # <=> is cosine distance operator in pgvector
        # 1 - distance = cosine similarity
        result = await session.execute(
            text("""
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    1 - (pe.embedding <=> :query_vector::vector) AS similarity
                FROM products p
                INNER JOIN product_embeddings pe ON p.id = pe.product_id
                WHERE p.id = ANY(:product_ids)
                ORDER BY pe.embedding <=> :query_vector::vector ASC
                LIMIT 10
            """),
            {
                "query_vector": str(query_vector),  # Convert to pgvector format
                "product_ids": [p.id for p in products]
            }
        )

        results = result.all()

        # Verify results
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"

        # First result should be the query vector itself (similarity = 1.0)
        assert results[0][0] == products[0].id, "First result should be query product"
        assert results[0][3] >= 0.99, f"Self-similarity should be ~1.0, got {results[0][3]}"

        # All results should have similarity > 0
        for row in results:
            assert row[3] > 0, f"Similarity should be positive, got {row[3]}"
            assert row[3] <= 1.0, f"Similarity should be <= 1.0, got {row[3]}"

        # Results should be ordered by similarity (descending)
        similarities = [row[3] for row in results]
        assert similarities == sorted(similarities, reverse=True), \
            "Results not sorted by similarity"

        # Cleanup
        for product in products:
            await session.delete(product)
        await session.commit()

        break


@pytest.mark.asyncio
async def test_updated_at_trigger():
    """Test that updated_at trigger works correctly."""
    async for session in get_session():
        # Create test product
        product = Product(
            shop_id=8,
            name="Test Product for Trigger",
            price=100000,
            enabled=True,
            product_type="flowers"
        )
        session.add(product)
        await session.flush()

        # Create embedding
        vector = (np.random.randn(512) / np.linalg.norm(np.random.randn(512))).tolist()
        embedding = ProductEmbedding(
            product_id=product.id,
            embedding=vector,
            embedding_type="image",
            model_version="test-model"
        )
        session.add(embedding)
        await session.commit()

        # Get initial timestamps
        await session.refresh(embedding)
        created_at = embedding.created_at
        updated_at_initial = embedding.updated_at

        # Update embedding
        import asyncio
        await asyncio.sleep(0.1)  # Small delay to ensure timestamp changes

        embedding.model_version = "test-model-v2"
        await session.commit()
        await session.refresh(embedding)

        # Verify updated_at changed
        assert embedding.created_at == created_at, "created_at should not change"
        assert embedding.updated_at > updated_at_initial, \
            "updated_at should be updated by trigger"

        # Cleanup
        await session.delete(embedding)
        await session.delete(product)
        await session.commit()

        break


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
