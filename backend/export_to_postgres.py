#!/usr/bin/env python3
"""Export SQLite data to PostgreSQL-compatible SQL"""

import sqlite3
import json
from datetime import datetime

def sqlite_to_postgres_value(value, column_type=None):
    """Convert SQLite value to PostgreSQL format"""
    if value is None:
        return 'NULL'
    elif isinstance(value, bool) or (column_type == 'BOOLEAN' and isinstance(value, int)):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, str):
        # Escape single quotes
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, dict) or isinstance(value, list):
        # JSON columns
        escaped = json.dumps(value).replace("'", "''")
        return f"'{escaped}'::jsonb"
    else:
        return f"'{str(value)}'"

# Connect to SQLite
conn = sqlite3.connect('/Users/alekenov/figma-product-catalog/backend/figma_catalog.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Output file
with open('/Users/alekenov/figma-product-catalog/backend/postgres_data.sql', 'w') as f:
    f.write("-- PostgreSQL data export from SQLite\n")
    f.write("-- Generated: {}\n\n".format(datetime.now().isoformat()))

    # Define table order (respecting foreign key constraints)
    tables = [
        'product',
        'warehouseitem',
        'user',
        'shopsettings',
        '"order"',
        'orderitem',
        'warehouseoperation',
        'productrecipe',
        'inventorycheck',
        'inventorycheckitem',
        'orderreservation',
        'order_reservation',
        'teaminvitation',
        'client',
        'ordercounter'
    ]

    # Boolean columns mapping
    boolean_columns = {
        'product': ['enabled', 'is_featured'],
        'warehouseitem': [],
        'user': ['is_active'],
        'shopsettings': ['weekday_closed', 'weekend_closed', 'pickup_available', 'delivery_available'],
        'orderitem': [],
        'warehouseoperation': [],
        'productrecipe': ['is_optional'],
        'inventorycheck': [],
        'inventorycheckitem': [],
        'orderreservation': [],
        'order_reservation': [],
        'teaminvitation': [],
        'client': [],
        'ordercounter': []
    }

    # JSON columns mapping
    json_columns = {
        'product': ['colors', 'occasions', 'cities']
    }

    for table in tables:
        clean_table = table.strip('"')

        # Get column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        column_names = [col['name'] for col in columns]
        column_types = {col['name']: col['type'] for col in columns}

        # Get data
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if rows:
            f.write(f"\n-- Data for table {table}\n")

            for row in rows:
                values = []
                for col in column_names:
                    value = row[col]

                    # Check if it's a boolean column
                    is_boolean = clean_table in boolean_columns and col in boolean_columns[clean_table]

                    # Check if it's a JSON column
                    is_json = clean_table in json_columns and col in json_columns.get(clean_table, [])

                    if is_json and value:
                        try:
                            # Parse JSON string to object
                            value = json.loads(value) if isinstance(value, str) else value
                        except:
                            pass

                    values.append(sqlite_to_postgres_value(value, 'BOOLEAN' if is_boolean else None))

                columns_str = ', '.join(f'"{col}"' for col in column_names)
                values_str = ', '.join(values)
                f.write(f"INSERT INTO {table} ({columns_str}) VALUES ({values_str});\n")

    f.write("\n-- Reset sequences\n")
    for table in tables:
        clean_table = table.strip('"')
        f.write(f"SELECT setval(pg_get_serial_sequence('{clean_table}', 'id'), COALESCE(MAX(id), 1)) FROM {table};\n")

conn.close()
print("Export completed to postgres_data.sql")