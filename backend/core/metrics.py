"""
Prometheus metrics collection for FastAPI application.

Provides application-level metrics:
- HTTP request counts by method, endpoint, status
- HTTP request durations (histogram)
- HTTP error counts by type
- Request ID tracking
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable


# ============================================================================
# Metrics Definitions
# ============================================================================

# Request counter: tracks total requests by method, endpoint, and status
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request duration: tracks request processing time
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Error counter: tracks errors by method, endpoint, and error type
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)


# ============================================================================
# Metrics Middleware
# ============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically collect Prometheus metrics for all requests.

    Collects:
    - Request counts (by method, endpoint, status)
    - Request durations (by method, endpoint)
    - Error counts (by method, endpoint, error_type)

    Works alongside RequestIDMiddleware for full observability.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""

        # Skip metrics endpoint itself to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Extract request details
        method = request.method
        endpoint = request.url.path

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response: Response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            status_code = response.status_code
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Track errors (4xx and 5xx)
            if status_code >= 400:
                error_type = "client_error" if status_code < 500 else "server_error"
                http_errors_total.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()

            return response

        except Exception as e:
            # Record exception metrics
            duration = time.time() - start_time

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                error_type=type(e).__name__
            ).inc()

            # Re-raise to let FastAPI handle it
            raise


# ============================================================================
# Metrics Endpoint Handler
# ============================================================================

async def metrics_handler() -> Response:
    """
    Expose Prometheus metrics at /metrics endpoint.

    Returns metrics in Prometheus text format.

    Example Prometheus scrape config:
        scrape_configs:
          - job_name: 'flower-shop-backend'
            static_configs:
              - targets: ['localhost:8014']
    """
    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Utility Functions
# ============================================================================

def normalize_endpoint(path: str) -> str:
    """
    Normalize endpoint path for cardinality reduction.

    Replaces dynamic segments (IDs, UUIDs) with placeholders
    to prevent high cardinality in metrics.

    Examples:
        /api/v1/orders/12345 → /api/v1/orders/{id}
        /api/v1/products/abc-def → /api/v1/products/{id}

    Args:
        path: Original request path

    Returns:
        Normalized path with placeholders
    """
    import re

    # Replace numeric IDs
    path = re.sub(r'/\d+', '/{id}', path)

    # Replace UUID-like strings
    path = re.sub(r'/[a-f0-9-]{32,}', '/{uuid}', path)

    # Replace tracking IDs (9 digits)
    path = re.sub(r'/\d{9}', '/{tracking_id}', path)

    return path


# ============================================================================
# Custom Metrics (Optional - for business logic)
# ============================================================================

# You can add custom business metrics here:
# Example:
# orders_created_total = Counter('orders_created_total', 'Total orders created', ['shop_id'])
# order_value_dollars = Histogram('order_value_dollars', 'Order value in dollars', ['shop_id'])
