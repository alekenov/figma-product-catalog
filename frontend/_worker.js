/**
 * Flower Shop Frontend Worker
 * Combines static site serving with R2 image storage
 * Routes:
 * - POST /api/upload -> Upload image to R2
 * - GET /image/{id} -> Serve image from R2 with CDN cache
 * - Everything else -> Static assets from dist/
 */

// Allowed image types
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // POST /api/upload - Upload new image
      if (path === '/api/upload' && request.method === 'POST') {
        return await handleUpload(request, env);
      }

      // GET /image/{imageId} - Serve image from R2
      if (path.startsWith('/image/') && request.method === 'GET') {
        const imageId = path.slice(7); // Remove '/image/' prefix
        return await handleGetImage(imageId, env);
      }

      // All other requests -> serve static assets from dist/
      return env.ASSETS.fetch(request);
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Internal Server Error',
        message: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  },
};

/**
 * Handle image upload to R2
 */
async function handleUpload(request, env) {
  try {
    const contentType = request.headers.get('Content-Type') || '';

    if (!contentType.includes('multipart/form-data')) {
      return jsonResponse({ error: 'Content-Type must be multipart/form-data' }, 400);
    }

    const formData = await request.formData();
    const fileEntry = formData.get('file');

    if (!fileEntry || !(fileEntry instanceof File)) {
      return jsonResponse({ error: 'No file provided' }, 400);
    }

    const file = fileEntry;
    const filename = fileEntry.name;

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return jsonResponse({
        error: `File too large. Max size: ${MAX_FILE_SIZE / 1024 / 1024}MB`
      }, 400);
    }

    // Validate file type
    const fileType = file.type;
    if (!ALLOWED_TYPES.includes(fileType)) {
      return jsonResponse({
        error: `Invalid file type: ${fileType}. Allowed: ${ALLOWED_TYPES.join(', ')}`
      }, 400);
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
    const imageUrl = `https://${workerHost}/image/${key}`;

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
      message: error.message
    }, 500);
  }
}

/**
 * Handle image retrieval from R2
 */
async function handleGetImage(key, env) {
  // Sanitize key to prevent path traversal
  const sanitizedKey = key.replace(/\.\./g, '').replace(/^\/+/, '');

  if (!sanitizedKey) {
    return new Response('Invalid image key', { status: 400 });
  }

  try {
    const object = await env.IMAGES.get(sanitizedKey);

    if (!object) {
      return new Response(JSON.stringify({
        error: 'Image not found',
        key: sanitizedKey
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Set response headers with CDN caching
    const headers = new Headers();
    headers.set('Content-Type', object.httpMetadata?.contentType || 'application/octet-stream');
    headers.set('Cache-Control', 'public, max-age=31536000, immutable'); // Cache for 1 year
    headers.set('ETag', object.httpEtag);

    return new Response(object.body, {
      headers,
      status: 200,
    });
  } catch (error) {
    console.error('Get image error:', error);
    return new Response('Failed to retrieve image', { status: 500 });
  }
}

/**
 * Helper: Generate unique ID
 */
function generateId() {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 15);
  return `${timestamp}-${randomPart}`;
}

/**
 * Helper: Get file extension from filename or mime type
 */
function getExtension(filename, mimeType) {
  // Try to get from filename
  const match = filename.match(/\.([^.]+)$/);
  if (match) {
    return match[1].toLowerCase();
  }

  // Fallback to mime type
  const mimeMap = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'image/gif': 'gif',
  };

  return mimeMap[mimeType] || 'jpg';
}

/**
 * Helper: JSON response
 */
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}