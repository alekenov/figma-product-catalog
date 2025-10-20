/**
 * Vectorize Service
 * Handles vector storage and similarity search using Cloudflare Vectorize
 */

import { Env, VectorizeMatch } from '../types';

/**
 * Insert or update vector in Vectorize index
 */
export async function upsertVector(
  index: VectorizeIndex,
  id: string,
  vector: number[],
  metadata?: Record<string, any>
): Promise<void> {
  try {
    await index.upsert([
      {
        id,
        values: vector,
        metadata: metadata || {},
      },
    ]);

    console.log(`Upserted vector for product ${id}`);
  } catch (error) {
    console.error('Vectorize upsert error:', error);
    throw new Error(`Failed to upsert vector: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Query similar vectors using cosine similarity
 */
export async function queryVectors(
  index: VectorizeIndex,
  vector: number[],
  topK = 20,
  filters?: Record<string, any>
): Promise<VectorizeMatch[]> {
  try {
    const startTime = Date.now();

    // Query Vectorize
    const results = await index.query(vector, {
      topK,
      returnValues: false,
      returnMetadata: 'all',
      filter: filters,
    });

    const duration = Date.now() - startTime;
    console.log(`Vectorize query completed in ${duration}ms (${results.matches.length} results)`);

    // Convert to our format
    return results.matches.map(match => ({
      id: match.id,
      score: match.score,
      metadata: match.metadata,
    }));
  } catch (error) {
    console.error('Vectorize query error:', error);
    throw new Error(`Failed to query vectors: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Delete vector from index
 */
export async function deleteVector(index: VectorizeIndex, id: string): Promise<void> {
  try {
    // @ts-ignore - deleteByIds might not be in types yet
    await index.deleteByIds([id]);
    console.log(`Deleted vector for product ${id}`);
  } catch (error) {
    console.error('Vectorize delete error:', error);
    throw new Error(`Failed to delete vector: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get index statistics
 */
export async function getIndexStats(index: VectorizeIndex): Promise<{
  count: number;
  dimensions: number;
}> {
  try {
    // @ts-ignore - describe might not be in types yet
    const info = await index.describe();
    return {
      count: info.count || 0,
      dimensions: info.dimensions || 512,
    };
  } catch (error) {
    console.error('Failed to get index stats:', error);
    // Return defaults if describe not supported
    return {
      count: 0,
      dimensions: 512,
    };
  }
}

/**
 * Batch upsert vectors (for batch indexing)
 */
export async function upsertVectorsBatch(
  index: VectorizeIndex,
  vectors: Array<{ id: string; values: number[]; metadata?: Record<string, any> }>
): Promise<{ success: number; failed: number }> {
  let success = 0;
  let failed = 0;

  // Vectorize supports batch upsert up to 1000 vectors
  const batchSize = 100;

  for (let i = 0; i < vectors.length; i += batchSize) {
    const batch = vectors.slice(i, i + batchSize);
    try {
      await index.upsert(batch);
      success += batch.length;
      console.log(`Batch upserted ${batch.length} vectors (${i + batch.length}/${vectors.length})`);
    } catch (error) {
      console.error(`Failed to upsert batch ${i}-${i + batch.length}:`, error);
      failed += batch.length;
    }
  }

  return { success, failed };
}
