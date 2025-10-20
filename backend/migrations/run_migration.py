#!/usr/bin/env python3
"""
Run SQL migration to link products with R2 images
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

def main():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    print(f"Connecting to database...")
    engine = create_engine(database_url)

    # Read SQL file
    sql_file = Path(__file__).parent / 'link_product_images.sql'
    with open(sql_file, 'r') as f:
        sql_content = f.read()

    print(f"Executing migration...")
    with engine.connect() as conn:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"[{i}/{len(statements)}] Executing statement...")
                try:
                    result = conn.execute(text(statement))
                    conn.commit()

                    # If it's a SELECT, print results
                    if statement.upper().startswith('SELECT'):
                        rows = result.fetchall()
                        print(f"  Found {len(rows)} products with images:")
                        for row in rows:
                            print(f"    ID {row[0]}: {row[1][:50]}... -> {row[2][-40:]}")
                    else:
                        print(f"  ✓ Updated {result.rowcount} rows")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    raise

    print("\n✅ Migration completed successfully!")

if __name__ == '__main__':
    main()
