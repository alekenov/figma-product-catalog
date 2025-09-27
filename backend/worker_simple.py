from workers import Response, WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Get URL path
        url = request.url
        path = url.split('/')[-1].split('?')[0]

        # Simple routing
        if "products" in url:
            # Query D1 database for products
            results = await self.env.DB.prepare(
                "SELECT * FROM products WHERE available = 1"
            ).all()

            return Response.json({
                "products": results.results if results else [],
                "total": len(results.results) if results else 0
            })

        # Default response
        return Response.json({
            "message": "Figma Product Catalog API",
            "database": "Cloudflare D1",
            "endpoints": ["/api/products"]
        })