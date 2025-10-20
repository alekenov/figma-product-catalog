/**
 * GET /stats - Get index statistics
 */

import { Env, StatsResponse } from '../types';
import { successResponse, errorResponse } from '../utils/response';
import { getIndexStats } from '../services/vectorize';
import { getTotalCount, getLastIndexedAt } from '../services/metadata';

export async function handleStats(request: Request, env: Env): Promise<Response> {
  try {
    // Get stats from Vectorize
    let vectorizeStatus: 'healthy' | 'error' = 'healthy';
    let vectorCount = 0;

    try {
      const indexStats = await getIndexStats(env.VECTORIZE_INDEX);
      vectorCount = indexStats.count;
    } catch (error) {
      console.error('Failed to get Vectorize stats:', error);
      vectorizeStatus = 'error';
    }

    // Get stats from D1
    const d1Count = await getTotalCount(env.DB);
    const lastIndexedAt = await getLastIndexedAt(env.DB);

    const response: StatsResponse = {
      total_indexed: d1Count,
      last_indexed_at: lastIndexedAt || undefined,
      vectorize_status: vectorizeStatus,
      d1_rows: d1Count,
      storage_usage_mb: undefined, // Could be calculated if needed
    };

    return successResponse(response);
  } catch (error) {
    console.error('Stats error:', error);
    return errorResponse(
      error instanceof Error ? error.message : 'Failed to get stats',
      500
    );
  }
}
