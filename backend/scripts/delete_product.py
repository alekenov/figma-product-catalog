#!/usr/bin/env python3
"""Script to delete product from Railway production database"""

import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment (will be injected by Railway)
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# Handle asyncpg vs psycopg2 URL schemes
if DATABASE_URL.startswith('postgresql+asyncpg'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')

# Create engine with connect_args for SSL
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "prefer"})

def find_product(search_name: str, shop_id: int = 8):
    """Find product by name"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name, price, type, enabled FROM product WHERE name LIKE :name AND shop_id = :shop_id"),
            {"name": f"%{search_name}%", "shop_id": shop_id}
        )
        products = result.fetchall()
        return products

def delete_product(product_id: int):
    """Delete product and related data"""
    with engine.begin() as conn:
        # Delete related data first (foreign key constraints)

        # Delete product images
        conn.execute(
            text("DELETE FROM productimage WHERE product_id = :id"),
            {"id": product_id}
        )

        # Delete product colors
        conn.execute(
            text("DELETE FROM productcolor WHERE product_id = :id"),
            {"id": product_id}
        )

        # Delete product tags
        conn.execute(
            text("DELETE FROM producttag WHERE product_id = :id"),
            {"id": product_id}
        )

        # Delete product stats
        conn.execute(
            text("DELETE FROM productstats WHERE product_id = :id"),
            {"id": product_id}
        )

        # Delete from recipe ingredients
        conn.execute(
            text("DELETE FROM recipe WHERE product_id = :id"),
            {"id": product_id}
        )

        # Finally delete the product
        result = conn.execute(
            text("DELETE FROM product WHERE id = :id"),
            {"id": product_id}
        )

        return result.rowcount

if __name__ == "__main__":
    search_term = "Белые розы премиум"

    print(f"Searching for product: {search_term}")
    products = find_product(search_term)

    if not products:
        print(f"No products found matching '{search_term}'")
        sys.exit(1)

    print(f"\nFound {len(products)} product(s):")
    for p in products:
        print(f"  ID: {p[0]}, Name: {p[1]}, Price: {p[2]}, Type: {p[3]}, Enabled: {p[4]}")

    if len(products) == 1:
        product_id = products[0][0]
        product_name = products[0][1]

        print(f"\nDeleting product ID {product_id}: {product_name}")
        rows_deleted = delete_product(product_id)
        print(f"✓ Product deleted successfully ({rows_deleted} row(s) affected)")
    else:
        print("\nMultiple products found. Please specify which one to delete.")
        sys.exit(1)
