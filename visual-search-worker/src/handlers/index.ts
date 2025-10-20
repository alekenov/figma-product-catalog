/**
 * POST /index - Index bouquet for visual search
 */

import { Env, IndexRequest, IndexResponse } from '../types';
import { successResponse, errorResponse } from '../utils/response';
import { validateImageInput, validateProductId } from '../utils/validation';
import {
  fetchImageFromUrl,
  decodeBase64Image,
  loadImageFromR2,
  extractR2KeyFromUrl,
  validateImageBytes,
} from '../utils/image';
import { generateEmbedding } from '../services/embeddings';
import { upsertVector } from '../services/vectorize';
import { upsertMetadata } from '../services/metadata';

export async function handleIndex(request: Request, env: Env): Promise<Response> {
  try {
    const startTime = Date.now();

    // Parse request body
    const body: IndexRequest = await request.json();

    // Validate required fields
    const productId = validateProductId(body.product_id);
    if (!body.name || !body.price) {
      return errorResponse('name and price are required', 400);
    }

    validateImageInput(body.image_url, body.image_base64);

    // Step 1: Load image bytes
    let imageBytes: Uint8Array;
    let imageKey: string;

    if (body.image_url) {
      // Check if URL is from our R2 bucket
      const r2Key = extractR2KeyFromUrl(body.image_url);
      if (r2Key) {
        // Load from R2 directly (faster)
        imageBytes = await loadImageFromR2(env.IMAGES, r2Key);
        imageKey = r2Key;
        console.log(`Loaded image from R2: ${r2Key}`);
      } else {
        // External URL - fetch and validate
        imageBytes = await fetchImageFromUrl(body.image_url);
        // Extract filename from URL for key
        imageKey = body.image_url.split('/').pop() || `product-${productId}.jpg`;
        console.log(`Fetched image from URL: ${body.image_url}`);
      }
    } else if (body.image_base64) {
      imageBytes = decodeBase64Image(body.image_base64);
      imageKey = `product-${productId}.jpg`;
      console.log(`Decoded base64 image for product ${productId}`);
    } else {
      return errorResponse('No image provided', 400);
    }

    // Validate image
    validateImageBytes(imageBytes);

    // Step 2: Generate Vertex AI embedding
    const embedding = await generateEmbedding(env, imageBytes);
    console.log(`Generated embedding for product ${productId} (${embedding.vector.length} dims)`);

    // Step 3: Upsert to Vectorize
    await upsertVector(
      env.VECTORIZE_INDEX,
      productId.toString(),
      embedding.vector,
      {
        colors: body.colors ? JSON.stringify(body.colors) : undefined,
        occasions: body.occasions ? JSON.stringify(body.occasions) : undefined,
        tags: body.tags ? JSON.stringify(body.tags) : undefined,
      }
    );

    // Step 4: Upsert metadata to D1
    await upsertMetadata(env.DB, {
      product_id: productId,
      name: body.name,
      price: body.price,
      image_key: imageKey,
      colors: body.colors,
      occasions: body.occasions,
      tags: body.tags,
      shop_id: body.shop_id || 8,
    });

    const duration = Date.now() - startTime;
    console.log(`Indexed product ${productId} in ${duration}ms`);

    const response: IndexResponse = {
      success: true,
      product_id: productId,
      vector_id: productId.toString(),
      indexed_at: new Date().toISOString(),
    };

    return successResponse(response, 201);
  } catch (error) {
    console.error('Index error:', error);
    return errorResponse(
      error instanceof Error ? error.message : 'Failed to index bouquet',
      500
    );
  }
}
