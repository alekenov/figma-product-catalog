#!/usr/bin/env python3
"""
Test Kaspi Pay Refund Workflow
Tests the complete refund process for paid order #00091
"""
import requests
import json

BASE_URL = "http://localhost:8014/api/v1"
PAYMENT_ID = "12704653807"  # Order #00091 - оплачен на 9 tenge

print("💳 Testing Kaspi Pay Refund Workflow\n")
print(f"Payment ID: {PAYMENT_ID}")
print(f"Order: #00091 (9 tenge paid)\n")

# Step 1: Check payment details
print("=" * 60)
print("STEP 1: Checking payment details")
print("=" * 60)

details_response = requests.get(f"{BASE_URL}/kaspi/details/{PAYMENT_ID}")

print(f"\nStatus Code: {details_response.status_code}")

if details_response.status_code == 200:
    details = details_response.json()
    print(f"\n✅ Payment Details:")
    print(json.dumps(details, indent=2, ensure_ascii=False))

    # Extract data
    data = details.get("data", {})
    total_amount = data.get("TotalAmount", 0)
    available_return = data.get("AvailableReturnAmount", 0)

    print(f"\n📊 Summary:")
    print(f"   Total Amount: {total_amount} tenge")
    print(f"   Available Return: {available_return} tenge")

    # Step 2: Execute partial refund (4.5 tenge)
    if available_return >= 4.5:
        print("\n" + "=" * 60)
        print("STEP 2: Executing partial refund (4.5 tenge)")
        print("=" * 60)

        refund_response = requests.post(
            f"{BASE_URL}/kaspi/refund",
            json={"external_id": PAYMENT_ID, "amount": 4.5}
        )

        print(f"\nStatus Code: {refund_response.status_code}")

        if refund_response.status_code == 200:
            refund_result = refund_response.json()
            print(f"\n✅ Refund Successful!")
            print(json.dumps(refund_result, indent=2, ensure_ascii=False))

            # Step 3: Verify updated available amount
            print("\n" + "=" * 60)
            print("STEP 3: Verifying updated available amount")
            print("=" * 60)

            verify_response = requests.get(f"{BASE_URL}/kaspi/details/{PAYMENT_ID}")

            if verify_response.status_code == 200:
                updated_details = verify_response.json()
                updated_data = updated_details.get("data", {})
                new_available = updated_data.get("AvailableReturnAmount", 0)

                print(f"\n📊 Verification Results:")
                print(f"   Previous Available: {available_return} tenge")
                print(f"   Refunded Amount: 4.5 tenge")
                print(f"   New Available: {new_available} tenge")
                print(f"   Expected: {available_return - 4.5} tenge")

                if abs(new_available - (available_return - 4.5)) < 0.01:
                    print(f"\n✅ SUCCESS! Amount matches expected value!")
                else:
                    print(f"\n⚠️  WARNING: Amount mismatch!")
                    print(f"      Expected: {available_return - 4.5}")
                    print(f"      Got: {new_available}")
            else:
                print(f"\n❌ Failed to verify: {verify_response.status_code}")
                print(f"Response: {verify_response.text[:300]}")
        else:
            print(f"\n❌ Refund Failed!")
            print(f"Response: {refund_response.text}")
    else:
        print(f"\n⚠️  Cannot refund: Available amount ({available_return}) < 4.5 tenge")
else:
    print(f"\n❌ Failed to get payment details")
    print(f"Response: {details_response.text[:500]}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
