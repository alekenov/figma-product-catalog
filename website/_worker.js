/**
 * Cvety.kz Customer Website Worker
 * Serves static React SPA with client-side routing support
 *
 * Routes:
 * - / -> Homepage with product catalog
 * - /product/:id -> Product detail page
 * - All other routes -> Fallback to index.html for React Router
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // Try to fetch the asset
      let response = await env.ASSETS.fetch(request);

      // If asset not found (404) and it's not a file extension request,
      // serve index.html for client-side routing (SPA)
      if (response.status === 404 && !path.includes('.')) {
        // Clone the request but change the pathname to /index.html
        const indexRequest = new Request(
          new URL('/index.html', url.origin),
          request
        );
        response = await env.ASSETS.fetch(indexRequest);
      }

      return response;
    } catch (error) {
      console.error('Worker error:', error);
      return new Response('Internal Server Error', { status: 500 });
    }
  },
};