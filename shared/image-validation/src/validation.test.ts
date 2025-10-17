/**
 * Tests for image validation functions
 */
import { describe, it, expect } from 'vitest';
import {
  validateFileSize,
  validateMimeType,
  validateFileExtension,
  validateFile,
  validateContentType
} from './validation';
import {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  ERROR_MESSAGES
} from './constants';

describe('validateFileSize', () => {
  it('should accept valid file sizes', () => {
    const result = validateFileSize(1024); // 1KB
    expect(result.success).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('should reject files larger than max size', () => {
    const result = validateFileSize(MAX_FILE_SIZE + 1);
    expect(result.success).toBe(false);
    expect(result.error).toContain('too large');
  });

  it('should reject zero-sized files', () => {
    const result = validateFileSize(0);
    expect(result.success).toBe(false);
  });

  it('should reject negative sizes', () => {
    const result = validateFileSize(-100);
    expect(result.success).toBe(false);
  });

  it('should respect custom max size', () => {
    const customMax = 5 * 1024 * 1024; // 5MB
    const result = validateFileSize(customMax + 1, customMax);
    expect(result.success).toBe(false);
  });

  it('should accept files exactly at max size', () => {
    const result = validateFileSize(MAX_FILE_SIZE);
    expect(result.success).toBe(true);
  });
});

describe('validateMimeType', () => {
  it('should accept allowed MIME types', () => {
    for (const mimeType of ALLOWED_TYPES) {
      const result = validateMimeType(mimeType);
      expect(result.success).toBe(true);
    }
  });

  it('should reject invalid MIME types', () => {
    const result = validateMimeType('image/bmp');
    expect(result.success).toBe(false);
    expect(result.error).toContain('Invalid');
  });

  it('should reject empty MIME type', () => {
    const result = validateMimeType('');
    expect(result.success).toBe(false);
  });

  it('should respect custom allowed types', () => {
    const result = validateMimeType('image/png', ['image/jpeg', 'image/gif']);
    expect(result.success).toBe(false);
  });

  it('should accept custom allowed types', () => {
    const result = validateMimeType('image/png', ['image/jpeg', 'image/png']);
    expect(result.success).toBe(true);
  });
});

describe('validateFileExtension', () => {
  it('should accept valid extensions', () => {
    const validExtensions = ['image.jpg', 'photo.png', 'picture.webp', 'gif.gif'];
    for (const filename of validExtensions) {
      const result = validateFileExtension(filename);
      expect(result.success).toBe(true);
    }
  });

  it('should accept jpeg extension', () => {
    const result = validateFileExtension('photo.jpeg');
    expect(result.success).toBe(true);
  });

  it('should reject invalid extensions', () => {
    const result = validateFileExtension('document.pdf');
    expect(result.success).toBe(false);
    expect(result.error).toContain('Invalid');
  });

  it('should reject files without extension', () => {
    const result = validateFileExtension('noextension');
    expect(result.success).toBe(false);
    expect(result.error).toContain('extension');
  });

  it('should be case insensitive', () => {
    const result = validateFileExtension('photo.JPG');
    expect(result.success).toBe(true);
  });

  it('should reject empty filename', () => {
    const result = validateFileExtension('');
    expect(result.success).toBe(false);
  });

  it('should handle filenames with multiple dots', () => {
    const result = validateFileExtension('my.photo.backup.jpg');
    expect(result.success).toBe(true);
  });
});

describe('validateFile', () => {
  it('should reject null files', () => {
    const result = validateFile(null);
    expect(result.success).toBe(false);
    expect(result.error).toContain('No file');
  });

  it('should reject undefined files', () => {
    const result = validateFile(undefined as any);
    expect(result.success).toBe(false);
  });

  it('should validate complete file object', () => {
    const blob = new Blob(['fake image data'], { type: 'image/jpeg' });
    const result = validateFile(blob);
    expect(result.success).toBe(true);
    expect(result.file).toBe(blob);
    expect(result.size).toBe(blob.size);
    expect(result.type).toBe('image/jpeg');
  });

  it('should reject oversized files', () => {
    // Note: In browser, Blob size is limited, so this is more of a unit test
    const blob = new Blob(new Array(MAX_FILE_SIZE + 1), { type: 'image/jpeg' });
    const result = validateFile(blob);
    expect(result.success).toBe(false);
  });

  it('should respect custom validation options', () => {
    const blob = new Blob(['data'], { type: 'image/png' });
    const result = validateFile(blob, {
      allowedTypes: ['image/jpeg'], // PNG is not allowed
      maxFileSize: MAX_FILE_SIZE
    });
    expect(result.success).toBe(false);
  });
});

describe('validateContentType', () => {
  it('should accept multipart/form-data', () => {
    const result = validateContentType('multipart/form-data; boundary=something');
    expect(result.success).toBe(true);
  });

  it('should accept image/* types', () => {
    const result = validateContentType('image/jpeg');
    expect(result.success).toBe(true);
  });

  it('should reject invalid content types', () => {
    const result = validateContentType('application/json');
    expect(result.success).toBe(false);
    expect(result.error).toContain(ERROR_MESSAGES.INVALID_CONTENT_TYPE);
  });

  it('should reject empty content type', () => {
    const result = validateContentType('');
    expect(result.success).toBe(false);
  });

  it('should handle content type with parameters', () => {
    const result = validateContentType('multipart/form-data; boundary=----');
    expect(result.success).toBe(true);
  });
});
