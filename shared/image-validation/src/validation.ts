/**
 * Core image validation functions
 */
import {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  ERROR_MESSAGES,
  ALLOWED_EXTENSIONS
} from './constants';
import type { FileValidationResult, ValidationOptions } from './types';

/**
 * Validate file size
 * @param fileSize - File size in bytes
 * @param maxSize - Maximum allowed size (defaults to MAX_FILE_SIZE)
 * @returns Validation result
 */
export function validateFileSize(
  fileSize: number,
  maxSize: number = MAX_FILE_SIZE
): FileValidationResult {
  if (fileSize <= 0) {
    return {
      success: false,
      error: 'File size must be greater than 0'
    };
  }

  if (fileSize > maxSize) {
    return {
      success: false,
      error: `${ERROR_MESSAGES.FILE_TOO_LARGE} (Max: ${maxSize / 1024 / 1024}MB, Got: ${(fileSize / 1024 / 1024).toFixed(2)}MB)`
    };
  }

  return { success: true };
}

/**
 * Validate file MIME type
 * @param mimeType - MIME type of the file
 * @param allowedTypes - List of allowed MIME types (defaults to ALLOWED_TYPES)
 * @returns Validation result
 */
export function validateMimeType(
  mimeType: string,
  allowedTypes: string[] = [...ALLOWED_TYPES]
): FileValidationResult {
  if (!mimeType) {
    return {
      success: false,
      error: 'MIME type is required'
    };
  }

  if (!allowedTypes.includes(mimeType)) {
    return {
      success: false,
      error: `${ERROR_MESSAGES.INVALID_TYPE} (Got: ${mimeType})`
    };
  }

  return { success: true };
}

/**
 * Validate file extension
 * @param filename - Original filename
 * @returns Validation result
 */
export function validateFileExtension(filename: string): FileValidationResult {
  if (!filename) {
    return {
      success: false,
      error: 'Filename is required'
    };
  }

  const match = filename.match(/\.([^.]+)$/);
  if (!match) {
    return {
      success: false,
      error: 'File must have an extension'
    };
  }

  const ext = match[1].toLowerCase();

  // Normalize jpeg to jpg
  if (ext === 'jpeg' || ext === 'jpg') {
    return { success: true };
  }

  if (!ALLOWED_EXTENSIONS.includes(ext as any)) {
    return {
      success: false,
      error: `${ERROR_MESSAGES.INVALID_EXTENSION} (Got: .${ext})`
    };
  }

  return { success: true };
}

/**
 * Validate file object (size + MIME type)
 * @param file - File object (web File or Node.js Buffer)
 * @param options - Validation options
 * @returns Validation result
 */
export function validateFile(
  file: File | Blob | null,
  options: ValidationOptions = {}
): FileValidationResult {
  if (!file) {
    return {
      success: false,
      error: ERROR_MESSAGES.NO_FILE
    };
  }

  const maxSize = options.maxFileSize || MAX_FILE_SIZE;
  const allowedTypes = options.allowedTypes || [...ALLOWED_TYPES];

  // Check file size
  const sizeValidation = validateFileSize(file.size, maxSize);
  if (!sizeValidation.success) {
    return sizeValidation;
  }

  // Check MIME type
  const typeValidation = validateMimeType(file.type, allowedTypes);
  if (!typeValidation.success) {
    return typeValidation;
  }

  return {
    success: true,
    file,
    size: file.size,
    type: file.type
  };
}

/**
 * Validate file from FormData
 * @param formData - FormData object from request
 * @param fieldName - Field name containing the file (defaults to 'file')
 * @param options - Validation options
 * @returns Validation result with filename
 */
export function validateFormDataFile(
  formData: FormData,
  fieldName: string = 'file',
  options: ValidationOptions = {}
): FileValidationResult {
  const fileEntry = formData.get(fieldName);

  if (!fileEntry || !(fileEntry instanceof File)) {
    return {
      success: false,
      error: ERROR_MESSAGES.NO_FILE
    };
  }

  // Validate file
  const fileValidation = validateFile(fileEntry, options);
  if (!fileValidation.success) {
    return fileValidation;
  }

  // Validate extension
  const extValidation = validateFileExtension(fileEntry.name);
  if (!extValidation.success) {
    return extValidation;
  }

  return {
    success: true,
    file: fileEntry,
    filename: fileEntry.name,
    size: fileEntry.size,
    type: fileEntry.type
  };
}

/**
 * Validate Content-Type header
 * @param contentType - Content-Type header value
 * @returns Validation result with parsed info
 */
export function validateContentType(contentType: string): FileValidationResult {
  if (!contentType) {
    return {
      success: false,
      error: 'Content-Type header is required'
    };
  }

  if (contentType.includes('multipart/form-data')) {
    return { success: true };
  }

  if (contentType.includes('image/')) {
    return { success: true };
  }

  return {
    success: false,
    error: ERROR_MESSAGES.INVALID_CONTENT_TYPE
  };
}
