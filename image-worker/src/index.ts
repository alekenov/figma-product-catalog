/**
 * Flower Shop Image Worker
 * Handles image upload to R2 and serves images with CDN caching
 */

import {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  generateId,
  getExtension,
} from '@flower-shop/image-validation';

export interface Env {
  IMAGES: R2Bucket;
  ENVIRONMENT?: string;
}

// CORS headers
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    try {
      // GET / - Health check
      if (path === '/' && request.method === 'GET') {
        return new Response(JSON.stringify({
          status: 'ok',
          service: 'flower-shop-images',
          version: '1.0.0'
        }), {
          headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
        });
      }

      // GET /debug - List R2 objects
      if (path === '/debug' && request.method === 'GET') {
        try {
          const listed = await env.IMAGES.list({ limit: 10 });
          return new Response(JSON.stringify({
            success: true,
            objects: listed.objects.map(obj => ({
              key: obj.key,
              size: obj.size,
              uploaded: obj.uploaded
            })),
            truncated: listed.truncated
          }), {
            headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
          });
        } catch (error) {
          return jsonResponse({
            error: 'Failed to list objects',
            message: error instanceof Error ? error.message : 'Unknown error'
          }, 500);
        }
      }

      // POST /upload - Upload new image
      if (path === '/upload' && request.method === 'POST') {
        return await handleUpload(request, env);
      }

      // GET /{imageId} - Serve image (must be last to not catch other routes)
      if (request.method === 'GET' && path.length > 1) {
        return await handleGetImage(path.slice(1), env);
      }

      return new Response('Not Found', { status: 404, headers: CORS_HEADERS });
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Internal Server Error',
        message: error instanceof Error ? error.message : 'Unknown error'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
      });
    }
  },
};

/**
 * Handle image upload
 */
async function handleUpload(request: Request, env: Env): Promise<Response> {
  try {
    const contentType = request.headers.get('Content-Type') || '';

    // Parse multipart/form-data or direct binary upload
    let file: File | Blob | null = null;
    let filename = 'upload';

    if (contentType.includes('multipart/form-data')) {
      const formData = await request.formData();
      const fileEntry = formData.get('file');

      if (!fileEntry || !(fileEntry instanceof File)) {
        return jsonResponse({ error: 'No file provided' }, 400);
      }

      file = fileEntry;
      filename = fileEntry.name;
    } else if (contentType.includes('image/')) {
      // Direct binary upload
      file = await request.blob();
    } else {
      return jsonResponse({ error: 'Invalid content type. Use multipart/form-data or image/* binary' }, 400);
    }

    // Validate file
    if (!file) {
      return jsonResponse({ error: 'No file provided' }, 400);
    }

    if (file.size > MAX_FILE_SIZE) {
      return jsonResponse({ error: `File too large. Max size: ${MAX_FILE_SIZE / 1024 / 1024}MB` }, 400);
    }

    const fileType = file.type || contentType;
    if (!ALLOWED_TYPES.includes(fileType)) {
      return jsonResponse({ error: `Invalid file type: ${fileType}. Allowed: ${ALLOWED_TYPES.join(', ')}` }, 400);
    }

    // Generate unique ID
    const imageId = generateId();
    const extension = getExtension(filename, fileType);
    const key = `${imageId}.${extension}`;

    // Upload to R2
    await env.IMAGES.put(key, file, {
      httpMetadata: {
        contentType: fileType,
      },
      customMetadata: {
        originalName: filename,
        uploadedAt: new Date().toISOString(),
      },
    });

    // Return success with image URL
    const workerHost = new URL(request.url).hostname;
    const imageUrl = `https://${workerHost}/${key}`;

    return jsonResponse({
      success: true,
      imageId: key,
      url: imageUrl,
      size: file.size,
      type: fileType,
    }, 201);
  } catch (error) {
    console.error('Upload error:', error);
    return jsonResponse({
      error: 'Upload failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, 500);
  }
}

/**
 * Handle image retrieval
 */
async function handleGetImage(key: string, env: Env): Promise<Response> {
  // Sanitize key to prevent path traversal
  const sanitizedKey = key.replace(/\.\./g, '').replace(/^\/+/, '');

  console.log('GET request for key:', key, '-> sanitized:', sanitizedKey);

  if (!sanitizedKey) {
    return new Response('Invalid image key', { status: 400, headers: CORS_HEADERS });
  }

  try {
    const object = await env.IMAGES.get(sanitizedKey);
    console.log('R2 get result:', object ? 'found' : 'not found');

    if (!object) {
      return new Response(JSON.stringify({
        error: 'Image not found',
        key: sanitizedKey,
        debug: 'File not found in R2'
      }), {
        status: 404,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }

    // Get image metadata
    const headers = new Headers(CORS_HEADERS);
    headers.set('Content-Type', object.httpMetadata?.contentType || 'application/octet-stream');
    headers.set('Cache-Control', 'public, max-age=31536000, immutable'); // Cache for 1 year
    headers.set('ETag', object.httpEtag);

    // Check If-None-Match for 304 Not Modified
    const ifNoneMatch = object.httpEtag;
    if (ifNoneMatch) {
      headers.set('ETag', ifNoneMatch);
    }

    return new Response(object.body, {
      headers,
      status: 200,
    });
  } catch (error) {
    console.error('Get image error:', error);
    return new Response('Failed to retrieve image', {
      status: 500,
      headers: CORS_HEADERS
    });
  }
}


/**
 * Helper: JSON response with CORS
 */
function jsonResponse(data: any, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS,
    },
  });
}