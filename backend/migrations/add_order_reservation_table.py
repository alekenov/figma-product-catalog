#!/usr/bin/env python3
"""
Migration script to add order_reservation table
This script adds the order reservation functionality to track reserved warehouse items for orders.
"""

import sqlite3
import sys
import os
from datetime import datetime


def run_migration(db_path: str):
    """Run the migration to add order_reservation table"""

    # SQL to create the order_reservation table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS order_reservation (
        id INTEGER NOT NULL,
        order_id INTEGER NOT NULL,
        warehouse_item_id INTEGER NOT NULL,
        reserved_quantity INTEGER NOT NULL,
        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        PRIMARY KEY (id),
        FOREIGN KEY(order_id) REFERENCES "order" (id),
        FOREIGN KEY(warehouse_item_id) REFERENCES warehouseitem (id)
    );
    """

    # Create indexes for better performance
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_order_reservation_order_id ON order_reservation(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_reservation_warehouse_item_id ON order_reservation(warehouse_item_id);"
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Running migration: Add order_reservation table")
        print(f"Database path: {db_path}")

        # Create the table
        cursor.execute(create_table_sql)
        print("✓ Created order_reservation table")

        # Create indexes
        for index_sql in create_indexes_sql:
            cursor.execute(index_sql)
        print("✓ Created indexes on order_reservation table")

        # Commit the changes
        conn.commit()
        print("✓ Migration completed successfully")

        # Verify the table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_reservation';")
        result = cursor.fetchone()

        if result:
            print("✓ Verified: order_reservation table exists")

            # Show table schema
            cursor.execute("PRAGMA table_info(order_reservation);")
            columns = cursor.fetchall()
            print("\nTable schema:")
            for col in columns:
                print(f"  - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        else:
            print("✗ Error: order_reservation table was not created")
            return False

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

    return True


def rollback_migration(db_path: str):
    """Rollback the migration by dropping the order_reservation table"""

    rollback_sql = "DROP TABLE IF EXISTS order_reservation;"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Rolling back migration: Remove order_reservation table")
        print(f"Database path: {db_path}")

        # Drop the table
        cursor.execute(rollback_sql)
        conn.commit()

        print("✓ Rollback completed successfully")

        # Verify the table was dropped
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_reservation';")
        result = cursor.fetchone()

        if not result:
            print("✓ Verified: order_reservation table removed")
        else:
            print("✗ Error: order_reservation table still exists")
            return False

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

    return True


if __name__ == "__main__":
    # Default database path
    default_db_path = os.path.join(os.path.dirname(__file__), "..", "figma_catalog.db")

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "rollback":
            # Rollback mode
            db_path = sys.argv[2] if len(sys.argv) > 2 else default_db_path
            success = rollback_migration(db_path)
        else:
            # Migration with custom db path
            db_path = sys.argv[1]
            success = run_migration(db_path)
    else:
        # Default migration
        db_path = default_db_path
        success = run_migration(db_path)

    # Exit with appropriate code
    sys.exit(0 if success else 1)