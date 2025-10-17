/**
 * Type definitions for image validation
 */

export interface FileValidationResult {
  success: boolean;
  error?: string;
  file?: File | Blob;
  filename?: string;
  size?: number;
  type?: string;
}

export interface ValidationOptions {
  maxFileSize?: number;
  allowedTypes?: string[];
}

export interface ImageUploadResponse {
  success: boolean;
  imageId: string;
  url: string;
  size: number;
  type: string;
  error?: string;
  message?: string;
}
