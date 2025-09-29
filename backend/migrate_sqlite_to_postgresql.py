#!/usr/bin/env python3
"""
SQLite to PostgreSQL migration script for figma_catalog database
"""

import sqlite3
import psycopg2
import json
from datetime import datetime

# Database connections
SQLITE_DB = '/Users/alekenov/figma-product-catalog/backend/figma_catalog.db'
POSTGRESQL_URL = "postgresql://postgres:BrWQJSWSsYoJhVagWicsDJHMVRNDJUAj@yamanote.proxy.rlwy.net:35081/railway"

def migrate_database():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(POSTGRESQL_URL)
    pg_cursor = pg_conn.cursor()

    try:
        # Get all tables from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in sqlite_cursor.fetchall()]

        print(f"Found {len(tables)} tables to migrate: {', '.join(tables)}")

        # Migrate each table
        for table_name in tables:
            print(f"\n📋 Migrating table: {table_name}")

            # Get table schema from SQLite
            sqlite_cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns_info = sqlite_cursor.fetchall()

            # Build CREATE TABLE statement for PostgreSQL
            # Quote table name if it's a reserved word
            quoted_table_name = f'"{table_name}"' if table_name in ['order', 'user'] else table_name
            create_table_sql = f"DROP TABLE IF EXISTS {quoted_table_name} CASCADE;\n"
            create_table_sql += f"CREATE TABLE {quoted_table_name} (\n"

            column_definitions = []
            for col in columns_info:
                col_name = col['name']
                col_type = col['type'].upper()
                not_null = " NOT NULL" if col['notnull'] else ""
                default = f" DEFAULT {col['dflt_value']}" if col['dflt_value'] else ""

                # Convert SQLite types to PostgreSQL types
                if 'INT' in col_type:
                    if col['pk'] and table_name != 'ordercounter':  # ordercounter uses specific ID
                        pg_type = 'SERIAL PRIMARY KEY'
                    else:
                        pg_type = 'INTEGER'
                        if col['pk']:
                            pg_type += ' PRIMARY KEY'
                elif col_type in ['TEXT', 'VARCHAR', 'CHAR']:
                    pg_type = 'VARCHAR'
                elif col_type == 'REAL' or col_type == 'FLOAT':
                    pg_type = 'REAL'
                elif col_type == 'BOOLEAN':
                    pg_type = 'BOOLEAN'
                elif col_type == 'DATETIME':
                    pg_type = 'TIMESTAMP'
                    if 'CURRENT_TIMESTAMP' in str(default).upper():
                        default = ' DEFAULT CURRENT_TIMESTAMP'
                elif col_type == 'JSON':
                    pg_type = 'JSONB'
                else:
                    pg_type = 'TEXT'

                # Handle special column names that need quotes
                if col_name in ['order', 'user']:
                    col_name = f'"{col_name}"'

                # Handle camelCase column names - PostgreSQL prefers snake_case but we'll keep original
                if any(c.isupper() for c in col_name) and not col_name.startswith('"'):
                    col_name = f'"{col_name}"'

                column_def = f"    {col_name} {pg_type}{not_null}{default}"
                column_definitions.append(column_def)

            create_table_sql += ",\n".join(column_definitions)
            create_table_sql += "\n);"

            # Execute CREATE TABLE
            try:
                pg_cursor.execute(create_table_sql)
                print(f"  ✅ Created table structure for {table_name}")
            except Exception as e:
                print(f"  ❌ Error creating table {table_name}: {e}")
                continue

            # Migrate data
            sqlite_cursor.execute(f'SELECT * FROM "{table_name}"')
            rows = sqlite_cursor.fetchall()

            if rows:
                # Get column names (handling special cases)
                col_names = [col['name'] for col in columns_info]
                # Quote special column names
                quoted_cols = []
                for col in col_names:
                    if col in ['order', 'user'] or any(c.isupper() for c in col):
                        quoted_cols.append(f'"{col}"')
                    else:
                        quoted_cols.append(col)

                # Prepare INSERT statement (use quoted table name)
                placeholders = ', '.join(['%s'] * len(col_names))
                insert_sql = f"INSERT INTO {quoted_table_name} ({', '.join(quoted_cols)}) VALUES ({placeholders})"

                # Convert and insert data
                converted_rows = []
                for row in rows:
                    converted_row = []
                    for i, value in enumerate(row):
                        col_type = columns_info[i]['type'].upper()

                        # Convert boolean values
                        if col_type == 'BOOLEAN':
                            if value in [0, '0', 'f', 'false', False]:
                                converted_row.append(False)
                            elif value in [1, '1', 't', 'true', True]:
                                converted_row.append(True)
                            else:
                                converted_row.append(None)
                        # Convert JSON
                        elif col_type == 'JSON':
                            if value:
                                try:
                                    # Parse and re-stringify to ensure valid JSON
                                    converted_row.append(json.dumps(json.loads(value)))
                                except:
                                    converted_row.append(value)
                            else:
                                converted_row.append(None)
                        else:
                            converted_row.append(value)

                    converted_rows.append(converted_row)

                # Execute batch insert
                try:
                    pg_cursor.executemany(insert_sql, converted_rows)
                    print(f"  ✅ Migrated {len(rows)} rows to {table_name}")
                except Exception as e:
                    print(f"  ❌ Error inserting data into {table_name}: {e}")
                    pg_conn.rollback()
                    continue

        # Commit all changes
        pg_conn.commit()
        print("\n✅ Migration completed successfully!")

        # Print summary
        print("\n📊 Migration Summary:")
        for table_name in tables:
            quoted_table_name = f'"{table_name}"' if table_name in ['order', 'user'] else table_name
            pg_cursor.execute(f"SELECT COUNT(*) FROM {quoted_table_name}")
            count = pg_cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_database()