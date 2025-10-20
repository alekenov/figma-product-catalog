/**
 * Input validation utilities
 */

import { ValidationError } from '../types';

/**
 * Validate image input (URL or base64)
 */
export function validateImageInput(imageUrl?: string, imageBase64?: string): void {
  if (!imageUrl && !imageBase64) {
    throw new ValidationError('Either image_url or image_base64 must be provided');
  }

  if (imageUrl && imageBase64) {
    throw new ValidationError('Cannot provide both image_url and image_base64');
  }

  if (imageUrl) {
    try {
      new URL(imageUrl);
    } catch (e) {
      throw new ValidationError('Invalid image_url format');
    }
  }

  if (imageBase64) {
    // Basic base64 validation
    const base64Pattern = /^data:image\/(png|jpeg|jpg|webp);base64,/;
    if (!base64Pattern.test(imageBase64)) {
      throw new ValidationError(
        'Invalid image_base64 format. Expected: data:image/(png|jpeg|jpg|webp);base64,...'
      );
    }
  }
}

/**
 * Validate product_id
 */
export function validateProductId(productId: any): number {
  const id = Number(productId);
  if (!Number.isInteger(id) || id <= 0) {
    throw new ValidationError('product_id must be a positive integer');
  }
  return id;
}

/**
 * Validate similarity threshold
 */
export function validateThreshold(threshold: any): number {
  const val = Number(threshold);
  if (isNaN(val) || val < 0 || val > 1) {
    throw new ValidationError('threshold must be between 0 and 1');
  }
  return val;
}

/**
 * Validate topK parameter
 */
export function validateTopK(topK: any, max = 100): number {
  const val = Number(topK);
  if (!Number.isInteger(val) || val < 1 || val > max) {
    throw new ValidationError(`topK must be between 1 and ${max}`);
  }
  return val;
}

/**
 * Validate shop_id
 */
export function validateShopId(shopId: any): number {
  const id = Number(shopId);
  if (!Number.isInteger(id) || id <= 0) {
    throw new ValidationError('shop_id must be a positive integer');
  }
  return id;
}

/**
 * Parse JSON array safely
 */
export function parseJsonArray(value: string | string[] | undefined): string[] | undefined {
  if (!value) return undefined;

  if (Array.isArray(value)) {
    return value;
  }

  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) {
      return parsed;
    }
    return undefined;
  } catch (e) {
    return undefined;
  }
}
