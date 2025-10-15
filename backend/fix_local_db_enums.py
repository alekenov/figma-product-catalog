#!/usr/bin/env python3
"""Fix invalid enum values in local SQLite database"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "figma_catalog.db"

def fix_enums():
    """Fix invalid enum values"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔧 Fixing invalid enum values in local database...")

    # Fix order statuses
    print("\n1. Checking order statuses...")
    cursor.execute('SELECT id, status FROM "order" WHERE status NOT IN (\'NEW\', \'PAID\', \'ACCEPTED\', \'ASSEMBLED\', \'IN_PRODUCTION\', \'READY\', \'IN_DELIVERY\', \'DELIVERED\', \'CANCELLED\')')
    invalid_orders = cursor.fetchall()

    if invalid_orders:
        print(f"   Found {len(invalid_orders)} orders with invalid status:")
        for order_id, status in invalid_orders:
            print(f"   - Order {order_id}: '{status}' → 'NEW'")

        cursor.execute("""
            UPDATE "order"
            SET status='NEW'
            WHERE status NOT IN ('NEW', 'PAID', 'ACCEPTED', 'ASSEMBLED', 'IN_PRODUCTION', 'READY', 'IN_DELIVERY', 'DELIVERED', 'CANCELLED')
        """)
        print(f"   ✅ Fixed {cursor.rowcount} order statuses")
    else:
        print("   ✅ All order statuses are valid")

    # Fix user roles
    print("\n2. Checking user roles...")
    cursor.execute("SELECT id, phone, role FROM user WHERE role NOT IN ('SUPERADMIN', 'ADMIN', 'DIRECTOR', 'FLORIST', 'COURIER')")
    invalid_users = cursor.fetchall()

    if invalid_users:
        print(f"   Found {len(invalid_users)} users with invalid role:")
        for user_id, phone, role in invalid_users:
            # Map lowercase to uppercase
            if role and role.lower() == 'admin':
                new_role = 'ADMIN'
            elif role and role.lower() == 'director':
                new_role = 'DIRECTOR'
            elif role and role.lower() == 'florist':
                new_role = 'FLORIST'
            elif role and role.lower() == 'courier':
                new_role = 'COURIER'
            else:
                new_role = 'ADMIN'  # Default to ADMIN

            print(f"   - User {user_id} ({phone}): '{role}' → '{new_role}'")
            cursor.execute("UPDATE user SET role=? WHERE id=?", (new_role, user_id))

        print(f"   ✅ Fixed {len(invalid_users)} user roles")
    else:
        print("   ✅ All user roles are valid")

    conn.commit()
    conn.close()

    print("\n✅ Database enum cleanup completed!")

if __name__ == "__main__":
    fix_enums()
