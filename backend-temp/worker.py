"""
Simplified Cloudflare Worker for Figma Product Catalog API
Using built-in Python modules only
"""
from workers import WorkerEntrypoint, Response
import json


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        """Handle incoming requests"""
        url = request.url
        method = request.method
        path = url.split('?')[0].split('/')[-1]

        # Basic routing
        if method == "GET":
            if path == "" or path == "api":
                return self.handle_root()
            elif path == "products":
                return self.handle_get_products()
            elif path == "health":
                return self.handle_health()
        elif method == "POST":
            if path == "products":
                return await self.handle_create_product(request)
        elif method == "OPTIONS":
            # Handle CORS preflight
            return self.handle_cors_preflight()

        # 404 for unknown routes
        return Response(
            json.dumps({"error": "Not found"}),
            status=404,
            headers=self.get_cors_headers()
        )

    def get_cors_headers(self):
        """Get CORS headers for responses"""
        return {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }

    def handle_cors_preflight(self):
        """Handle CORS preflight requests"""
        return Response(
            "",
            status=204,
            headers=self.get_cors_headers()
        )

    def handle_root(self):
        """Root endpoint"""
        response_data = {
            "message": "Figma Product Catalog API on Cloudflare Workers",
            "version": self.env.API_VERSION,
            "endpoints": {
                "/api": "API info",
                "/api/health": "Health check",
                "/api/products": "Products endpoint (GET/POST)"
            }
        }
        return Response(
            json.dumps(response_data),
            headers=self.get_cors_headers()
        )

    def handle_health(self):
        """Health check endpoint"""
        return Response(
            json.dumps({"status": "healthy", "service": "Cloudflare Workers Python"}),
            headers=self.get_cors_headers()
        )

    def handle_get_products(self):
        """Get products - example data"""
        products = [
            {
                "id": 1,
                "name": "Букет роз",
                "price": 15000,
                "currency": "KZT",
                "available": True,
                "category": "bouquets",
                "image": "https://example.com/roses.jpg"
            },
            {
                "id": 2,
                "name": "Тюльпаны",
                "price": 8000,
                "currency": "KZT",
                "available": True,
                "category": "flowers",
                "image": "https://example.com/tulips.jpg"
            },
            {
                "id": 3,
                "name": "Орхидея в горшке",
                "price": 25000,
                "currency": "KZT",
                "available": False,
                "category": "potted",
                "image": "https://example.com/orchid.jpg"
            },
            {
                "id": 4,
                "name": "Свадебный букет",
                "price": 45000,
                "currency": "KZT",
                "available": True,
                "category": "wedding",
                "image": "https://example.com/wedding.jpg"
            }
        ]

        return Response(
            json.dumps({"products": products, "total": len(products)}),
            headers=self.get_cors_headers()
        )

    async def handle_create_product(self, request):
        """Create a new product (example - doesn't persist)"""
        try:
            # Get request body
            body = await request.text()
            product_data = json.loads(body)

            # Add ID and return
            product_data["id"] = 999
            product_data["created_at"] = "2025-09-26T18:00:00Z"

            return Response(
                json.dumps({
                    "message": "Product created successfully",
                    "product": product_data
                }),
                status=201,
                headers=self.get_cors_headers()
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=400,
                headers=self.get_cors_headers()
            )