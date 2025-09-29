"""
Cloudflare Worker with D1 database for Figma Product Catalog
"""
from workers import WorkerEntrypoint, Response
import json


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        """Handle incoming requests"""
        url = request.url
        method = request.method
        path_parts = url.split('/')
        path = path_parts[-1].split('?')[0] if path_parts else ""

        # Extract product ID from path like /api/products/123
        product_id = None
        if len(path_parts) >= 2 and path_parts[-2] == 'products' and path_parts[-1].isdigit():
            product_id = int(path_parts[-1])
            path = 'product_detail'

        # CORS headers
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }

        # Handle OPTIONS for CORS
        if method == "OPTIONS":
            return Response("", status=204, headers=headers)

        try:
            # Route handling
            if method == "GET":
                if path == "" or path == "api":
                    return await self.handle_root(headers)
                elif path == "products":
                    return await self.handle_get_products(headers)
                elif path == "product_detail" and product_id:
                    return await self.handle_get_product(product_id, headers)
                elif path == "categories":
                    return await self.handle_get_categories(headers)
            elif method == "POST":
                if path == "products":
                    return await self.handle_create_product(request, headers)
                elif path == "orders":
                    return await self.handle_create_order(request, headers)
            elif method == "PUT":
                if path == "product_detail" and product_id:
                    return await self.handle_update_product(product_id, request, headers)

            # 404 for unknown routes
            return Response(
                json.dumps({"error": "Not found"}),
                status=404,
                headers=headers
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers=headers
            )

    async def handle_root(self, headers):
        """Root endpoint"""
        response_data = {
            "message": "Figma Product Catalog API with D1 Database",
            "version": self.env.API_VERSION,
            "database": "Cloudflare D1",
            "endpoints": {
                "/api": "API info",
                "/api/products": "Get all products",
                "/api/products/{id}": "Get product by ID",
                "/api/categories": "Get all categories",
                "/api/orders": "Create order (POST)"
            }
        }
        return Response(json.dumps(response_data), headers=headers)

    async def handle_get_products(self, headers):
        """Get all products from D1 database"""
        try:
            # Query D1 database
            result = await self.env.DB.prepare(
                "SELECT * FROM products WHERE available = 1 ORDER BY created_at DESC"
            ).all()

            products = []
            for row in result.results:
                products.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"],
                    "price": row["price"],
                    "currency": row["currency"],
                    "available": bool(row["available"]),
                    "category": row["category"],
                    "stock_quantity": row["stock_quantity"],
                    "image_url": row["image_url"]
                })

            return Response(
                json.dumps({"products": products, "total": len(products)}),
                headers=headers
            )
        except Exception as e:
            return Response(
                json.dumps({"error": f"Database error: {str(e)}"}),
                status=500,
                headers=headers
            )

    async def handle_get_product(self, product_id, headers):
        """Get single product by ID"""
        try:
            result = await self.env.DB.prepare(
                "SELECT * FROM products WHERE id = ?"
            ).bind(product_id).first()

            if not result:
                return Response(
                    json.dumps({"error": "Product not found"}),
                    status=404,
                    headers=headers
                )

            product = {
                "id": result["id"],
                "name": result["name"],
                "description": result["description"],
                "price": result["price"],
                "currency": result["currency"],
                "available": bool(result["available"]),
                "category": result["category"],
                "stock_quantity": result["stock_quantity"],
                "image_url": result["image_url"]
            }

            return Response(json.dumps(product), headers=headers)
        except Exception as e:
            return Response(
                json.dumps({"error": f"Database error: {str(e)}"}),
                status=500,
                headers=headers
            )

    async def handle_get_categories(self, headers):
        """Get all categories"""
        try:
            result = await self.env.DB.prepare(
                "SELECT * FROM categories ORDER BY name"
            ).all()

            categories = []
            for row in result.results:
                categories.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"]
                })

            return Response(
                json.dumps({"categories": categories}),
                headers=headers
            )
        except Exception as e:
            return Response(
                json.dumps({"error": f"Database error: {str(e)}"}),
                status=500,
                headers=headers
            )

    async def handle_create_product(self, request, headers):
        """Create new product"""
        try:
            body = await request.text()
            product_data = json.loads(body)

            # Insert into D1
            result = await self.env.DB.prepare(
                """
                INSERT INTO products (name, description, price, category, available, stock_quantity, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
            ).bind(
                product_data.get("name"),
                product_data.get("description", ""),
                product_data.get("price"),
                product_data.get("category", ""),
                product_data.get("available", True),
                product_data.get("stock_quantity", 0),
                product_data.get("image_url", "")
            ).run()

            return Response(
                json.dumps({
                    "message": "Product created successfully",
                    "id": result.meta.last_row_id
                }),
                status=201,
                headers=headers
            )
        except Exception as e:
            return Response(
                json.dumps({"error": f"Failed to create product: {str(e)}"}),
                status=400,
                headers=headers
            )

    async def handle_update_product(self, product_id, request, headers):
        """Update product"""
        try:
            body = await request.text()
            product_data = json.loads(body)

            # Update in D1
            await self.env.DB.prepare(
                """
                UPDATE products
                SET name = ?, description = ?, price = ?, available = ?, stock_quantity = ?
                WHERE id = ?
                """
            ).bind(
                product_data.get("name"),
                product_data.get("description"),
                product_data.get("price"),
                product_data.get("available"),
                product_data.get("stock_quantity"),
                product_id
            ).run()

            return Response(
                json.dumps({"message": "Product updated successfully"}),
                headers=headers
            )
        except Exception as e:
            return Response(
                json.dumps({"error": f"Failed to update product: {str(e)}"}),
                status=400,
                headers=headers
            )

    async def handle_create_order(self, request, headers):
        """Create new order"""
        try:
            body = await request.text()
            order_data = json.loads(body)

            # Insert order
            result = await self.env.DB.prepare(
                """
                INSERT INTO orders (customer_name, customer_phone, delivery_address, total_amount, status)
                VALUES (?, ?, ?, ?, ?)
                """
            ).bind(
                order_data.get("customer_name"),
                order_data.get("customer_phone"),
                order_data.get("delivery_address", ""),
                order_data.get("total_amount"),
                "pending"
            ).run()

            order_id = result.meta.last_row_id

            # Insert order items if provided
            if "items" in order_data:
                for item in order_data["items"]:
                    await self.env.DB.prepare(
                        """
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                        """
                    ).bind(
                        order_id,
                        item.get("product_id"),
                        item.get("quantity"),
                        item.get("price")
                    ).run()

            return Response(
                json.dumps({
                    "message": "Order created successfully",
                    "order_id": order_id
                }),
                status=201,
                headers=headers
            )
        except Exception as e:
            return Response(
                json.dumps({"error": f"Failed to create order: {str(e)}"}),
                status=400,
                headers=headers
            )