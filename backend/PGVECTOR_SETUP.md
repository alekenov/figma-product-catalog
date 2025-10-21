# PostgreSQL + pgvector Setup Guide

## Phase 1 Complete! ✅

This guide describes the setup of PostgreSQL vector similarity search using pgvector extension.

---

## What Was Added

### 1. Database Migration
- **File**: `migrations/add_pgvector_embeddings.py`
- **Creates**:
  - `vector` extension for PostgreSQL
  - `product_embeddings` table with 512D vector column
  - IVFFlat index for fast cosine similarity search
  - Indexes for filtering (product_id, embedding_type)
  - Trigger for auto-updating `updated_at` timestamp

### 2. SQLAlchemy Model
- **File**: `models/embeddings.py`
- **Model**: `ProductEmbedding`
- **Features**:
  - pgvector column type for embeddings
  - Relationship to Product model
  - Support for multiple embedding types ('image', 'text')
  - Model versioning for tracking embedding models

### 3. Dependencies
- **Added to** `requirements.txt`:
  - `pgvector==0.2.4` - PostgreSQL vector extension Python bindings

### 4. Tests
- **File**: `tests/test_pgvector_setup.py`
- **Coverage**:
  - Extension enabled
  - Table schema validation
  - Vector insertion/retrieval
  - Cosine similarity search
  - Index verification
  - Trigger functionality

---

## Installation Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs `pgvector==0.2.4` along with other dependencies.

### Step 2: Run Migration

**Important**: Make sure your PostgreSQL database is running and `DATABASE_URL` is set.

```bash
# Run migration
python migrations/add_pgvector_embeddings.py

# Expected output:
# INFO - Starting pgvector embeddings migration...
# INFO - Enabling pgvector extension...
# INFO - Creating product_embeddings table...
# INFO - Creating indexes for product_embeddings...
# INFO - Creating trigger for updated_at column...
# INFO - ✅ pgvector embeddings migration completed successfully!
# INFO - ✅ Verified: product_embeddings table exists
# INFO - ✅ Verified: pgvector extension enabled
```

### Step 3: Verify Installation

```bash
# Run tests
pytest tests/test_pgvector_setup.py -v

# Expected output:
# tests/test_pgvector_setup.py::test_pgvector_extension_enabled PASSED
# tests/test_pgvector_setup.py::test_product_embeddings_table_exists PASSED
# tests/test_pgvector_setup.py::test_vector_indexes_exist PASSED
# tests/test_pgvector_setup.py::test_insert_and_query_vector PASSED
# tests/test_pgvector_setup.py::test_cosine_similarity_search PASSED
# tests/test_pgvector_setup.py::test_updated_at_trigger PASSED
```

---

## Database Schema

### product_embeddings Table

```sql
CREATE TABLE product_embeddings (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    embedding vector(512) NOT NULL,  -- 512-dimensional vector
    embedding_type VARCHAR(20) NOT NULL DEFAULT 'image',  -- 'image' or 'text'
    model_version VARCHAR(50) NOT NULL DEFAULT 'vertex-multimodal-001',
    source_url TEXT,  -- Image URL or text content
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_product_embedding_type UNIQUE (product_id, embedding_type)
);
```

### Indexes

1. **IVFFlat Vector Index** (for similarity search):
   ```sql
   CREATE INDEX product_embeddings_vector_idx
   ON product_embeddings
   USING ivfflat (embedding vector_cosine_ops)
   WITH (lists = 100);
   ```
   - Optimized for < 100k vectors
   - Uses cosine distance metric

2. **Regular Indexes** (for filtering):
   ```sql
   CREATE INDEX product_embeddings_product_id_idx ON product_embeddings(product_id);
   CREATE INDEX product_embeddings_type_idx ON product_embeddings(embedding_type);
   CREATE INDEX product_embeddings_created_at_idx ON product_embeddings(created_at DESC);
   ```

---

## Usage Examples

### Python (SQLAlchemy)

```python
from models import Product, ProductEmbedding
from sqlalchemy import text
import numpy as np

# Insert embedding
product = Product(name="Букет роз", price=950000, ...)
embedding_vector = np.random.randn(512)
embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)  # Normalize

embedding = ProductEmbedding(
    product_id=product.id,
    embedding=embedding_vector.tolist(),
    embedding_type="image",
    model_version="vertex-multimodal-001",
    source_url="https://flower-shop-images.../image.png"
)
session.add(embedding)
await session.commit()

# Similarity search
query_vector = [0.123, -0.456, ...]  # Your query embedding (512D)

result = await session.execute(
    text("""
        SELECT
            p.id,
            p.name,
            p.price,
            1 - (pe.embedding <=> :query_vector::vector) AS similarity
        FROM products p
        INNER JOIN product_embeddings pe ON p.id = pe.product_id
        WHERE pe.embedding_type = 'image'
        ORDER BY pe.embedding <=> :query_vector::vector ASC
        LIMIT 10
    """),
    {"query_vector": str(query_vector)}
)

for row in result:
    print(f"Product: {row[1]}, Similarity: {row[3]:.3f}")
```

### SQL (Raw Queries)

```sql
-- Find top 10 similar products
SELECT
    p.id,
    p.name,
    p.price,
    1 - (pe.embedding <=> '[0.123, -0.456, ...]'::vector) AS similarity
FROM products p
INNER JOIN product_embeddings pe ON p.id = pe.product_id
WHERE pe.embedding_type = 'image'
  AND p.enabled = true
ORDER BY pe.embedding <=> '[0.123, -0.456, ...]'::vector ASC
LIMIT 10;

-- Count embeddings by type
SELECT
    embedding_type,
    COUNT(*) as count,
    COUNT(DISTINCT product_id) as unique_products
FROM product_embeddings
GROUP BY embedding_type;

-- Get embedding statistics
SELECT
    COUNT(*) as total_embeddings,
    COUNT(DISTINCT product_id) as products_with_embeddings,
    COUNT(DISTINCT model_version) as models_used,
    MIN(created_at) as first_embedding,
    MAX(created_at) as last_embedding
FROM product_embeddings;
```

---

## Performance Considerations

### Vector Search Performance

| Vectors | Query Time | Index Type | Recommendation |
|---------|------------|------------|----------------|
| < 10k   | ~50-100ms  | IVFFlat (lists=100) | ✅ Current setup |
| 10k-100k | ~100-200ms | IVFFlat (lists=1000) | Adjust lists param |
| 100k-1M | ~200-500ms | IVFFlat (lists=10000) | Consider HNSW index |
| > 1M    | ~500ms+    | HNSW | Upgrade to HNSW |

**Current Setup**:
- ~50-100 products → IVFFlat with lists=100 is optimal
- Query time: ~50-100ms per search

### Index Tuning

If you grow beyond 1000 products, rebuild the index:

```sql
-- Drop old index
DROP INDEX product_embeddings_vector_idx;

-- Create new index with more lists
CREATE INDEX product_embeddings_vector_idx
ON product_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);  -- Increase lists parameter
```

### Query Optimization

```sql
-- Set optimal settings for vector search
SET ivfflat.probes = 10;  -- Number of lists to scan (balance speed/accuracy)

-- For production queries
SET enable_seqscan = off;  -- Force index usage
SET max_parallel_workers_per_gather = 4;  -- Parallel query execution
```

---

## Rollback

If you need to rollback the migration:

```bash
python migrations/add_pgvector_embeddings.py --rollback

# This will:
# - Drop product_embeddings table
# - Drop trigger and function
# - Keep pgvector extension (safe to leave enabled)
```

---

## Next Steps

1. ✅ **Phase 1 Complete**: PostgreSQL + pgvector setup
2. ⏳ **Phase 2**: Create Embedding Service (Railway microservice)
3. ⏳ **Phase 3**: Webhook integration from Bitrix
4. ⏳ **Phase 4**: Search API in Backend
5. ⏳ **Phase 5**: Batch indexing script

---

## Troubleshooting

### Error: "type 'vector' does not exist"
**Cause**: pgvector extension not enabled
**Fix**: Run migration again, it will enable the extension

### Error: "could not create index 'product_embeddings_vector_idx'"
**Cause**: Table doesn't exist or has no data
**Fix**:
1. Ensure migration completed successfully
2. IVFFlat index requires some data to train - insert at least 1 embedding first

### Error: "invalid input syntax for type vector"
**Cause**: Vector format is incorrect
**Fix**: Ensure vector is:
- List of floats: `[0.1, 0.2, ..., 0.n]`
- Correct dimensions: 512
- Normalized (optional but recommended)

### Slow Queries
**Cause**: Index not being used
**Fix**:
```sql
-- Check if index is used
EXPLAIN ANALYZE
SELECT * FROM product_embeddings
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;

-- Look for "Index Scan using product_embeddings_vector_idx"
-- If you see "Seq Scan", index is not used
```

---

## Resources

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Vector Operations](https://github.com/pgvector/pgvector#getting-started)
- [Similarity Search Guide](https://github.com/pgvector/pgvector#approximate-search)
- [Index Tuning](https://github.com/pgvector/pgvector#indexing)
