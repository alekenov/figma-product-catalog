"""
Tests for phone number normalization and validation.

Ensures consistent phone number handling across the application.
"""

import pytest
from utils import normalize_phone_number, validate_phone_number


class TestPhoneNormalization:
    """Test phone number normalization to +7XXXXXXXXXX format"""

    def test_normalize_phone_with_plus_seven(self):
        """Test normalization of phone starting with +7"""
        assert normalize_phone_number("+77015211545") == "+77015211545"

    def test_normalize_phone_with_seven(self):
        """Test normalization of phone starting with 7"""
        assert normalize_phone_number("77015211545") == "+77015211545"

    def test_normalize_phone_with_eight(self):
        """Test normalization of phone starting with 8 (Kazakhstan legacy format)"""
        assert normalize_phone_number("87015211545") == "+77015211545"

    def test_normalize_phone_ten_digits(self):
        """Test normalization of 10-digit phone (add country code)"""
        assert normalize_phone_number("7015211545") == "+77015211545"

    def test_normalize_phone_with_spaces(self):
        """Test normalization with spaces"""
        assert normalize_phone_number("+7 701 521 15 45") == "+77015211545"

    def test_normalize_phone_with_dashes(self):
        """Test normalization with dashes"""
        assert normalize_phone_number("+7-701-521-15-45") == "+77015211545"

    def test_normalize_phone_with_parentheses(self):
        """Test normalization with parentheses"""
        assert normalize_phone_number("+7 (701) 521-15-45") == "+77015211545"

    def test_normalize_phone_mixed_formatting(self):
        """Test normalization with mixed formatting characters"""
        assert normalize_phone_number("+7 (701) 521 15-45") == "+77015211545"

    def test_normalize_phone_empty_raises_error(self):
        """Test that empty phone raises ValueError"""
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            normalize_phone_number("")

    def test_normalize_phone_invalid_length_raises_error(self):
        """Test that invalid length raises ValueError"""
        with pytest.raises(ValueError, match="Invalid Kazakhstan phone number format"):
            normalize_phone_number("123")

    def test_normalize_phone_invalid_country_code_raises_error(self):
        """Test that non-7 country code raises ValueError"""
        with pytest.raises(ValueError, match="Invalid Kazakhstan phone number format"):
            normalize_phone_number("+19175551234")  # US number

    def test_normalize_phone_non_numeric_raises_error(self):
        """Test that non-numeric input raises ValueError"""
        with pytest.raises(ValueError, match="Invalid Kazakhstan phone number format"):
            normalize_phone_number("not-a-phone")


class TestPhoneValidation:
    """Test phone number validation"""

    def test_validate_valid_phone(self):
        """Test validation of valid phone numbers"""
        assert validate_phone_number("+77015211545") is True
        assert validate_phone_number("77015211545") is True
        assert validate_phone_number("87015211545") is True
        assert validate_phone_number("7015211545") is True

    def test_validate_invalid_phone(self):
        """Test validation of invalid phone numbers"""
        assert validate_phone_number("") is False
        assert validate_phone_number("123") is False
        assert validate_phone_number("+19175551234") is False
        assert validate_phone_number("not-a-phone") is False


class TestPhoneEdgeCases:
    """Test edge cases and special scenarios"""

    def test_normalize_phone_whitespace_only_raises_error(self):
        """Test that whitespace-only input raises ValueError"""
        with pytest.raises(ValueError, match="Invalid Kazakhstan phone number format"):
            normalize_phone_number("   ")

    def test_normalize_phone_handles_eleven_digit_numbers(self):
        """Test handling of 11-digit numbers starting with 7"""
        # 11-digit number starting with 7 is assumed to be correct Kazakhstan format
        assert normalize_phone_number("70152115450") == "+70152115450"

    def test_normalize_phone_handles_unicode_spaces(self):
        """Test handling of unicode spaces and special characters"""
        # Non-breaking space (U+00A0)
        assert normalize_phone_number("+7\u00a0701\u00a0521\u00a015\u00a045") == "+77015211545"


class TestDatabaseCompatibility:
    """Test compatibility with database storage format"""

    def test_normalize_produces_consistent_format(self):
        """Test that multiple formats normalize to same result"""
        formats = [
            "+77015211545",
            "77015211545",
            "87015211545",
            "7015211545",
            "+7 701 521 15 45",
            "+7-701-521-15-45",
            "+7 (701) 521-15-45",
        ]

        normalized = [normalize_phone_number(fmt) for fmt in formats]
        assert len(set(normalized)) == 1, "All formats should normalize to same value"
        assert normalized[0] == "+77015211545"

    def test_normalize_matches_migration_format(self):
        """Test that normalization matches the format used in phone migration script"""
        # Migration script uses normalize_phone_number from utils.py
        # This test ensures consistency
        test_phone = "87776665544"
        expected = "+77776665544"
        assert normalize_phone_number(test_phone) == expected


class TestRealWorldExamples:
    """Test with real-world phone number examples"""

    def test_normalize_common_almaty_numbers(self):
        """Test normalization of common Almaty (701-709) prefixes"""
        assert normalize_phone_number("87012345678") == "+77012345678"
        assert normalize_phone_number("87022345678") == "+77022345678"
        assert normalize_phone_number("87059876543") == "+77059876543"

    def test_normalize_common_astana_numbers(self):
        """Test normalization of common Astana (71X) prefixes"""
        assert normalize_phone_number("87172345678") == "+77172345678"
        assert normalize_phone_number("87012345678") == "+77012345678"

    def test_normalize_mobile_operator_numbers(self):
        """Test normalization of major Kazakhstan mobile operators"""
        # Kcell (7701-7705)
        assert normalize_phone_number("87012345678") == "+77012345678"

        # Beeline (7051)
        assert normalize_phone_number("87051234567") == "+77051234567"

        # Tele2 (7076, 7077)
        assert normalize_phone_number("87076543210") == "+77076543210"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
