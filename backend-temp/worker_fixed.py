from workers import Response, WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        """Handle incoming HTTP requests"""
        # Parse URL
        url_parts = request.url.split('/')

        # Check if requesting products
        if 'products' in request.url:
            try:
                # Execute D1 query - note the correct method is 'run()'
                result = await self.env.DB.prepare(
                    "SELECT * FROM products WHERE available = 1"
                ).run()

                # Return results as JSON
                return Response.json({
                    "products": result["results"] if result else [],
                    "total": len(result["results"]) if result and "results" in result else 0
                })
            except Exception as e:
                return Response.json({
                    "error": str(e),
                    "message": "Database query failed"
                }, status=500)

        # Check if requesting categories
        if 'categories' in request.url:
            try:
                result = await self.env.DB.prepare(
                    "SELECT * FROM categories ORDER BY name"
                ).run()

                return Response.json({
                    "categories": result["results"] if result else []
                })
            except Exception as e:
                return Response.json({"error": str(e)}, status=500)

        # Root endpoint - API info
        return Response.json({
            "message": "Figma Product Catalog API",
            "version": "1.0.0",
            "database": "Cloudflare D1",
            "endpoints": {
                "/api": "API information",
                "/api/products": "Get all products",
                "/api/categories": "Get all categories"
            }
        })