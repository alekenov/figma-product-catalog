"""
Check status of all pending Kaspi payments
"""
import asyncio
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError


async def check_payment_status(external_id: str, order_number: str):
    """Check single payment status"""
    kaspi_service = get_kaspi_service()

    try:
        print(f"\n{'='*60}")
        print(f"Order {order_number} - Payment ID: {external_id}")
        print(f"{'='*60}")

        # Check status
        status_response = await kaspi_service.check_status(external_id)
        status_data = status_response.get("data", {})
        payment_status = status_data.get("status")

        print(f"Status: {payment_status}")

        # Get details if processed
        if payment_status == "Processed":
            details_response = await kaspi_service.get_details(external_id)
            details_data = details_response.get("data", {})

            total_amount = details_data.get("TotalAmount", 0)
            available_return = details_data.get("AvailableReturnAmount", 0)

            print(f"✅ ОПЛАЧЕНО!")
            print(f"   Total Amount: {total_amount} ₸")
            print(f"   Available for Refund: {available_return} ₸")

            return {
                "order_number": order_number,
                "external_id": external_id,
                "status": payment_status,
                "amount": total_amount,
                "can_refund": available_return
            }
        else:
            print(f"⏳ Не оплачено (статус: {payment_status})")
            return None

    except KaspiPayServiceError as e:
        print(f"❌ Error: {str(e)}")
        return None


async def main():
    """Check all payments"""

    payments = [
        ("12691399451", "#00032"),
        ("12691387534", "#00031"),
        ("12691380817", "#00030"),
    ]

    print("\n" + "="*60)
    print("Проверка всех Kaspi платежей")
    print("="*60)

    paid_payments = []

    for external_id, order_num in payments:
        result = await check_payment_status(external_id, order_num)
        if result:
            paid_payments.append(result)

    print("\n" + "="*60)
    print("ИТОГИ:")
    print("="*60)

    if paid_payments:
        print(f"\n✅ Найдено {len(paid_payments)} оплаченных платежей:\n")
        for payment in paid_payments:
            print(f"Order {payment['order_number']}:")
            print(f"  Payment ID: {payment['external_id']}")
            print(f"  Amount: {payment['amount']} ₸")
            print(f"  Available for Refund: {payment['can_refund']} ₸")
            print()
    else:
        print("\n⚠️  Ни один платёж пока не оплачен")

    return paid_payments


if __name__ == "__main__":
    paid = asyncio.run(main())
