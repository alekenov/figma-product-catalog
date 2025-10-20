/**
 * Visual Search Worker - Main Entry Point
 * Provides visual bouquet search using CLIP embeddings and Vectorize
 */

import { Env } from './types';
import { handleCORS, notFoundResponse, jsonResponse, internalErrorResponse } from './utils/response';
import { handleIndex } from './handlers/index';
import { handleSearch } from './handlers/search';
import { handleBatchIndex } from './handlers/batch';
import { handleStats } from './handlers/stats';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      return handleCORS();
    }

    try {
      // Health check
      if (path === '/' && method === 'GET') {
        return jsonResponse({
          status: 'ok',
          service: 'visual-search',
          version: '1.0.0',
          endpoints: [
            'POST /index - Index bouquet for visual search',
            'POST /search - Search for similar bouquets by image',
            'POST /batch-index - Batch index bouquets',
            'GET /stats - Get index statistics',
          ],
        });
      }

      // POST /index - Index single bouquet
      if (path === '/index' && method === 'POST') {
        return await handleIndex(request, env);
      }

      // POST /search - Search by image
      if (path === '/search' && method === 'POST') {
        return await handleSearch(request, env);
      }

      // POST /batch-index - Batch indexing
      if (path === '/batch-index' && method === 'POST') {
        return await handleBatchIndex(request, env);
      }

      // GET /stats - Index statistics
      if (path === '/stats' && method === 'GET') {
        return await handleStats(request, env);
      }

      // Route not found
      return notFoundResponse(`Route ${method} ${path} not found`);
    } catch (error) {
      console.error('Worker error:', error);
      return internalErrorResponse(error instanceof Error ? error : new Error('Unknown error'));
    }
  },
};
