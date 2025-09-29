#!/usr/bin/env python3
"""
Migration script to add authentication and shop settings tables
This script adds User, ShopSettings, and TeamInvitation tables with proper enums and relationships.
"""

import sqlite3
import sys
import os
from datetime import datetime


def run_migration(db_path: str):
    """Run the migration to add authentication and shop settings tables"""

    # SQL to create the User table
    create_user_table_sql = """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        role VARCHAR(8) NOT NULL CHECK (role IN ('director', 'manager', 'florist', 'courier')),
        password_hash VARCHAR(255) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        invited_by INTEGER,
        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        PRIMARY KEY (id),
        UNIQUE (phone),
        FOREIGN KEY(invited_by) REFERENCES user (id)
    );
    """

    # SQL to create the ShopSettings table
    create_shop_settings_table_sql = """
    CREATE TABLE IF NOT EXISTS shopsettings (
        id INTEGER NOT NULL,
        shop_name VARCHAR(200) NOT NULL,
        address VARCHAR(500) NOT NULL,
        city VARCHAR(6) NOT NULL CHECK (city IN ('Almaty', 'Astana')),
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
        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        PRIMARY KEY (id)
    );
    """

    # SQL to create the TeamInvitation table
    create_team_invitation_table_sql = """
    CREATE TABLE IF NOT EXISTS teaminvitation (
        id INTEGER NOT NULL,
        phone VARCHAR(20) NOT NULL,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(8) NOT NULL CHECK (role IN ('director', 'manager', 'florist', 'courier')),
        invited_by INTEGER NOT NULL,
        status VARCHAR(8) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired')),
        invitation_code VARCHAR(6) NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        PRIMARY KEY (id),
        FOREIGN KEY(invited_by) REFERENCES user (id)
    );
    """

    # Create indexes for better performance
    create_indexes_sql = [
        # User table indexes
        "CREATE INDEX IF NOT EXISTS idx_user_phone ON user(phone);",
        "CREATE INDEX IF NOT EXISTS idx_user_role ON user(role);",
        "CREATE INDEX IF NOT EXISTS idx_user_is_active ON user(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_user_invited_by ON user(invited_by);",

        # TeamInvitation table indexes
        "CREATE INDEX IF NOT EXISTS idx_teaminvitation_phone ON teaminvitation(phone);",
        "CREATE INDEX IF NOT EXISTS idx_teaminvitation_invitation_code ON teaminvitation(invitation_code);",
        "CREATE INDEX IF NOT EXISTS idx_teaminvitation_status ON teaminvitation(status);",
        "CREATE INDEX IF NOT EXISTS idx_teaminvitation_expires_at ON teaminvitation(expires_at);",
        "CREATE INDEX IF NOT EXISTS idx_teaminvitation_invited_by ON teaminvitation(invited_by);",

        # ShopSettings table indexes (minimal since it's a singleton table)
        "CREATE INDEX IF NOT EXISTS idx_shopsettings_city ON shopsettings(city);"
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Running migration: Add authentication and shop settings tables")
        print(f"Database path: {db_path}")

        # Check which tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user', 'shopsettings', 'teaminvitation');")
        existing_tables = {row[0] for row in cursor.fetchall()}

        # Create User table
        if 'user' in existing_tables:
            print("✓ User table already exists")
        else:
            cursor.execute(create_user_table_sql)
            print("✓ Created user table")

        # Create ShopSettings table
        if 'shopsettings' in existing_tables:
            print("✓ ShopSettings table already exists")
        else:
            cursor.execute(create_shop_settings_table_sql)
            print("✓ Created shopsettings table")

        # Create TeamInvitation table
        if 'teaminvitation' in existing_tables:
            print("✓ TeamInvitation table already exists")
        else:
            cursor.execute(create_team_invitation_table_sql)
            print("✓ Created teaminvitation table")

        # Create indexes
        for index_sql in create_indexes_sql:
            try:
                cursor.execute(index_sql)
            except sqlite3.Error as e:
                print(f"Note: Index creation failed (may already exist): {e}")

        print("✓ Created/verified indexes on all tables")

        # Commit the changes
        conn.commit()
        print("✓ Migration completed successfully")

        # Verify all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user', 'shopsettings', 'teaminvitation');")
        created_tables = {row[0] for row in cursor.fetchall()}

        if created_tables == {'user', 'shopsettings', 'teaminvitation'}:
            print("✓ Verified: All authentication and shop settings tables exist")

            # Show table schemas
            for table_name in ['user', 'shopsettings', 'teaminvitation']:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print(f"\n{table_name.upper()} table schema:")
                for col in columns:
                    print(f"  - {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        else:
            print("✗ Error: Not all tables were created")
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
    """Rollback the migration by dropping the authentication and shop settings tables"""

    # Note: Be careful with rollback - these tables may have dependent data
    rollback_sql = [
        "DROP TABLE IF EXISTS teaminvitation;",
        "DROP TABLE IF EXISTS user;",
        "DROP TABLE IF EXISTS shopsettings;"
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Rolling back migration: Remove authentication and shop settings tables")
        print(f"Database path: {db_path}")

        # Warning about data loss
        print("⚠️  WARNING: This will permanently delete all user accounts, team invitations, and shop settings!")

        # Drop tables in reverse order to respect foreign key constraints
        for sql in rollback_sql:
            try:
                cursor.execute(sql)
                table_name = sql.split()[-1].rstrip(';')
                print(f"✓ Dropped table {table_name}")
            except sqlite3.Error as e:
                print(f"Note: Failed to drop table (may not exist): {e}")

        conn.commit()
        print("✓ Rollback completed successfully")

        # Verify tables were dropped
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user', 'shopsettings', 'teaminvitation');")
        remaining_tables = [row[0] for row in cursor.fetchall()]

        if not remaining_tables:
            print("✓ Verified: All authentication and shop settings tables removed")
        else:
            print(f"✗ Warning: Some tables still exist: {remaining_tables}")
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
            print("⚠️  WARNING: You are about to delete all authentication data!")
            confirm = input("Type 'yes' to confirm rollback: ")
            if confirm.lower() == 'yes':
                success = rollback_migration(db_path)
            else:
                print("Rollback cancelled.")
                success = True
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