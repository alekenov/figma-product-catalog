/**
 * Pages Function: GET /image/[id]
 * Serve image from R2 with CDN caching
 */

export async function onRequestGet(context) {
  const { request, env, params } = context;
  const imageId = params.id;

  // Sanitize key to prevent path traversal
  const sanitizedKey = imageId.replace(/\.\./g, '').replace(/^\/+/, '');

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