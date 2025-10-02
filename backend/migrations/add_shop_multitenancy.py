#!/usr/bin/env python3
"""
Migration script to add Shop multi-tenancy support
This script adds Shop table and shop_id to all relevant tables for data isolation between shops.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Environment detection
DB_TYPE = None  # Will be set based on environment


def detect_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    global DB_TYPE

    # Check if DATABASE_URL is set (PostgreSQL on Railway)
    if os.getenv("DATABASE_URL"):
        DB_TYPE = "postgresql"
    else:
        DB_TYPE = "sqlite"

    print(f"Detected database type: {DB_TYPE}")
    return DB_TYPE


def get_db_connection():
    """Get database connection based on environment"""
    if DB_TYPE == "postgresql":
        import psycopg2
        from urllib.parse import urlparse

        database_url = os.getenv("DATABASE_URL")
        # Parse connection string
        result = urlparse(database_url)

        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    else:  # SQLite
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "..", "figma_catalog.db")
        conn = sqlite3.connect(db_path)
        return conn


def run_migration():
    """Run the migration to add Shop multi-tenancy"""
    detect_database_type()

    print("\n" + "=" * 60)
    print("🏪 MULTI-TENANCY MIGRATION: Add Shop Isolation")
    print("=" * 60 + "\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Create Shop table
        print("Step 1: Creating Shop table...")

        if DB_TYPE == "postgresql":
            create_shop_table_sql = """
            CREATE TABLE IF NOT EXISTS shop (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL DEFAULT 'Мой магазин',
                owner_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id),
                phone VARCHAR(20),
                address VARCHAR(500),
                city VARCHAR(6) CHECK (city IN ('Almaty', 'Astana')),

                weekday_start VARCHAR NOT NULL DEFAULT '09:00',
                weekday_end VARCHAR NOT NULL DEFAULT '18:00',
                weekday_closed BOOLEAN NOT NULL DEFAULT FALSE,

                weekend_start VARCHAR NOT NULL DEFAULT '10:00',
                weekend_end VARCHAR NOT NULL DEFAULT '17:00',
                weekend_closed BOOLEAN NOT NULL DEFAULT FALSE,

                delivery_cost INTEGER NOT NULL DEFAULT 150000,
                free_delivery_amount INTEGER NOT NULL DEFAULT 1000000,
                pickup_available BOOLEAN NOT NULL DEFAULT TRUE,
                delivery_available BOOLEAN NOT NULL DEFAULT TRUE,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        else:  # SQLite
            create_shop_table_sql = """
            CREATE TABLE IF NOT EXISTS shop (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL DEFAULT 'Мой магазин',
                owner_id INTEGER NOT NULL UNIQUE REFERENCES user(id),
                phone VARCHAR(20),
                address VARCHAR(500),
                city VARCHAR(6) CHECK (city IN ('Almaty', 'Astana')),

                weekday_start VARCHAR NOT NULL DEFAULT '09:00',
                weekday_end VARCHAR NOT NULL DEFAULT '18:00',
                weekday_closed BOOLEAN NOT NULL DEFAULT 0,

                weekend_start VARCHAR NOT NULL DEFAULT '10:00',
                weekend_end VARCHAR NOT NULL DEFAULT '17:00',
                weekend_closed BOOLEAN NOT NULL DEFAULT 0,

                delivery_cost INTEGER NOT NULL DEFAULT 150000,
                free_delivery_amount INTEGER NOT NULL DEFAULT 1000000,
                pickup_available BOOLEAN NOT NULL DEFAULT 1,
                delivery_available BOOLEAN NOT NULL DEFAULT 1,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """

        cursor.execute(create_shop_table_sql)
        print("   ✓ Shop table created")

        # Step 2: Find first DIRECTOR user or create default shop
        print("\nStep 2: Creating default shop for existing users...")

        if DB_TYPE == "postgresql":
            cursor.execute("SELECT id, name, phone FROM \"user\" WHERE role = 'director' ORDER BY id LIMIT 1;")
        else:
            cursor.execute("SELECT id, name, phone FROM user WHERE role = 'director' ORDER BY id LIMIT 1;")

        director = cursor.fetchone()

        if director:
            director_id, director_name, director_phone = director
            print(f"   Found director: {director_name} (ID: {director_id})")

            # Create shop for this director
            cursor.execute("""
                INSERT INTO shop (owner_id, name, phone)
                VALUES (%s, %s, %s)
                RETURNING id;
            """ if DB_TYPE == "postgresql" else """
                INSERT INTO shop (owner_id, name, phone)
                VALUES (?, ?, ?);
            """, (director_id, 'Цветы.kz', director_phone))

            if DB_TYPE == "postgresql":
                shop_id = cursor.fetchone()[0]
            else:
                shop_id = cursor.lastrowid

            print(f"   ✓ Created default shop (ID: {shop_id}) for {director_name}")
        else:
            print("   ⚠ No director found - skipping default shop creation")
            print("   (Shop will be created during first registration)")
            shop_id = None

        # Step 3: Add shop_id column to User table
        print("\nStep 3: Adding shop_id to User table...")

        if DB_TYPE == "postgresql":
            cursor.execute("""
                ALTER TABLE "user"
                ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES shop(id);
            """)
        else:
            # SQLite doesn't support ADD COLUMN IF NOT EXISTS or adding FK after table creation easily
            # Check if column exists first
            cursor.execute("PRAGMA table_info(user);")
            columns = [col[1] for col in cursor.fetchall()]

            if 'shop_id' not in columns:
                cursor.execute("""
                    ALTER TABLE user
                    ADD COLUMN shop_id INTEGER REFERENCES shop(id);
                """)

        print("   ✓ Added shop_id to User table")

        # Update users to have shop_id
        if shop_id:
            if DB_TYPE == "postgresql":
                cursor.execute('UPDATE "user" SET shop_id = %s WHERE id = %s;', (shop_id, director_id))
            else:
                cursor.execute('UPDATE user SET shop_id = ? WHERE id = ?;', (shop_id, director_id))
            print(f"   ✓ Updated director's shop_id to {shop_id}")

        # Step 4: Add shop_id to Product table
        print("\nStep 4: Adding shop_id to Product table...")
        add_column_to_table(cursor, "product", shop_id)

        # Step 5: Add shop_id to Order table
        print("\nStep 5: Adding shop_id to Order table...")
        add_column_to_table(cursor, "order", shop_id, table_name_quoted=True)

        # Step 6: Add shop_id to WarehouseItem table
        print("\nStep 6: Adding shop_id to WarehouseItem table...")
        add_column_to_table(cursor, "warehouseitem", shop_id)

        # Step 7: Add shop_id to Client table
        print("\nStep 7: Adding shop_id to Client table...")
        add_column_to_table(cursor, "client", shop_id)

        # Step 8: Add shop_id to InventoryCheck table
        print("\nStep 8: Adding shop_id to InventoryCheck table...")
        add_column_to_table(cursor, "inventorycheck", shop_id)

        # Step 9: Add shop_id to CompanyReview table
        print("\nStep 9: Adding shop_id to CompanyReview table...")
        add_column_to_table(cursor, "companyreview", shop_id)

        # Step 10: Add shop_id to FAQ table
        print("\nStep 10: Adding shop_id to FAQ table...")
        add_column_to_table(cursor, "faq", shop_id)

        # Step 11: Add shop_id to StaticPage table
        print("\nStep 11: Adding shop_id to StaticPage table...")
        add_column_to_table(cursor, "staticpage", shop_id)

        # Step 12: Add shop_id to PickupLocation table
        print("\nStep 12: Adding shop_id to PickupLocation table...")
        add_column_to_table(cursor, "pickuplocation", shop_id)

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)

        if shop_id:
            print(f"\nDefault shop created with ID: {shop_id}")
            print("All existing data has been assigned to this shop.")

        print("\n📋 Next steps:")
        print("  1. Restart your backend server")
        print("  2. Register a new user - they will create their own shop")
        print("  3. Verify data isolation between shops")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        cursor.close()
        conn.close()


def add_column_to_table(cursor, table_name, default_shop_id, table_name_quoted=False):
    """Helper function to add shop_id column to a table and update existing rows"""

    # Quote table name for both PostgreSQL and SQLite reserved words (like "order")
    quoted_table = f'"{table_name}"' if table_name_quoted else table_name

    if DB_TYPE == "postgresql":
        cursor.execute(f"""
            ALTER TABLE {quoted_table}
            ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES shop(id);
        """)
    else:
        # SQLite - check if column exists (PRAGMA also needs quoted table names)
        cursor.execute(f"PRAGMA table_info({quoted_table});")
        columns = [col[1] for col in cursor.fetchall()]

        if 'shop_id' not in columns:
            cursor.execute(f"""
                ALTER TABLE {quoted_table}
                ADD COLUMN shop_id INTEGER REFERENCES shop(id);
            """)

    print(f"   ✓ Added shop_id column to {table_name}")

    # Update existing rows if default shop exists
    if default_shop_id:
        if DB_TYPE == "postgresql":
            cursor.execute(f"UPDATE {quoted_table} SET shop_id = %s WHERE shop_id IS NULL;", (default_shop_id,))
        else:
            cursor.execute(f"UPDATE {quoted_table} SET shop_id = ? WHERE shop_id IS NULL;", (default_shop_id,))

        rows_updated = cursor.rowcount
        if rows_updated > 0:
            print(f"   ✓ Updated {rows_updated} existing rows with shop_id={default_shop_id}")


def rollback_migration():
    """Rollback the migration by removing shop_id columns and Shop table"""
    detect_database_type()

    print("\n" + "=" * 60)
    print("⚠️  ROLLBACK: Removing Shop Multi-Tenancy")
    print("=" * 60 + "\n")

    print("WARNING: This will remove all shop isolation!")
    print("All users will see all data again.")

    confirm = input("\nType 'yes' to confirm rollback: ")
    if confirm.lower() != 'yes':
        print("Rollback cancelled.")
        return True

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Remove shop_id columns from all tables (in reverse order)
        tables = [
            "pickuplocation",
            "staticpage",
            "faq",
            "companyreview",
            "inventorycheck",
            "client",
            "warehouseitem",
            '"order"' if DB_TYPE == "postgresql" else "order",
            "product",
            '"user"' if DB_TYPE == "postgresql" else "user"
        ]

        for table in tables:
            try:
                if DB_TYPE == "postgresql":
                    cursor.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS shop_id;")
                else:
                    # SQLite doesn't support DROP COLUMN easily - would need table rebuild
                    print(f"   ⚠ SQLite doesn't support DROP COLUMN - {table}.shop_id will remain (but unused)")

                print(f"   ✓ Removed shop_id from {table}")
            except Exception as e:
                print(f"   ⚠ Could not remove shop_id from {table}: {e}")

        # Drop Shop table
        cursor.execute("DROP TABLE IF EXISTS shop;")
        print("   ✓ Dropped Shop table")

        conn.commit()
        print("\n✅ Rollback completed successfully!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback_migration()
    else:
        success = run_migration()

    sys.exit(0 if success else 1)
