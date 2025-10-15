"""
Test Kaspi Pay refund functionality

This script:
1. Finds the latest Processed payment
2. Performs a full refund via Kaspi API
3. Verifies the refund was successful
"""
import asyncio
import sys
from sqlalchemy import select
from database import get_session
from models.orders import Order
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError


async def find_latest_processed_payment():
    """Find the most recent processed Kaspi payment"""
    async for session in get_session():
        query = (
            select(Order)
            .where(
                Order.payment_method == "kaspi",
                Order.kaspi_payment_status == "Processed",
                Order.kaspi_payment_id.isnot(None)
            )
            .order_by(Order.created_at.desc())
            .limit(1)
        )

        result = await session.execute(query)
        order = result.scalar_one_or_none()

        if order:
            print("=" * 60)
            print("Found processed payment:")
            print("=" * 60)
            print(f"Order ID: {order.id}")
            print(f"Order Number: {order.orderNumber}")
            print(f"Customer: {order.customer_name}")
            print(f"Phone: {order.phone}")
            print(f"Amount: {order.total / 100:.2f} ₸")
            print(f"Kaspi Payment ID: {order.kaspi_payment_id}")
            print(f"Payment Status: {order.kaspi_payment_status}")
            print(f"Order Status: {order.status}")
            print("=" * 60)
            return order
        else:
            print("❌ No processed Kaspi payments found")
            return None


async def perform_refund(order: Order):
    """Perform full refund for the order"""
    kaspi_service = get_kaspi_service()

    amount_tenge = order.total / 100  # Convert kopecks to tenge

    print(f"\n🔄 Initiating refund...")
    print(f"   External ID: {order.kaspi_payment_id}")
    print(f"   Amount: {amount_tenge} ₸")

    try:
        # Perform refund
        response = await kaspi_service.refund(
            external_id=order.kaspi_payment_id,
            amount=amount_tenge
        )

        print("\n✅ Refund successful!")
        print(f"   Response: {response}")

        # Update order status (optional - you might want to add a refunded status)
        async for session in get_session():
            result = await session.execute(
                select(Order).where(Order.id == order.id)
            )
            db_order = result.scalar_one()

            # Add note about refund
            if db_order.notes:
                db_order.notes += f"\n[REFUND] {amount_tenge} ₸ возвращено {asyncio.get_event_loop().time()}"
            else:
                db_order.notes = f"[REFUND] {amount_tenge} ₸ возвращено"

            await session.commit()
            print(f"   Order updated with refund note")
            break

        return True

    except KaspiPayServiceError as e:
        print(f"\n❌ Refund failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False


async def verify_refund(order: Order):
    """Verify refund by checking payment details"""
    kaspi_service = get_kaspi_service()

    print(f"\n🔍 Verifying refund...")

    try:
        # Get payment details to check AvailableReturnAmount
        response = await kaspi_service.get_details(order.kaspi_payment_id)

        data = response.get("data", {})
        total_amount = data.get("TotalAmount", 0)
        available_return = data.get("AvailableReturnAmount", 0)

        print(f"   Total Amount: {total_amount} ₸")
        print(f"   Available Return: {available_return} ₸")

        if available_return == 0:
            print("   ✅ Full refund confirmed (AvailableReturnAmount = 0)")
            return True
        else:
            print(f"   ⚠️ Partial refund or pending ({available_return} ₸ still available)")
            return False

    except Exception as e:
        print(f"   ❌ Verification failed: {str(e)}")
        return False


async def main():
    """Main test flow"""
    print("\n" + "=" * 60)
    print("Kaspi Pay Refund Test")
    print("=" * 60 + "\n")

    # Step 1: Find payment
    order = await find_latest_processed_payment()
    if not order:
        sys.exit(1)

    # Step 2: Confirm refund
    print("\n⚠️  WARNING: This will refund the payment!")
    confirm = input("Proceed with refund? (yes/no): ")

    if confirm.lower() != "yes":
        print("\n❌ Refund cancelled")
        sys.exit(0)

    # Step 3: Perform refund
    success = await perform_refund(order)

    if not success:
        sys.exit(1)

    # Step 4: Verify refund
    await asyncio.sleep(2)  # Wait a bit for Kaspi to process
    verified = await verify_refund(order)

    # Summary
    print("\n" + "=" * 60)
    if verified:
        print("✅ TEST PASSED: Refund completed and verified")
    else:
        print("⚠️  TEST INCOMPLETE: Refund may need verification")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
