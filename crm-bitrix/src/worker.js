const BITRIX_API_URL = 'https://cvety.kz/api/v2';
const BITRIX_TOKEN = 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    // Proxy API requests through Cloudflare to avoid CORS issues
    if (pathname.startsWith('/api/v2/')) {
      const apiPath = pathname.replace('/api/v2', '');
      const apiUrl = new URL(apiPath + url.search, BITRIX_API_URL);

      const apiRequest = new Request(apiUrl, {
        method: request.method,
        headers: {
          'Authorization': `Bearer ${BITRIX_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: request.method === 'GET' ? undefined : await request.text(),
      });

      try {
        const response = await fetch(apiRequest);

        // Clone response and add CORS headers
        const corsResponse = new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: new Headers(response.headers),
        });

        // Set proper CORS headers (single origin only)
        corsResponse.headers.set('Access-Control-Allow-Origin', '*');
        corsResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
        corsResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        corsResponse.headers.set('Access-Control-Max-Age', '3600');

        // Remove duplicate CORS headers if present
        corsResponse.headers.delete('access-control-allow-origin');
        corsResponse.headers.set('Access-Control-Allow-Origin', '*');

        return corsResponse;
      } catch (error) {
        return new Response(
          JSON.stringify({ success: false, error: 'API request failed: ' + error.message }),
          {
            status: 500,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
            }
          }
        );
      }
    }

    // Handle OPTIONS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          'Access-Control-Max-Age': '3600',
        },
      });
    }

    try {
      // Try to serve the requested file from assets
      let response = await env.ASSETS.fetch(request);

      // If not found and it's a route (not an asset), serve index.html for SPA
      if (response.status === 404 && !pathname.includes('.')) {
        response = await env.ASSETS.fetch(new Request(new URL('/index.html', url).toString()));
      }

      return response;
    } catch (error) {
      // Fallback: serve index.html for SPA routing
      return env.ASSETS.fetch(new Request(new URL('/index.html', url).toString()));
    }
  },
};
