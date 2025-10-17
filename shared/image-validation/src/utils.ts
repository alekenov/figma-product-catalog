/**
 * Utility functions for image handling
 */
import { MIME_TYPE_MAP } from './constants';

/**
 * Generate a unique image ID
 * @returns Unique ID combining timestamp and random string
 */
export function generateId(): string {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 15);
  return `${timestamp}-${randomPart}`;
}

/**
 * Get file extension from filename or MIME type
 * @param filename - Original filename
 * @param mimeType - MIME type of the file
 * @returns File extension (without dot)
 */
export function getExtension(filename: string, mimeType: string): string {
  // Try to get from filename
  const match = filename.match(/\.([^.]+)$/);
  if (match) {
    const ext = match[1].toLowerCase();
    // Validate extension
    if (ext === 'jpeg') return 'jpg';
    return ext;
  }

  // Fallback to MIME type mapping
  return MIME_TYPE_MAP[mimeType] || 'jpg';
}

/**
 * Generate image storage key (filename with path)
 * @param imageId - Unique image ID
 * @param filename - Original filename
 * @param mimeType - MIME type of the file
 * @returns Storage key for R2/S3
 */
export function generateStorageKey(
  imageId: string,
  filename: string,
  mimeType: string
): string {
  const extension = getExtension(filename, mimeType);
  return `${imageId}.${extension}`;
}

/**
 * Generate image URL from storage key
 * @param workerHost - Cloudflare Worker hostname
 * @param storageKey - Storage key in R2
 * @returns Full image URL
 */
export function generateImageUrl(workerHost: string, storageKey: string): string {
  return `https://${workerHost}/${storageKey}`;
}

/**
 * Extract hostname from URL
 * @param urlString - URL string
 * @returns Hostname
 */
export function getHostnameFromUrl(urlString: string): string {
  try {
    const url = new URL(urlString);
    return url.hostname;
  } catch {
    return 'unknown.workers.dev';
  }
}
