"""
Direct refund for Payment #00031 (12691387534) - 90 tenge
Skips /details endpoint since it returns 404
"""
import asyncio
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError


async def refund_payment():
    """Perform refund on Payment #00031"""
    kaspi_service = get_kaspi_service()

    external_id = "12691387534"  # Payment #00031
    amount = 90.0  # 9000 kopecks = 90 tenge

    print("=" * 60)
    print(f"Refunding Payment #00031")
    print(f"Payment ID: {external_id}")
    print(f"Amount: {amount} ₸")
    print("=" * 60)

    # Step 1: Verify payment is Processed
    try:
        print("\n🔍 Checking payment status...")
        status_response = await kaspi_service.check_status(external_id)
        status_data = status_response.get("data", {})
        payment_status = status_data.get("status")

        print(f"   Status: {payment_status}")

        if payment_status != "Processed":
            print(f"\n⚠️  Cannot refund: Payment status is {payment_status}")
            print("   Only Processed payments can be refunded")
            return False

    except KaspiPayServiceError as e:
        print(f"\n❌ Status check failed: {str(e)}")
        return False

    # Step 2: Perform refund (skip /details check since it returns 404)
    try:
        print("\n💰 Processing refund...")
        print(f"   Amount: {amount} ₸")

        refund_response = await kaspi_service.refund(
            external_id=external_id,
            amount=amount
        )

        print("\n✅ Refund successful!")
        print(f"   Response: {refund_response}")

        # Step 3: Verify with status check
        print("\n🔄 Verifying refund...")
        await asyncio.sleep(2)  # Wait for API to process

        verify_status = await kaspi_service.check_status(external_id)
        print(f"   Updated status: {verify_status.get('data', {})}")

        return True

    except KaspiPayServiceError as e:
        print(f"\n❌ Refund failed: {str(e)}")
        return False


async def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("Kaspi Pay Refund - Payment #00031")
    print("=" * 60 + "\n")

    success = await refund_payment()

    print("\n" + "=" * 60)
    if success:
        print("✅ REFUND COMPLETED")
        print("\nThe 90 ₸ has been refunded successfully!")
    else:
        print("⚠️  REFUND FAILED")
        print("\nCheck the error messages above for details")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
