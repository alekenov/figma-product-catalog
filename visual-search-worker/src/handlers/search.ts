/**
 * POST /search - Search for similar bouquets by image
 */

import { Env, SearchRequest, SearchResponse, SearchResult } from '../types';
import { successResponse, errorResponse } from '../utils/response';
import { validateImageInput, validateThreshold, validateTopK } from '../utils/validation';
import {
  fetchImageFromUrl,
  decodeBase64Image,
  extractR2KeyFromUrl,
  loadImageFromR2,
  validateImageBytes,
  getPresignedUrl,
} from '../utils/image';
import { generateEmbedding } from '../services/embeddings';
import { queryVectors } from '../services/vectorize';
import { getMetadataBatch, parseMetadataArrays } from '../services/metadata';

export async function handleSearch(request: Request, env: Env): Promise<Response> {
  try {
    const startTime = Date.now();

    // Parse request body
    const body: SearchRequest = await request.json();

    // Validate inputs
    validateImageInput(body.image_url, body.image_base64);

    const topK = body.topK ? validateTopK(body.topK, 100) : 20;
    const thresholdExact = parseFloat(env.SIMILARITY_THRESHOLD_EXACT || '0.85');
    const thresholdSimilar = parseFloat(env.SIMILARITY_THRESHOLD_SIMILAR || '0.70');

    // Step 1: Load image bytes
    let imageBytes: Uint8Array;

    if (body.image_url) {
      const r2Key = extractR2KeyFromUrl(body.image_url);
      if (r2Key) {
        imageBytes = await loadImageFromR2(env.IMAGES, r2Key);
      } else {
        imageBytes = await fetchImageFromUrl(body.image_url);
      }
    } else if (body.image_base64) {
      imageBytes = decodeBase64Image(body.image_base64);
    } else {
      return errorResponse('No image provided', 400);
    }

    validateImageBytes(imageBytes);

    // Step 2: Generate Vertex AI embedding for query image
    const embedding = await generateEmbedding(env, imageBytes);
    console.log(`Generated query embedding (${embedding.vector.length} dims)`);

    // Step 3: Query Vectorize for similar vectors
    const matches = await queryVectors(
      env.VECTORIZE_INDEX,
      embedding.vector,
      topK,
      body.filters
    );

    console.log(`Found ${matches.length} matches from Vectorize`);

    // Step 4: Enrich with metadata from D1
    const productIds = matches.map(m => parseInt(m.id));
    const metadataMap = await getMetadataBatch(env.DB, productIds);

    // Step 5: Build search results
    const workerHost = new URL(request.url).hostname;
    const results: SearchResult[] = [];

    for (const match of matches) {
      const productId = parseInt(match.id);
      const metadata = metadataMap.get(productId);

      if (!metadata) {
        console.warn(`No metadata found for product ${productId}, skipping`);
        continue;
      }

      const parsed = parseMetadataArrays(metadata);

      results.push({
        product_id: productId,
        name: metadata.name,
        price: metadata.price,
        image_url: getPresignedUrl(workerHost, metadata.image_key),
        similarity: match.score,
        colors: parsed.colors,
        occasions: parsed.occasions,
        tags: parsed.tags,
      });
    }

    // Step 6: Split into exact and similar categories
    const exact = results.filter(r => r.similarity >= thresholdExact);
    const similar = results.filter(
      r => r.similarity >= thresholdSimilar && r.similarity < thresholdExact
    );

    const searchTime = Date.now() - startTime;
    console.log(
      `Search completed in ${searchTime}ms: ${exact.length} exact, ${similar.length} similar`
    );

    // Get total indexed count for stats
    const totalIndexed = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM bouquets'
    ).first<{ count: number }>();

    const response: SearchResponse = {
      exact,
      similar,
      search_time_ms: searchTime,
      total_indexed: totalIndexed?.count || 0,
    };

    return successResponse(response);
  } catch (error) {
    console.error('Search error:', error);
    return errorResponse(
      error instanceof Error ? error.message : 'Failed to search',
      500
    );
  }
}
