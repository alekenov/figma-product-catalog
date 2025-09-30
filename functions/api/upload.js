/**
 * Pages Function: POST /api/upload
 * Upload image to R2 storage
 */

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export async function onRequestPost(context) {
  const { request, env } = context;

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

function generateId() {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 15);
  return `${timestamp}-${randomPart}`;
}

function getExtension(filename, mimeType) {
  const match = filename.match(/\.([^.]+)$/);
  if (match) {
    return match[1].toLowerCase();
  }

  const mimeMap = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'image/gif': 'gif',
  };

  return mimeMap[mimeType] || 'jpg';
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}