/**
 * Shared constants for image validation
 */

/**
 * Allowed image MIME types
 */
export const ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif'
] as const;

/**
 * Maximum file size in bytes (10MB)
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024;

/**
 * MIME type to file extension mapping
 */
export const MIME_TYPE_MAP: Record<string, string> = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
  'image/gif': 'gif'
} as const;

/**
 * Allowed file extensions
 */
export const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif'] as const;

/**
 * Error messages
 */
export const ERROR_MESSAGES = {
  NO_FILE: 'No file provided',
  FILE_TOO_LARGE: 'File too large. Max size: 10MB',
  INVALID_TYPE: 'Invalid file type. Allowed types: JPEG, PNG, WebP, GIF',
  INVALID_EXTENSION: 'Invalid file extension. Allowed: jpg, jpeg, png, webp, gif',
  INVALID_CONTENT_TYPE: 'Invalid content type. Use multipart/form-data or image/* binary'
} as const;

export type ErrorMessage = keyof typeof ERROR_MESSAGES;
