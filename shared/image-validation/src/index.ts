/**
 * Flower Shop Image Validation
 *
 * Shared library for image validation and utilities
 * Used by image-worker (Cloudflare Worker) and functions (Cloudflare Pages)
 */

// Export types
export type { FileValidationResult, ValidationOptions, ImageUploadResponse } from './types';

// Export constants
export {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  MIME_TYPE_MAP,
  ALLOWED_EXTENSIONS,
  ERROR_MESSAGES
} from './constants';

// Export validation functions
export {
  validateFileSize,
  validateMimeType,
  validateFileExtension,
  validateFile,
  validateFormDataFile,
  validateContentType
} from './validation';

// Export utility functions
export {
  generateId,
  getExtension,
  generateStorageKey,
  generateImageUrl,
  getHostnameFromUrl
} from './utils';
