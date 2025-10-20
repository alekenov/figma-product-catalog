/**
 * POST /batch-index - Batch index bouquets from PostgreSQL or R2
 */

import { Env, BatchIndexRequest, BatchIndexResponse } from '../types';
import { successResponse, errorResponse } from '../utils/response';
import { loadImageFromR2, validateImageBytes } from '../utils/image';
import { generateEmbeddingsBatch } from '../services/embeddings';
import { upsertVectorsBatch } from '../services/vectorize';
import { upsertMetadata } from '../services/metadata';

interface ProductData {
  id: number;
  name: string;
  price: number;
  image: string;  // R2 key or URL
  colors?: string[];
  occasions?: string[];
  tags?: string[];
  shop_id?: number;
}

export async function handleBatchIndex(request: Request, env: Env): Promise<Response> {
  try {
    const startTime = Date.now();

    // Parse request body
    const body: BatchIndexRequest = await request.json();
    const source = body.source || 'postgresql';
    const limit = body.limit || 100;
    const offset = body.offset || 0;
    const shopId = body.shop_id || 8;

    console.log(`Starting batch index: source=${source}, limit=${limit}, offset=${offset}`);

    // Step 1: Fetch products from source
    let products: ProductData[] = [];

    if (source === 'postgresql') {
      // Fetch from PostgreSQL backend API
      const backendUrl = 'https://figma-product-catalog-production.up.railway.app/api/v1';
      const response = await fetch(
        `${backendUrl}/products/?shop_id=${shopId}&enabled_only=true&limit=${limit}&skip=${offset}`
      );

      if (!response.ok) {
        return errorResponse(`Failed to fetch products from backend: ${response.statusText}`, 500);
      }

      const productsData = await response.json();
      products = productsData.map((p: any) => ({
        id: p.id,
        name: p.name,
        price: p.price,
        image: p.image,
        colors: p.colors,
        occasions: p.occasions,
        tags: p.tags,
        shop_id: p.shop_id,
      }));
    } else if (source === 'r2') {
      // List R2 objects and match with existing D1 metadata
      const listed = await env.IMAGES.list({ limit: limit });

      // Get existing metadata from D1
      const existingMetadata = await env.DB.prepare(`
        SELECT * FROM bouquets LIMIT ? OFFSET ?
      `)
        .bind(limit, offset)
        .all();

      products = existingMetadata.results?.map((m: any) => ({
        id: m.product_id,
        name: m.name,
        price: m.price,
        image: m.image_key,
        colors: m.colors ? JSON.parse(m.colors) : undefined,
        occasions: m.occasions ? JSON.parse(m.occasions) : undefined,
        tags: m.tags ? JSON.parse(m.tags) : undefined,
        shop_id: m.shop_id,
      })) || [];
    } else {
      return errorResponse('Invalid source. Use "postgresql" or "r2"', 400);
    }

    console.log(`Fetched ${products.length} products from ${source}`);

    if (products.length === 0) {
      return successResponse({
        success: true,
        total: 0,
        indexed: 0,
        failed: 0,
        errors: [],
        duration_ms: Date.now() - startTime,
      });
    }

    // Step 2: Load images from R2
    const imagesWithBytes: Array<{ id: number; bytes: Uint8Array; product: ProductData }> = [];
    const errors: Array<{ product_id: number; error: string }> = [];

    for (const product of products) {
      try {
        // Extract R2 key from URL or use directly
        let r2Key = product.image;
        if (r2Key.startsWith('http')) {
          const parts = r2Key.split('/');
          r2Key = parts[parts.length - 1];
        }

        const bytes = await loadImageFromR2(env.IMAGES, r2Key);
        validateImageBytes(bytes);
        imagesWithBytes.push({ id: product.id, bytes, product });
      } catch (error) {
        console.error(`Failed to load image for product ${product.id}:`, error);
        errors.push({
          product_id: product.id,
          error: error instanceof Error ? error.message : 'Failed to load image',
        });
      }
    }

    console.log(`Loaded ${imagesWithBytes.length} images successfully`);

    // Step 3: Generate embeddings in batch (Vertex AI)
    const embeddingResults = await generateEmbeddingsBatch(
      env,
      imagesWithBytes.map(({ id, bytes }) => ({ id, bytes }))
    );

    // Step 4: Prepare vectors for Vectorize
    const vectors = [];
    for (const result of embeddingResults) {
      if (result.error) {
        errors.push({
          product_id: result.id,
          error: result.error,
        });
      } else {
        const product = imagesWithBytes.find(i => i.id === result.id)?.product;
        if (!product) continue;

        vectors.push({
          id: result.id.toString(),
          values: result.embedding.vector,
          metadata: {
            colors: product.colors ? JSON.stringify(product.colors) : undefined,
            occasions: product.occasions ? JSON.stringify(product.occasions) : undefined,
            tags: product.tags ? JSON.stringify(product.tags) : undefined,
          },
        });
      }
    }

    // Step 5: Batch upsert to Vectorize
    const vectorizeResult = await upsertVectorsBatch(env.VECTORIZE_INDEX, vectors);
    console.log(`Vectorize batch: ${vectorizeResult.success} success, ${vectorizeResult.failed} failed`);

    // Step 6: Upsert metadata to D1
    let metadataSuccess = 0;
    for (const { id, product } of imagesWithBytes) {
      try {
        let r2Key = product.image;
        if (r2Key.startsWith('http')) {
          const parts = r2Key.split('/');
          r2Key = parts[parts.length - 1];
        }

        await upsertMetadata(env.DB, {
          product_id: id,
          name: product.name,
          price: product.price,
          image_key: r2Key,
          colors: product.colors,
          occasions: product.occasions,
          tags: product.tags,
          shop_id: product.shop_id || shopId,
        });
        metadataSuccess++;
      } catch (error) {
        console.error(`Failed to upsert metadata for product ${id}:`, error);
        errors.push({
          product_id: id,
          error: error instanceof Error ? error.message : 'Failed to upsert metadata',
        });
      }
    }

    const duration = Date.now() - startTime;
    console.log(`Batch index completed in ${duration}ms`);

    const response: BatchIndexResponse = {
      success: true,
      total: products.length,
      indexed: vectorizeResult.success,
      failed: errors.length,
      errors,
      duration_ms: duration,
    };

    return successResponse(response);
  } catch (error) {
    console.error('Batch index error:', error);
    return errorResponse(
      error instanceof Error ? error.message : 'Failed to batch index',
      500
    );
  }
}
