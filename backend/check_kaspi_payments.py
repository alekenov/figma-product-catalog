"""
Check all Kaspi payments in database
"""
import asyncio
from sqlalchemy import select
from database import get_session
from models.orders import Order


async def main():
    """List all Kaspi payments"""
    async for session in get_session():
        query = (
            select(Order)
            .where(Order.payment_method == "kaspi")
            .order_by(Order.created_at.desc())
            .limit(10)
        )

        result = await session.execute(query)
        orders = result.scalars().all()

        if not orders:
            print("❌ No Kaspi payments found in database")
            return

        print("=" * 80)
        print(f"Found {len(orders)} Kaspi payment(s):")
        print("=" * 80)

        for order in orders:
            print(f"\nOrder #{order.orderNumber} (ID: {order.id})")
            print(f"  Customer: {order.customerName} ({order.phone})")
            print(f"  Amount: {order.total / 100:.2f} ₸")
            print(f"  Created: {order.created_at}")
            print(f"  Order Status: {order.status}")
            print(f"  Kaspi Payment ID: {order.kaspi_payment_id or 'NOT CREATED'}")
            print(f"  Kaspi Status: {order.kaspi_payment_status or 'N/A'}")
            if order.kaspi_payment_created_at:
                print(f"  Payment Created At: {order.kaspi_payment_created_at}")
            if order.kaspi_payment_completed_at:
                print(f"  Payment Completed At: {order.kaspi_payment_completed_at}")
            print("-" * 80)

        break


if __name__ == "__main__":
    asyncio.run(main())
