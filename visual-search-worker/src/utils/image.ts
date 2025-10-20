/**
 * Image processing utilities
 */

import { ImageProcessingError } from '../types';

const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_MIME_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];

/**
 * Fetch image from URL
 */
export async function fetchImageFromUrl(url: string): Promise<Uint8Array> {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'VisualSearchWorker/1.0',
      },
    });

    if (!response.ok) {
      throw new ImageProcessingError(`Failed to fetch image: ${response.status} ${response.statusText}`);
    }

    // Skip Content-Type validation for external URLs (e.g., Telegram CDN returns application/octet-stream)
    // Image format will be validated by magic bytes in validateImageBytes()
    // const contentType = response.headers.get('content-type');
    // if (contentType && !ALLOWED_MIME_TYPES.includes(contentType)) {
    //   throw new ImageProcessingError(`Unsupported image type: ${contentType}`);
    // }

    const contentLength = response.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > MAX_IMAGE_SIZE) {
      throw new ImageProcessingError(`Image too large: ${contentLength} bytes (max ${MAX_IMAGE_SIZE})`);
    }

    const arrayBuffer = await response.arrayBuffer();
    return new Uint8Array(arrayBuffer);
  } catch (error) {
    if (error instanceof ImageProcessingError) {
      throw error;
    }
    throw new ImageProcessingError(`Failed to fetch image: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Decode base64 image
 */
export function decodeBase64Image(base64: string): Uint8Array {
  try {
    // Extract base64 data (remove data:image/...;base64, prefix)
    const base64Data = base64.split(',')[1];
    if (!base64Data) {
      throw new ImageProcessingError('Invalid base64 format');
    }

    // Decode base64 to binary
    const binaryString = atob(base64Data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    if (bytes.length > MAX_IMAGE_SIZE) {
      throw new ImageProcessingError(`Image too large: ${bytes.length} bytes (max ${MAX_IMAGE_SIZE})`);
    }

    return bytes;
  } catch (error) {
    if (error instanceof ImageProcessingError) {
      throw error;
    }
    throw new ImageProcessingError(`Failed to decode base64 image: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Load image from R2 bucket
 */
export async function loadImageFromR2(bucket: R2Bucket, key: string): Promise<Uint8Array> {
  try {
    const object = await bucket.get(key);
    if (!object) {
      throw new ImageProcessingError(`Image not found in R2: ${key}`);
    }

    const arrayBuffer = await object.arrayBuffer();
    return new Uint8Array(arrayBuffer);
  } catch (error) {
    if (error instanceof ImageProcessingError) {
      throw error;
    }
    throw new ImageProcessingError(`Failed to load image from R2: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Extract R2 key from URL
 * Example: https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png -> mg6684nq-0y61rde1owm.png
 */
export function extractR2KeyFromUrl(url: string): string | null {
  try {
    const parsedUrl = new URL(url);

    // Only extract key for our R2 CDN domain
    // External URLs (like Telegram CDN) will return null and be fetched via fetchImageFromUrl
    if (!parsedUrl.hostname.includes('flower-shop-images.alekenov.workers.dev')) {
      return null;
    }

    const pathname = parsedUrl.pathname;
    // Remove leading slash
    const key = pathname.startsWith('/') ? pathname.slice(1) : pathname;
    return key || null;
  } catch (e) {
    return null;
  }
}

/**
 * Get presigned URL for R2 object (short TTL for security)
 */
export function getPresignedUrl(workerHost: string, key: string, ttlSeconds = 3600): string {
  // For now, return direct worker URL (R2 bucket is public via worker)
  // In production, consider implementing signed URLs with expiration
  return `https://${workerHost}/${key}`;
}

/**
 * Validate image bytes
 */
export function validateImageBytes(bytes: Uint8Array): void {
  if (bytes.length === 0) {
    throw new ImageProcessingError('Image is empty');
  }

  if (bytes.length > MAX_IMAGE_SIZE) {
    throw new ImageProcessingError(`Image too large: ${bytes.length} bytes (max ${MAX_IMAGE_SIZE})`);
  }

  // Check magic bytes for common image formats
  const isPNG = bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4E && bytes[3] === 0x47;
  const isJPEG = bytes[0] === 0xFF && bytes[1] === 0xD8 && bytes[2] === 0xFF;
  const isWebP = bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50;

  if (!isPNG && !isJPEG && !isWebP) {
    throw new ImageProcessingError('Unsupported image format (not PNG, JPEG, or WebP)');
  }
}
