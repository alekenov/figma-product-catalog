#!/usr/bin/env python3
"""
Phone Number Migration Script

This script normalizes all phone numbers in the database to +7XXXXXXXXXX format
and handles potential duplicate conflicts.

Usage:
    python migrate_phone_numbers.py --dry-run  # Preview changes without applying
    python migrate_phone_numbers.py            # Apply changes
"""

import argparse
import sys
from sqlmodel import Session, select, create_engine
from collections import defaultdict
from typing import List, Dict, Tuple

from models.users import User, Client
from models.orders import Order
from models.shop import Shop
from utils import normalize_phone_number, validate_phone_number


def get_db_session():
    """Create database session from environment"""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment")

    engine = create_engine(database_url, echo=False)
    return Session(engine)


def analyze_phone_duplicates(session: Session) -> Dict[str, List]:
    """
    Analyze potential phone number duplicates after normalization.

    Returns:
        Dictionary with duplicate analysis for each table
    """
    print("\n" + "=" * 80)
    print("ANALYZING PHONE NUMBER DUPLICATES")
    print("=" * 80)

    results = {
        "users": [],
        "clients": [],
        "orders": [],
        "shops": []
    }

    # 1. Check User table (phone must be globally unique)
    print("\n1. Checking User table (globally unique phone)...")
    users = session.exec(select(User)).all()

    phone_to_users = defaultdict(list)
    for user in users:
        if user.phone:
            try:
                normalized = normalize_phone_number(user.phone)
                phone_to_users[normalized].append({
                    "id": user.id,
                    "name": user.name,
                    "original": user.phone,
                    "normalized": normalized
                })
            except ValueError as e:
                print(f"   ⚠️  WARNING: User {user.id} has invalid phone: {user.phone} - {e}")

    duplicates = {phone: users for phone, users in phone_to_users.items() if len(users) > 1}
    if duplicates:
        print(f"   ❌ Found {len(duplicates)} duplicate phone numbers after normalization:")
        for phone, user_list in duplicates.items():
            print(f"      {phone}:")
            for u in user_list:
                print(f"         - User #{u['id']} ({u['name']}): {u['original']} → {u['normalized']}")
        results["users"] = duplicates
    else:
        print("   ✅ No duplicates found")

    # 2. Check Client table (phone + shop_id must be unique)
    print("\n2. Checking Client table (unique per shop)...")
    clients = session.exec(select(Client)).all()

    shop_phone_to_clients = defaultdict(list)
    for client in clients:
        if client.phone:
            try:
                normalized = normalize_phone_number(client.phone)
                key = (client.shop_id, normalized)
                shop_phone_to_clients[key].append({
                    "id": client.id,
                    "name": client.customerName,
                    "shop_id": client.shop_id,
                    "original": client.phone,
                    "normalized": normalized
                })
            except ValueError as e:
                print(f"   ⚠️  WARNING: Client {client.id} has invalid phone: {client.phone} - {e}")

    duplicates = {key: clients for key, clients in shop_phone_to_clients.items() if len(clients) > 1}
    if duplicates:
        print(f"   ❌ Found {len(duplicates)} duplicate client phones within shops:")
        for (shop_id, phone), client_list in duplicates.items():
            print(f"      Shop #{shop_id}, {phone}:")
            for c in client_list:
                print(f"         - Client #{c['id']} ({c['name']}): {c['original']} → {c['normalized']}")
        results["clients"] = duplicates
    else:
        print("   ✅ No duplicates found")

    # 3. Check Order table (no unique constraint, just report)
    print("\n3. Checking Order table (no unique constraint)...")
    orders = session.exec(select(Order)).all()

    invalid_orders = []
    for order in orders:
        for field, value in [
            ("phone", order.phone),
            ("recipient_phone", order.recipient_phone),
            ("sender_phone", order.sender_phone)
        ]:
            if value:
                try:
                    normalize_phone_number(value)
                except ValueError as e:
                    invalid_orders.append({
                        "order_id": order.id,
                        "tracking_id": order.tracking_id,
                        "field": field,
                        "value": value,
                        "error": str(e)
                    })

    if invalid_orders:
        print(f"   ⚠️  Found {len(invalid_orders)} invalid phone numbers:")
        for inv in invalid_orders[:5]:  # Show first 5
            print(f"      Order #{inv['order_id']} ({inv['tracking_id']}): {inv['field']}={inv['value']}")
        if len(invalid_orders) > 5:
            print(f"      ... and {len(invalid_orders) - 5} more")
        results["orders"] = invalid_orders
    else:
        print("   ✅ All phone numbers valid")

    # 4. Check Shop table (no unique constraint)
    print("\n4. Checking Shop table (no unique constraint)...")
    shops = session.exec(select(Shop)).all()

    invalid_shops = []
    for shop in shops:
        if shop.phone:
            try:
                normalize_phone_number(shop.phone)
            except ValueError as e:
                invalid_shops.append({
                    "shop_id": shop.id,
                    "name": shop.name,
                    "phone": shop.phone,
                    "error": str(e)
                })

    if invalid_shops:
        print(f"   ⚠️  Found {len(invalid_shops)} invalid phone numbers:")
        for inv in invalid_shops:
            print(f"      Shop #{inv['shop_id']} ({inv['name']}): {inv['phone']}")
        results["shops"] = invalid_shops
    else:
        print("   ✅ All phone numbers valid")

    return results


def migrate_phone_numbers(session: Session, dry_run: bool = True):
    """
    Normalize all phone numbers in the database.

    Args:
        session: Database session
        dry_run: If True, only preview changes without committing
    """
    print("\n" + "=" * 80)
    if dry_run:
        print("DRY RUN MODE - No changes will be applied")
    else:
        print("MIGRATION MODE - Changes will be applied")
    print("=" * 80)

    total_updated = 0

    # 1. Migrate Users
    print("\n1. Migrating User table...")
    users = session.exec(select(User)).all()
    updated_users = 0

    for user in users:
        if user.phone:
            try:
                normalized = normalize_phone_number(user.phone)
                if normalized != user.phone:
                    print(f"   User #{user.id} ({user.name}): {user.phone} → {normalized}")
                    if not dry_run:
                        user.phone = normalized
                    updated_users += 1
            except ValueError as e:
                print(f"   ⚠️  SKIP User #{user.id}: Invalid phone {user.phone}")

    print(f"   Updated {updated_users} users")
    total_updated += updated_users

    # 2. Migrate Clients
    print("\n2. Migrating Client table...")
    clients = session.exec(select(Client)).all()
    updated_clients = 0

    for client in clients:
        if client.phone:
            try:
                normalized = normalize_phone_number(client.phone)
                if normalized != client.phone:
                    print(f"   Client #{client.id} (Shop {client.shop_id}): {client.phone} → {normalized}")
                    if not dry_run:
                        client.phone = normalized
                    updated_clients += 1
            except ValueError as e:
                print(f"   ⚠️  SKIP Client #{client.id}: Invalid phone {client.phone}")

    print(f"   Updated {updated_clients} clients")
    total_updated += updated_clients

    # 3. Migrate Orders
    print("\n3. Migrating Order table...")
    orders = session.exec(select(Order)).all()
    updated_orders = 0

    for order in orders:
        order_updated = False

        # Phone
        if order.phone:
            try:
                normalized = normalize_phone_number(order.phone)
                if normalized != order.phone:
                    print(f"   Order #{order.id}: phone {order.phone} → {normalized}")
                    if not dry_run:
                        order.phone = normalized
                    order_updated = True
            except ValueError:
                print(f"   ⚠️  SKIP Order #{order.id}.phone: {order.phone}")

        # Recipient phone
        if order.recipient_phone:
            try:
                normalized = normalize_phone_number(order.recipient_phone)
                if normalized != order.recipient_phone:
                    print(f"   Order #{order.id}: recipient_phone {order.recipient_phone} → {normalized}")
                    if not dry_run:
                        order.recipient_phone = normalized
                    order_updated = True
            except ValueError:
                print(f"   ⚠️  SKIP Order #{order.id}.recipient_phone: {order.recipient_phone}")

        # Sender phone
        if order.sender_phone:
            try:
                normalized = normalize_phone_number(order.sender_phone)
                if normalized != order.sender_phone:
                    print(f"   Order #{order.id}: sender_phone {order.sender_phone} → {normalized}")
                    if not dry_run:
                        order.sender_phone = normalized
                    order_updated = True
            except ValueError:
                print(f"   ⚠️  SKIP Order #{order.id}.sender_phone: {order.sender_phone}")

        if order_updated:
            updated_orders += 1

    print(f"   Updated {updated_orders} orders")
    total_updated += updated_orders

    # 4. Migrate Shops
    print("\n4. Migrating Shop table...")
    shops = session.exec(select(Shop)).all()
    updated_shops = 0

    for shop in shops:
        if shop.phone:
            try:
                normalized = normalize_phone_number(shop.phone)
                if normalized != shop.phone:
                    print(f"   Shop #{shop.id} ({shop.name}): {shop.phone} → {normalized}")
                    if not dry_run:
                        shop.phone = normalized
                    updated_shops += 1
            except ValueError:
                print(f"   ⚠️  SKIP Shop #{shop.id}: Invalid phone {shop.phone}")

    print(f"   Updated {updated_shops} shops")
    total_updated += updated_shops

    # Commit or rollback
    if not dry_run and total_updated > 0:
        try:
            session.commit()
            print(f"\n✅ Successfully migrated {total_updated} records")
        except Exception as e:
            session.rollback()
            print(f"\n❌ Migration failed: {e}")
            print("   All changes rolled back")
            raise
    else:
        session.rollback()
        print(f"\n📋 Dry run complete. Would update {total_updated} records")

    return total_updated


def main():
    parser = argparse.ArgumentParser(description="Migrate phone numbers to normalized format")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze duplicates, don't migrate"
    )

    args = parser.parse_args()

    try:
        session = get_db_session()

        # Step 1: Analyze duplicates
        duplicates = analyze_phone_duplicates(session)

        # If there are user or client duplicates, stop
        if duplicates["users"] or duplicates["clients"]:
            print("\n" + "=" * 80)
            print("⚠️  CRITICAL: Duplicate phone numbers found!")
            print("=" * 80)
            print("\nYou must manually resolve these duplicates before running migration:")
            print("1. Decide which records to keep")
            print("2. Merge or delete duplicate records")
            print("3. Re-run this script")
            return 1

        if args.analyze_only:
            print("\n✅ Analysis complete. No duplicates found.")
            return 0

        # Step 2: Migrate
        migrate_phone_numbers(session, dry_run=args.dry_run)

        if args.dry_run:
            print("\n💡 Run without --dry-run to apply changes")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
