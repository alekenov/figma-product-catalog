/**
 * HTTP response helpers with CORS support
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

/**
 * Create JSON response with CORS headers
 */
export function jsonResponse(data: any, status = 200): Response {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS,
    },
  });
}

/**
 * Create success response
 */
export function successResponse(data: any, status = 200): Response {
  return jsonResponse({ success: true, ...data }, status);
}

/**
 * Create error response
 */
export function errorResponse(error: string, status = 400, details?: any): Response {
  return jsonResponse({
    success: false,
    error,
    ...(details && { details }),
  }, status);
}

/**
 * Handle CORS preflight
 */
export function handleCORS(): Response {
  return new Response(null, {
    headers: CORS_HEADERS,
  });
}

/**
 * Create 404 response
 */
export function notFoundResponse(message = 'Not Found'): Response {
  return errorResponse(message, 404);
}

/**
 * Create 500 response
 */
export function internalErrorResponse(error: Error): Response {
  console.error('Internal error:', error);
  return errorResponse(
    'Internal Server Error',
    500,
    process.env.ENVIRONMENT === 'development' ? {
      message: error.message,
      stack: error.stack,
    } : undefined
  );
}
