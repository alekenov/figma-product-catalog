"""
Refund remaining 8910 tenge for Payment #00031 (12691387534)
Total paid: 9000 tenge
Already refunded: 90 tenge
Remaining to refund: 8910 tenge = 891000 tiyns
"""
import asyncio
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError


async def refund_remaining():
    """Refund remaining 8910 tenge"""
    kaspi_service = get_kaspi_service()

    external_id = "12691387534"  # Payment #00031
    amount = 8910.0  # 8910 tenge

    print("=" * 60)
    print(f"Refunding REMAINING amount for Payment #00031")
    print(f"Payment ID: {external_id}")
    print(f"Total paid: 9000 тенге")
    print(f"Already refunded: 90 тенге")
    print(f"Refunding now: {amount} тенге")
    print("=" * 60)

    # Step 1: Verify payment status
    try:
        print("\n🔍 Checking payment status...")
        status_response = await kaspi_service.check_status(external_id)
        status_data = status_response.get("data", {})
        payment_status = status_data.get("status")

        print(f"   Status: {payment_status}")

        if payment_status != "Processed":
            print(f"\n⚠️  Cannot refund: Payment status is {payment_status}")
            return False

    except KaspiPayServiceError as e:
        print(f"\n❌ Status check failed: {str(e)}")
        return False

    # Step 2: Perform refund for remaining amount
    try:
        print(f"\n💰 Processing refund for {amount} тенге...")

        refund_response = await kaspi_service.refund(
            external_id=external_id,
            amount=amount
        )

        print("\n✅ Refund successful!")
        print(f"   Response: {refund_response}")
        print(f"\n   ✅ Full refund completed!")
        print(f"   Total refunded: 90 + 8910 = 9000 тенге")

        # Step 3: Verify
        print("\n🔄 Verifying...")
        await asyncio.sleep(2)

        verify_status = await kaspi_service.check_status(external_id)
        print(f"   Status: {verify_status.get('data', {})}")

        return True

    except KaspiPayServiceError as e:
        print(f"\n❌ Refund failed: {str(e)}")
        return False


async def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("Kaspi Pay - Refund Remaining 8910 тенге")
    print("=" * 60 + "\n")

    success = await refund_remaining()

    print("\n" + "=" * 60)
    if success:
        print("✅ ПОЛНЫЙ ВОЗВРАТ ЗАВЕРШЕН")
        print("\nВсего возвращено: 9000 тенге")
        print("(90 тенге + 8910 тенге)")
    else:
        print("⚠️  ОШИБКА ВОЗВРАТА")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
