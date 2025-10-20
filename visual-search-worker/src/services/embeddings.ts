/**
 * Vertex AI Multimodal Embeddings Service
 * Generates image embeddings using Google Vertex AI
 */

import { Env, ImageEmbedding } from '../types';
import { getAccessToken } from './gcp-auth';

const VERTEX_MODEL = 'multimodalembedding@001';
const EMBEDDING_DIMENSIONS = 512;

/**
 * Generate embedding from image bytes using Vertex AI
 */
export async function generateEmbedding(
  env: Env,
  imageBytes: Uint8Array
): Promise<ImageEmbedding> {
  try {
    const startTime = Date.now();

    // Get GCP credentials from environment
    const projectId = env.VERTEX_PROJECT_ID;
    const location = env.VERTEX_LOCATION;
    const serviceAccountKey = env.VERTEX_SERVICE_ACCOUNT_KEY;

    if (!projectId || !location || !serviceAccountKey) {
      throw new Error('Missing Vertex AI credentials in environment');
    }

    // Get OAuth2 access token
    const accessToken = await getAccessToken(serviceAccountKey);

    // Convert image to base64
    const base64Image = arrayBufferToBase64(imageBytes.buffer);

    // Vertex AI API endpoint
    const endpoint = `https://${location}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${location}/publishers/google/models/${VERTEX_MODEL}:predict`;

    // Call Vertex AI Multimodal Embeddings API
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        instances: [
          {
            image: {
              bytesBase64Encoded: base64Image,
            },
          },
        ],
        parameters: {
          dimension: EMBEDDING_DIMENSIONS,
        },
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Vertex AI API error: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    const duration = Date.now() - startTime;
    console.log(`Vertex AI embedding generated in ${duration}ms`);

    // Extract embedding from response
    if (!data.predictions || !data.predictions[0] || !data.predictions[0].imageEmbedding) {
      throw new Error('Invalid Vertex AI response format');
    }

    const embedding: number[] = data.predictions[0].imageEmbedding;

    // Validate dimensions
    if (embedding.length !== EMBEDDING_DIMENSIONS) {
      throw new Error(
        `Invalid embedding dimensions: expected ${EMBEDDING_DIMENSIONS}, got ${embedding.length}`
      );
    }

    // Normalize embedding (L2 normalization for cosine similarity)
    const normalized = normalizeVector(embedding);

    return {
      vector: normalized,
      model: VERTEX_MODEL,
      generated_at: new Date().toISOString(),
    };
  } catch (error) {
    console.error('Vertex AI embedding error:', error);
    throw new Error(
      `Failed to generate embedding: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * L2 normalize vector for cosine similarity
 */
function normalizeVector(vector: number[]): number[] {
  const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  return magnitude === 0 ? vector : vector.map((val) => val / magnitude);
}

/**
 * Convert ArrayBuffer to base64 string
 */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Batch generate embeddings (for batch indexing)
 */
export async function generateEmbeddingsBatch(
  env: Env,
  images: Array<{ id: number; bytes: Uint8Array }>
): Promise<Array<{ id: number; embedding: ImageEmbedding; error?: string }>> {
  const results = [];

  // Process in parallel with concurrency limit (max 3 concurrent for Vertex AI)
  const concurrency = 3;
  for (let i = 0; i < images.length; i += concurrency) {
    const batch = images.slice(i, i + concurrency);
    const promises = batch.map(async ({ id, bytes }) => {
      try {
        const embedding = await generateEmbedding(env, bytes);
        return { id, embedding };
      } catch (error) {
        return {
          id,
          embedding: null as any,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    });

    const batchResults = await Promise.all(promises);
    results.push(...batchResults);
  }

  return results;
}

/**
 * Calculate cosine similarity between two vectors
 */
export function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) {
    throw new Error('Vectors must have same dimensions');
  }

  let dotProduct = 0;
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
  }

  // Assuming vectors are normalized, cosine = dot product
  return dotProduct;
}
