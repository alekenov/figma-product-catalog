/**
 * POST /reindex-one - Reindex single product from Railway backend
 */

import { Env } from '../types';
import { successResponse, errorResponse } from '../utils/response';
import {
  fetchImageFromUrl,
  loadImageFromR2,
  extractR2KeyFromUrl,
  validateImageBytes,
} from '../utils/image';
import { generateEmbedding } from '../services/embeddings';
import { upsertVector } from '../services/vectorize';
import { upsertMetadata } from '../services/metadata';

interface ReindexOneRequest {
  product_id: number;
  shop_id?: number;
}

interface ReindexOneResponse {
  success: boolean;
  product_id: number;
  indexed_at: string;
  duration_ms: number;
}

export async function handleReindexOne(request: Request, env: Env): Promise<Response> {
  try {
    const startTime = Date.now();

    // Parse request body
    const body: ReindexOneRequest = await request.json();

    if (!body.product_id) {
      return errorResponse('product_id is required', 400);
    }

    const productId = body.product_id;
    const shopId = body.shop_id || 8;

    console.log(`Reindexing product ${productId} from shop ${shopId}...`);

    // Step 1: Fetch product from Railway API
    const backendUrl = 'https://figma-product-catalog-production.up.railway.app/api/v1';
    const productResponse = await fetch(
      `${backendUrl}/products/?shop_id=${shopId}&enabled_only=false`
    );

    if (!productResponse.ok) {
      return errorResponse(`Failed to fetch product from backend: ${productResponse.statusText}`, 500);
    }

    const products = await productResponse.json();
    const product = products.find((p: any) => p.id === productId);

    if (!product) {
      return errorResponse(`Product ${productId} not found in backend`, 404);
    }

    // Check if product is enabled
    if (!product.enabled) {
      console.log(`Product ${productId} is disabled, skipping reindex`);
      return successResponse({
        success: true,
        product_id: productId,
        indexed_at: new Date().toISOString(),
        duration_ms: Date.now() - startTime,
        skipped: true,
        reason: 'Product is disabled',
      });
    }

    // Step 2: Load image
    let imageBytes: Uint8Array;
    let imageKey: string;

    const imageUrl = product.image;
    if (!imageUrl) {
      return errorResponse(`Product ${productId} has no image`, 400);
    }

    // Check if URL is from R2 bucket or external
    const r2Key = extractR2KeyFromUrl(imageUrl);
    if (r2Key) {
      // Load from R2
      imageBytes = await loadImageFromR2(env.IMAGES, r2Key);
      imageKey = r2Key;
      console.log(`Loaded image from R2: ${r2Key}`);
    } else {
      // External URL (e.g., cvety.kz) - fetch it
      imageBytes = await fetchImageFromUrl(imageUrl);
      // Extract filename from URL for key
      imageKey = imageUrl.split('/').pop() || `product-${productId}.jpg`;
      console.log(`Fetched image from external URL: ${imageUrl}`);
    }

    // Validate image
    validateImageBytes(imageBytes);

    // Step 3: Generate embedding
    const embedding = await generateEmbedding(env, imageBytes);
    console.log(`Generated embedding for product ${productId} (${embedding.vector.length} dims)`);

    // Step 4: Upsert to Vectorize
    await upsertVector(
      env.VECTORIZE_INDEX,
      productId.toString(),
      embedding.vector,
      {
        colors: product.colors ? JSON.stringify(product.colors) : undefined,
        occasions: product.occasions ? JSON.stringify(product.occasions) : undefined,
        tags: product.tags ? JSON.stringify(product.tags) : undefined,
      }
    );

    // Step 5: Upsert metadata to D1
    await upsertMetadata(env.DB, {
      product_id: productId,
      name: product.name,
      price: product.price,
      image_key: imageKey,
      colors: product.colors,
      occasions: product.occasions,
      tags: product.tags,
      shop_id: shopId,
    });

    const duration = Date.now() - startTime;
    console.log(`✅ Reindexed product ${productId} in ${duration}ms`);

    const response: ReindexOneResponse = {
      success: true,
      product_id: productId,
      indexed_at: new Date().toISOString(),
      duration_ms: duration,
    };

    return successResponse(response);
  } catch (error) {
    console.error('Reindex error:', error);
    return errorResponse(
      error instanceof Error ? error.message : 'Failed to reindex product',
      500
    );
  }
}
