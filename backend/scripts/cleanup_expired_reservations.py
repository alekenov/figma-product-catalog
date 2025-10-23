#!/usr/bin/env python3
"""
Cleanup script for expired order reservations.
This script identifies and removes reservations for orders that have been in certain states
for too long, preventing inventory from being locked indefinitely.
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import select
from models import Order, OrderReservation, OrderStatus


async def cleanup_expired_reservations(dry_run: bool = True, max_age_hours: int = 72):
    """
    Clean up expired reservations based on order age and status.

    Args:
        dry_run: If True, only report what would be cleaned, don't actually delete
        max_age_hours: Age threshold in hours for considering reservations expired
    """

    print(f"🧹 Starting reservation cleanup (dry_run={dry_run})")
    print(f"   Max age: {max_age_hours} hours")
    print("=" * 50)

    engine = create_async_engine("sqlite+aiosqlite:///figma_catalog.db")

    async with AsyncSession(engine) as session:
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Find orders with reservations that meet cleanup criteria
        query = select(Order, OrderReservation).join(
            OrderReservation, Order.id == OrderReservation.order_id
        ).where(
            Order.created_at < cutoff_time
        ).where(
            # Clean up reservations for:
            # 1. NEW orders that haven't been paid (likely abandoned)
            # 2. CANCELLED orders (should have been cleaned already, but failsafe)
            Order.status.in_([OrderStatus.NEW, OrderStatus.CANCELLED])
        )

        result = await session.execute(query)
        orders_with_reservations = result.all()

        if not orders_with_reservations:
            print("✅ No expired reservations found")
            return

        # Group by order for reporting
        orders_to_clean = {}
        total_reservations = 0

        for order, reservation in orders_with_reservations:
            if order.id not in orders_to_clean:
                orders_to_clean[order.id] = {
                    'order': order,
                    'reservations': []
                }
            orders_to_clean[order.id]['reservations'].append(reservation)
            total_reservations += 1

        print(f"🔍 Found {total_reservations} expired reservations in {len(orders_to_clean)} orders:")

        for order_id, data in orders_to_clean.items():
            order = data['order']
            reservations = data['reservations']
            age_hours = (datetime.now() - order.created_at).total_seconds() / 3600

            print(f"\n   📦 Order #{order.orderNumber} (ID: {order_id})")
            print(f"      Status: {order.status}")
            print(f"      Age: {age_hours:.1f} hours")
            print(f"      Customer: {order.customerName}")
            print(f"      Reservations: {len(reservations)}")

            for reservation in reservations:
                print(f"         - {reservation.reserved_quantity} units of item #{reservation.warehouse_item_id}")

        if not dry_run:
            print(f"\n🗑️  Cleaning up {total_reservations} reservations...")

            deleted_count = 0
            for order_id, data in orders_to_clean.items():
                for reservation in data['reservations']:
                    await session.delete(reservation)
                    deleted_count += 1

            await session.commit()
            print(f"✅ Successfully deleted {deleted_count} expired reservations")

            # Log the cleanup action
            print(f"\n📝 Cleanup summary:")
            print(f"   - Orders processed: {len(orders_to_clean)}")
            print(f"   - Reservations deleted: {deleted_count}")
            print(f"   - Cutoff time: {cutoff_time}")

        else:
            print(f"\n💡 This was a dry run. Use dry_run=False to actually delete reservations")


async def get_reservation_statistics():
    """Get current reservation statistics"""

    print("📊 Current Reservation Statistics")
    print("=" * 50)

    engine = create_async_engine("sqlite+aiosqlite:///figma_catalog.db")

    async with AsyncSession(engine) as session:
        # Total reservations
        total_query = select(OrderReservation)
        total_result = await session.execute(total_query)
        total_reservations = len(total_result.all())

        print(f"Total reservations: {total_reservations}")

        if total_reservations == 0:
            print("No reservations found.")
            return

        # Reservations by order status
        status_query = select(Order.status, OrderReservation.id).join(
            OrderReservation, Order.id == OrderReservation.order_id
        )
        status_result = await session.execute(status_query)

        status_counts = {}
        for status, _ in status_result.all():
            status_counts[status] = status_counts.get(status, 0) + 1

        print("\nReservations by order status:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")

        # Age distribution
        age_query = select(OrderReservation.created_at)
        age_result = await session.execute(age_query)

        now = datetime.now()
        age_buckets = {
            "< 1 hour": 0,
            "1-24 hours": 0,
            "1-7 days": 0,
            "> 7 days": 0
        }

        for (created_at,) in age_result.all():
            age_hours = (now - created_at).total_seconds() / 3600

            if age_hours < 1:
                age_buckets["< 1 hour"] += 1
            elif age_hours < 24:
                age_buckets["1-24 hours"] += 1
            elif age_hours < 168:  # 7 days
                age_buckets["1-7 days"] += 1
            else:
                age_buckets["> 7 days"] += 1

        print("\nReservations by age:")
        for bucket, count in age_buckets.items():
            print(f"   {bucket}: {count}")


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    dry_run = True
    max_age_hours = 72

    if len(sys.argv) > 1:
        if "--execute" in sys.argv:
            dry_run = False
        if "--hours" in sys.argv:
            try:
                hours_index = sys.argv.index("--hours") + 1
                max_age_hours = int(sys.argv[hours_index])
            except (IndexError, ValueError):
                print("Error: --hours requires a numeric value")
                sys.exit(1)
        if "--help" in sys.argv or "-h" in sys.argv:
            print("Usage: python3 cleanup_expired_reservations.py [options]")
            print("")
            print("Options:")
            print("  --execute          Actually delete reservations (default is dry-run)")
            print("  --hours N          Set max age threshold to N hours (default: 72)")
            print("  --stats-only       Only show statistics, don't run cleanup")
            print("  --help, -h         Show this help message")
            sys.exit(0)
        if "--stats-only" in sys.argv:
            asyncio.run(get_reservation_statistics())
            sys.exit(0)

    # Show usage info for dry runs
    if dry_run:
        print("🚨 DRY RUN MODE - No changes will be made")
        print("   Use --execute to actually delete expired reservations")
        print("   Use --stats-only to only view current statistics")
        print("   Use --help for more options\n")

    # Run statistics first
    asyncio.run(get_reservation_statistics())
    print()

    # Then run cleanup
    asyncio.run(cleanup_expired_reservations(dry_run=dry_run, max_age_hours=max_age_hours))