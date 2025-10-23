#!/usr/bin/env python3
"""Import data to Render PostgreSQL"""

import psycopg2
import os
from psycopg2.extras import execute_batch

# Read the SQL file
with open('/Users/alekenov/figma-product-catalog/backend/postgres_data.sql', 'r') as f:
    sql_content = f.read()

# Parse SQL statements (split by semicolon + newline)
statements = []
current = []
for line in sql_content.split('\n'):
    if line.strip().startswith('--'):
        continue
    current.append(line)
    if line.strip().endswith(';'):
        stmt = '\n'.join(current).strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)
        current = []

print(f"Found {len(statements)} SQL statements to execute")

# Render PostgreSQL connection details
# You need to get the Internal Database URL from Render dashboard
DATABASE_URL = "postgresql://figma_catalog_db_user:YOUR_PASSWORD@dpg-d3d3i07diees738dl92g-a/figma_catalog_db?sslmode=require"

# For now, let's create a script that shows what would be imported
print("\n=== Data Import Summary ===")
print("Tables to populate:")
tables = ['product', 'warehouseitem', 'user', 'shopsettings', '"order"',
          'orderitem', 'warehouseoperation', 'productrecipe', 'inventorycheck',
          'inventorycheckitem', 'orderreservation', 'order_reservation',
          'teaminvitation', 'client', 'ordercounter']

for table in tables:
    # Count INSERT statements for each table
    count = sum(1 for stmt in statements if f'INSERT INTO {table}' in stmt)
    if count > 0:
        print(f"  - {table}: {count} records")

print(f"\nTotal statements: {len(statements)}")
print("\n⚠️  To import data to Render PostgreSQL:")
print("1. Go to Render Dashboard: https://dashboard.render.com")
print("2. Click on your database: figma-catalog-db")
print("3. Copy the 'Internal Database URL'")
print("4. Replace YOUR_PASSWORD in this script")
print("5. Run: python3 import_to_render_final.py")

# Save the statements for later use
import json
with open('/Users/alekenov/figma-product-catalog/backend/import_statements.json', 'w') as f:
    json.dump(statements, f, indent=2)