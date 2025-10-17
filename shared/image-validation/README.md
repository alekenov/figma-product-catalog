# Image Validation Shared Package

Consolidated image validation and utility functions for Flower Shop image uploading services.

## Overview

This package provides centralized image validation logic used by:
- **Cloudflare Image Worker** (`image-worker/src/index.ts`)
- **Cloudflare Pages Function** (`functions/api/upload.js`)

## Features

- ✅ File size validation (configurable limits)
- ✅ MIME type validation (jpeg, png, webp, gif)
- ✅ File extension validation
- ✅ FormData file extraction and validation
- ✅ Unique ID generation
- ✅ File extension detection
- ✅ Image URL generation
- ✅ 100% test coverage

## Installation

```bash
npm install @flower-shop/image-validation
```

Or with pnpm (recommended):
```bash
pnpm add @flower-shop/image-validation
```

## Usage

### Basic File Validation

```typescript
import { validateFile, validateFileSize, validateMimeType } from '@flower-shop/image-validation';

// Validate a file blob
const file = new File(['image data'], 'photo.jpg', { type: 'image/jpeg' });
const result = validateFile(file);

if (result.success) {
  console.log(`File is valid: ${result.filename} (${result.size} bytes)`);
} else {
  console.error(result.error);
}
```

### Validate FormData

```typescript
import { validateFormDataFile } from '@flower-shop/image-validation';

// In your request handler
const formData = await request.formData();
const result = validateFormDataFile(formData, 'file');

if (!result.success) {
  return new Response(JSON.stringify({ error: result.error }), { status: 400 });
}

const { file, filename, size, type } = result;
```

### Custom Validation Options

```typescript
import { validateFile } from '@flower-shop/image-validation';

const result = validateFile(file, {
  maxFileSize: 5 * 1024 * 1024, // 5MB
  allowedTypes: ['image/jpeg', 'image/png'] // Only JPEG and PNG
});
```

### Generate Unique ID and Storage Key

```typescript
import { generateId, generateStorageKey, generateImageUrl } from '@flower-shop/image-validation';

const imageId = generateId();  // "abcd1234-xyz567"
const key = generateStorageKey(imageId, 'photo.jpg', 'image/jpeg');  // "abcd1234-xyz567.jpg"
const url = generateImageUrl('example.workers.dev', key);  // "https://example.workers.dev/abcd1234-xyz567.jpg"
```

### In Cloudflare Worker (TypeScript)

```typescript
import { validateFile, generateId, generateStorageKey, generateImageUrl } from '@flower-shop/image-validation';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === 'POST') {
      const formData = await request.formData();
      const file = formData.get('file');

      // Validate
      const validation = validateFile(file);
      if (!validation.success) {
        return new Response(JSON.stringify({ error: validation.error }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Generate ID and key
      const imageId = generateId();
      const key = generateStorageKey(imageId, file.name, file.type);

      // Upload to R2
      await env.IMAGES.put(key, file, {
        httpMetadata: { contentType: file.type }
      });

      // Generate URL
      const hostname = new URL(request.url).hostname;
      const url = generateImageUrl(hostname, key);

      return new Response(JSON.stringify({
        success: true,
        imageId: key,
        url: url,
        size: file.size,
        type: file.type
      }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
```

### In Cloudflare Pages Function (JavaScript)

```javascript
import { validateFormDataFile, generateId, generateStorageKey } from '@flower-shop/image-validation';

export async function onRequestPost(context) {
  const { request, env } = context;

  const formData = await request.formData();
  const validation = validateFormDataFile(formData, 'file');

  if (!validation.success) {
    return jsonResponse({ error: validation.error }, 400);
  }

  const { file, filename } = validation;
  const imageId = generateId();
  const key = generateStorageKey(imageId, filename, file.type);

  // Upload to R2
  await env.IMAGES.put(key, file, {
    httpMetadata: { contentType: file.type }
  });

  return jsonResponse({
    success: true,
    imageId: key,
    url: `https://${new URL(request.url).hostname}/${key}`,
    size: file.size,
    type: file.type
  }, 201);
}
```

## API Reference

### Constants

```typescript
import {
  ALLOWED_TYPES,           // ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  MAX_FILE_SIZE,           // 10 * 1024 * 1024 (10MB)
  MIME_TYPE_MAP,           // { 'image/jpeg': 'jpg', ... }
  ALLOWED_EXTENSIONS,      // ['jpg', 'jpeg', 'png', 'webp', 'gif']
  ERROR_MESSAGES           // Error message constants
} from '@flower-shop/image-validation';
```

### Validation Functions

#### `validateFile(file: File | Blob | null, options?: ValidationOptions): FileValidationResult`

Validates a file object (size and MIME type).

#### `validateFileSize(fileSize: number, maxSize?: number): FileValidationResult`

Validates only file size.

#### `validateMimeType(mimeType: string, allowedTypes?: string[]): FileValidationResult`

Validates only MIME type.

#### `validateFileExtension(filename: string): FileValidationResult`

Validates file extension based on filename.

#### `validateFormDataFile(formData: FormData, fieldName?: string, options?: ValidationOptions): FileValidationResult`

Extracts and validates a file from FormData.

#### `validateContentType(contentType: string): FileValidationResult`

Validates HTTP Content-Type header.

### Utility Functions

#### `generateId(): string`

Generates a unique image ID (e.g., "abc123xyz-def456uvw").

#### `getExtension(filename: string, mimeType: string): string`

Extracts file extension from filename or MIME type.

#### `generateStorageKey(imageId: string, filename: string, mimeType: string): string`

Generates R2/S3 storage key (e.g., "abc123xyz-def456uvw.jpg").

#### `generateImageUrl(workerHost: string, storageKey: string): string`

Generates full CDN URL for image.

## Types

```typescript
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
}
```

## Testing

Run tests with coverage:

```bash
pnpm build
pnpm test:coverage
```

## File Size Limits

Default: 10MB

To use different limits:
- Cloudflare Free: 100MB (file size limit)
- Cloudflare Pages: 100MB (file size limit)

Update `MAX_FILE_SIZE` in `src/constants.ts` if needed.

## MIME Types

Currently supported:
- `image/jpeg` → `.jpg`
- `image/png` → `.png`
- `image/webp` → `.webp`
- `image/gif` → `.gif`

To add more types, update `ALLOWED_TYPES` and `MIME_TYPE_MAP` in `src/constants.ts`.

## Migration Guide

### From image-worker (before)

```typescript
// Before: Validation logic inline
const ALLOWED_TYPES = ['image/jpeg', '...'];
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// After: Import from package
import { validateFile, generateId, generateStorageKey } from '@flower-shop/image-validation';
```

### From functions/api/upload.js (before)

```javascript
// Before: Duplicate validation
const ALLOWED_TYPES = ['image/jpeg', '...'];
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// After: Import from package
import { validateFormDataFile, generateId, generateStorageKey } from '@flower-shop/image-validation';
```

## Contributing

To add new validation rules or utility functions:

1. Add types to `src/types.ts`
2. Add constants to `src/constants.ts`
3. Implement functions in appropriate file
4. Add tests to `src/*.test.ts`
5. Export from `src/index.ts`
6. Run `pnpm test:coverage` to verify

## License

MIT
