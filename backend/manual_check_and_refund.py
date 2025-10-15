"""
Manually check Kaspi payment status and perform refund if paid
"""
import asyncio
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError


async def check_and_refund(external_id: str, amount: float):
    """Check payment status and refund if Processed"""
    kaspi_service = get_kaspi_service()

    print("=" * 60)
    print(f"Checking Kaspi Payment: {external_id}")
    print("=" * 60)

    # Step 1: Check status
    try:
        print("\n🔍 Checking payment status...")
        status_response = await kaspi_service.check_status(external_id)

        status_data = status_response.get("data", {})
        payment_status = status_data.get("status")

        print(f"   Status: {payment_status}")

        if payment_status != "Processed":
            print(f"\n⚠️  Payment not processed yet. Current status: {payment_status}")
            print("   Cannot refund unpaid payment")
            return False

    except KaspiPayServiceError as e:
        print(f"\n❌ Failed to check status: {str(e)}")
        return False

    # Step 2: Get payment details
    try:
        print("\n📊 Getting payment details...")
        details_response = await kaspi_service.get_details(external_id)

        details_data = details_response.get("data", {})
        total_amount = details_data.get("TotalAmount", 0)
        available_return = details_data.get("AvailableReturnAmount", 0)

        print(f"   Total Amount: {total_amount} ₸")
        print(f"   Available for Refund: {available_return} ₸")

        if available_return == 0:
            print("\n⚠️  Already fully refunded")
            return False

    except KaspiPayServiceError as e:
        print(f"\n❌ Failed to get details: {str(e)}")
        return False

    # Step 3: Confirm refund
    print(f"\n💰 Refund amount: {amount} ₸")
    print(f"   (You will receive this back)")

    confirm = input("\nProceed with refund? (yes/no): ")

    if confirm.lower() != "yes":
        print("\n❌ Refund cancelled")
        return False

    # Step 4: Perform refund
    try:
        print("\n🔄 Processing refund...")
        refund_response = await kaspi_service.refund(
            external_id=external_id,
            amount=amount
        )

        print("✅ Refund successful!")
        print(f"   Response: {refund_response}")

        # Verify refund
        await asyncio.sleep(2)

        verify_response = await kaspi_service.get_details(external_id)
        verify_data = verify_response.get("data", {})
        remaining = verify_data.get("AvailableReturnAmount", 0)

        print(f"\n✅ Verification: {remaining} ₸ remaining for refund")

        if remaining == 0:
            print("   ✅ Full refund confirmed!")

        return True

    except KaspiPayServiceError as e:
        print(f"\n❌ Refund failed: {str(e)}")
        return False


async def main():
    """Main flow"""
    # Use the most recent payment ID from your list
    payment_id = "12691399451"  # Order #00032
    amount = 90.0  # 9000 kopecks = 90 tenge

    print("\n" + "=" * 60)
    print("Manual Kaspi Payment Check & Refund")
    print("=" * 60 + "\n")

    success = await check_and_refund(payment_id, amount)

    print("\n" + "=" * 60)
    if success:
        print("✅ REFUND COMPLETED")
        print("\nПОЛЛИНГ: Статус узнан через POLLING (manual check)")
        print("         Обычно polling service проверяет каждые 2 минуты")
    else:
        print("⚠️  REFUND NOT COMPLETED")
        print("\nПОЛЛИНГ: Платеж в статусе Wait - ещё не оплачен")
        print("         Нужно оплатить через Kaspi QR, потом polling")
        print("         service автоматически обновит статус через 2 мин")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
