#!/usr/bin/env python3
"""
Test phone number validation and normalization.

This script tests the phone validation utility across various input formats.
"""

import sys
from utils import normalize_phone_number, validate_phone_number


def test_phone_normalization():
    """Test phone number normalization with various input formats"""

    test_cases = [
        # (input, expected_output, should_pass)
        ("+77015211545", "+77015211545", True),
        ("77015211545", "+77015211545", True),
        ("87015211545", "+77015211545", True),  # Kazakhstan legacy format
        ("7015211545", "+77015211545", True),   # 10 digits, add +7
        ("+7 701 521 15 45", "+77015211545", True),  # With spaces
        ("8-701-521-15-45", "+77015211545", True),  # With dashes
        ("+7(701)521-15-45", "+77015211545", True),  # Mixed format
        ("", None, False),  # Empty string
        ("123", None, False),  # Too short
        ("+17015211545", None, False),  # Wrong country code
        ("+7701", None, False),  # Too short
    ]

    print("=" * 60)
    print("PHONE NUMBER VALIDATION TESTS")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for input_phone, expected, should_pass in test_cases:
        try:
            result = normalize_phone_number(input_phone)
            if should_pass:
                if result == expected:
                    print(f"✅ PASS: '{input_phone}' → '{result}'")
                    passed += 1
                else:
                    print(f"❌ FAIL: '{input_phone}' → '{result}' (expected '{expected}')")
                    failed += 1
            else:
                print(f"❌ FAIL: '{input_phone}' should have raised ValueError but got '{result}'")
                failed += 1
        except ValueError as e:
            if not should_pass:
                print(f"✅ PASS: '{input_phone}' → ValueError (expected)")
                passed += 1
            else:
                print(f"❌ FAIL: '{input_phone}' → ValueError: {e}")
                failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


def test_pydantic_models():
    """Test phone validation in Pydantic models"""
    from models.users import ClientBase, UserCreate
    from models.orders import OrderCreate
    from models.shop import ShopCreate

    print()
    print("=" * 60)
    print("PYDANTIC MODEL VALIDATION TESTS")
    print("=" * 60)
    print()

    # Test ClientBase normalization
    try:
        client = ClientBase(
            phone="8 701 521 15 45",  # Legacy format with spaces
            customerName="Test Client",
            shop_id=1
        )
        print(f"✅ ClientBase: '{client.phone}' (normalized from '8 701 521 15 45')")
    except Exception as e:
        print(f"❌ ClientBase failed: {e}")

    # Test UserCreate normalization
    try:
        user = UserCreate(
            name="Test User",
            phone="77015211545",  # No + prefix
            password="test123"
        )
        print(f"✅ UserCreate: '{user.phone}' (normalized from '77015211545')")
    except Exception as e:
        print(f"❌ UserCreate failed: {e}")

    # Test OrderCreate normalization
    try:
        order = OrderCreate(
            customerName="Test Customer",
            phone="+7 (701) 521-15-45",  # Mixed format
            recipient_phone="87015211545",  # Legacy format
            sender_phone="7015211545"  # 10 digits
        )
        print(f"✅ OrderCreate:")
        print(f"   - phone: '{order.phone}' (from '+7 (701) 521-15-45')")
        print(f"   - recipient_phone: '{order.recipient_phone}' (from '87015211545')")
        print(f"   - sender_phone: '{order.sender_phone}' (from '7015211545')")
    except Exception as e:
        print(f"❌ OrderCreate failed: {e}")

    # Test ShopCreate normalization
    try:
        shop = ShopCreate(
            name="Test Shop",
            phone="8-701-521-15-45"  # Legacy format with dashes
        )
        print(f"✅ ShopCreate: '{shop.phone}' (normalized from '8-701-521-15-45')")
    except Exception as e:
        print(f"❌ ShopCreate failed: {e}")

    # Test invalid phone number
    print()
    print("Testing invalid phone numbers:")
    try:
        invalid_user = UserCreate(
            name="Invalid User",
            phone="123456",  # Invalid
            password="test123"
        )
        print(f"❌ Should have failed but got: {invalid_user.phone}")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid phone: {e}")

    print()


if __name__ == "__main__":
    # Test utility functions
    success = test_phone_normalization()

    # Test Pydantic models
    test_pydantic_models()

    sys.exit(0 if success else 1)
