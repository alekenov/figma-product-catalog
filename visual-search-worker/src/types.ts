/**
 * Type definitions for Visual Search Worker
 */

// ============================================
// Cloudflare Environment Bindings
// ============================================

export interface Env {
  // R2 bucket for images
  IMAGES: R2Bucket;

  // Vectorize index for embeddings
  VECTORIZE_INDEX: VectorizeIndex;

  // D1 database for metadata
  DB: D1Database;

  // Google Vertex AI credentials (stored as Cloudflare Secrets)
  VERTEX_PROJECT_ID: string;
  VERTEX_LOCATION: string;
  VERTEX_SERVICE_ACCOUNT_KEY: string;

  // Environment variables
  ENVIRONMENT?: string;
  SIMILARITY_THRESHOLD_EXACT?: string;
  SIMILARITY_THRESHOLD_SIMILAR?: string;
  MAX_RESULTS?: string;
}

// ============================================
// Database Models
// ============================================

export interface BouquetMetadata {
  product_id: number;
  name: string;
  price: number;  // kopecks
  image_key: string;  // R2 key
  colors?: string;  // JSON array
  occasions?: string;  // JSON array
  tags?: string;  // JSON array
  shop_id: number;
  indexed_at: string;
  updated_at: string;
}

// ============================================
// API Request/Response Types
// ============================================

// POST /index - Index bouquet
export interface IndexRequest {
  product_id: number;
  image_url?: string;  // R2 URL or external URL
  image_base64?: string;  // Base64 encoded image
  name: string;
  price: number;
  colors?: string[];
  occasions?: string[];
  tags?: string[];
  shop_id?: number;
}

export interface IndexResponse {
  success: boolean;
  product_id: number;
  vector_id: string;
  indexed_at: string;
  error?: string;
}

// POST /search - Search by image
export interface SearchRequest {
  image_url?: string;
  image_base64?: string;
  topK?: number;  // Max results to return (default: 10)
  threshold?: number;  // Min similarity score (default: 0.7)
  filters?: {
    colors?: string[];
    occasions?: string[];
    tags?: string[];
    shop_id?: number;
  };
}

export interface SearchResult {
  product_id: number;
  name: string;
  price: number;
  image_url: string;  // Presigned R2 URL
  similarity: number;  // 0.0 - 1.0
  colors?: string[];
  occasions?: string[];
  tags?: string[];
}

export interface SearchResponse {
  exact: SearchResult[];  // similarity >= THRESHOLD_EXACT
  similar: SearchResult[];  // similarity >= THRESHOLD_SIMILAR
  search_time_ms: number;
  total_indexed: number;
}

// POST /batch-index - Batch indexing
export interface BatchIndexRequest {
  source: 'postgresql' | 'r2';
  limit?: number;
  offset?: number;
  shop_id?: number;
}

export interface BatchIndexResponse {
  success: boolean;
  total: number;
  indexed: number;
  failed: number;
  errors: Array<{
    product_id: number;
    error: string;
  }>;
  duration_ms: number;
}

// GET /stats - Index statistics
export interface StatsResponse {
  total_indexed: number;
  last_indexed_at?: string;
  vectorize_status: 'healthy' | 'error';
  d1_rows: number;
  storage_usage_mb?: number;
}

// ============================================
// Internal Types
// ============================================

export interface ImageEmbedding {
  vector: number[];  // 512-dim float array from Vertex AI Multimodal
  model: string;
  generated_at: string;
}

export interface VectorizeMatch {
  id: string;  // product_id as string
  score: number;  // cosine similarity
  metadata?: Record<string, any>;
}

// ============================================
// Error Types
// ============================================

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ImageProcessingError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ImageProcessingError';
  }
}

export class VectorizeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'VectorizeError';
  }
}
