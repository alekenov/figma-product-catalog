"""
Unit tests for DeliveryParser.
Tests natural language date/time parsing logic.
"""
import pytest
from datetime import datetime, timedelta, date

from api.delivery_parser import DeliveryParser, ParsedDelivery


class TestDeliveryParser:
    """Test suite for DeliveryParser natural language parsing."""

    def test_parse_date_today(self):
        """Test parsing 'сегодня' and 'today'."""
        today = date.today()

        assert DeliveryParser.parse_date("сегодня") == today
        assert DeliveryParser.parse_date("today") == today
        assert DeliveryParser.parse_date("Today") == today  # Case insensitive

    def test_parse_date_tomorrow(self):
        """Test parsing 'завтра' and 'tomorrow'."""
        tomorrow = date.today() + timedelta(days=1)

        assert DeliveryParser.parse_date("завтра") == tomorrow
        assert DeliveryParser.parse_date("tomorrow") == tomorrow
        assert DeliveryParser.parse_date("ЗАВТРА") == tomorrow  # Case insensitive

    def test_parse_date_day_after_tomorrow(self):
        """Test parsing 'послезавтра' and 'day after tomorrow'."""
        day_after = date.today() + timedelta(days=2)

        assert DeliveryParser.parse_date("послезавтра") == day_after
        assert DeliveryParser.parse_date("day after tomorrow") == day_after

    def test_parse_date_through_n_days(self):
        """Test parsing 'через N дней' format."""
        today = date.today()

        assert DeliveryParser.parse_date("через 1 дней") == today + timedelta(days=1)
        assert DeliveryParser.parse_date("через 3 дня") == today + timedelta(days=3)
        assert DeliveryParser.parse_date("через 7 дней") == today + timedelta(days=7)

    def test_parse_date_iso_format(self):
        """Test parsing YYYY-MM-DD format."""
        assert DeliveryParser.parse_date("2025-01-15") == date(2025, 1, 15)
        assert DeliveryParser.parse_date("2025-12-31") == date(2025, 12, 31)

    def test_parse_date_invalid_fallback(self):
        """Test that invalid dates fall back to today."""
        today = date.today()

        assert DeliveryParser.parse_date("invalid") == today
        assert DeliveryParser.parse_date("через много дней") == today
        assert DeliveryParser.parse_date("2025-13-45") == today  # Invalid date

    def test_parse_time_morning(self):
        """Test parsing morning times."""
        assert DeliveryParser.parse_time("утром") == "10:00"
        assert DeliveryParser.parse_time("утро") == "10:00"
        assert DeliveryParser.parse_time("morning") == "10:00"
        assert DeliveryParser.parse_time("УТРОМ") == "10:00"  # Case insensitive

    def test_parse_time_afternoon(self):
        """Test parsing afternoon times."""
        assert DeliveryParser.parse_time("днем") == "14:00"
        assert DeliveryParser.parse_time("день") == "14:00"
        assert DeliveryParser.parse_time("afternoon") == "14:00"

    def test_parse_time_evening(self):
        """Test parsing evening times."""
        assert DeliveryParser.parse_time("вечером") == "18:00"
        assert DeliveryParser.parse_time("вечер") == "18:00"
        assert DeliveryParser.parse_time("evening") == "18:00"

    def test_parse_time_asap(self):
        """Test parsing ASAP times (depends on current hour)."""
        result = DeliveryParser.parse_time("как можно скорее")
        assert result in ["12:00", "16:00", "18:00"]

        result = DeliveryParser.parse_time("asap")
        assert result in ["12:00", "16:00", "18:00"]

        result = DeliveryParser.parse_time("срочно")
        assert result in ["12:00", "16:00", "18:00"]

    def test_parse_time_hh_mm_format(self):
        """Test that HH:MM format is passed through unchanged."""
        assert DeliveryParser.parse_time("14:30") == "14:30"
        assert DeliveryParser.parse_time("09:15") == "09:15"
        assert DeliveryParser.parse_time("21:45") == "21:45"

    def test_to_iso_datetime(self):
        """Test ISO datetime formatting."""
        test_date = date(2025, 1, 15)
        test_time = "14:30"

        result = DeliveryParser.to_iso_datetime(test_date, test_time)
        assert result == "2025-01-15T14:30:00"

    def test_parse_combined(self):
        """Test full parsing with date and time."""
        result = DeliveryParser.parse("завтра", "днем")

        expected_date = date.today() + timedelta(days=1)
        expected_iso = f"{expected_date.strftime('%Y-%m-%d')}T14:00:00"

        assert result.date == expected_date
        assert result.time == "14:00"
        assert result.iso_datetime == expected_iso
        assert result.original_date == "завтра"
        assert result.original_time == "днем"

    def test_parse_combined_russian(self):
        """Test combined parsing with Russian natural language."""
        result = DeliveryParser.parse("послезавтра", "вечером")

        expected_date = date.today() + timedelta(days=2)
        expected_iso = f"{expected_date.strftime('%Y-%m-%d')}T18:00:00"

        assert result.date == expected_date
        assert result.time == "18:00"
        assert result.iso_datetime == expected_iso

    def test_parse_combined_english(self):
        """Test combined parsing with English natural language."""
        result = DeliveryParser.parse("tomorrow", "morning")

        expected_date = date.today() + timedelta(days=1)
        expected_iso = f"{expected_date.strftime('%Y-%m-%d')}T10:00:00"

        assert result.date == expected_date
        assert result.time == "10:00"
        assert result.iso_datetime == expected_iso

    def test_parse_combined_mixed_formats(self):
        """Test parsing with ISO date and natural time."""
        result = DeliveryParser.parse("2025-03-15", "утром")

        assert result.date == date(2025, 3, 15)
        assert result.time == "10:00"
        assert result.iso_datetime == "2025-03-15T10:00:00"

    def test_parse_combined_iso_formats(self):
        """Test parsing with ISO date and HH:MM time."""
        result = DeliveryParser.parse("2025-06-20", "16:45")

        assert result.date == date(2025, 6, 20)
        assert result.time == "16:45"
        assert result.iso_datetime == "2025-06-20T16:45:00"

    def test_parse_edge_case_through_zero_days(self):
        """Test edge case 'через 0 дней' (should be today)."""
        today = date.today()
        # Note: Currently "через 0 дней" would fail int() parsing
        # This documents current behavior
        result = DeliveryParser.parse_date("через 0 дней")
        # Falls back to today on parse error
        assert result == today

    def test_parse_type_validation(self):
        """Test that ParsedDelivery has correct types."""
        result = DeliveryParser.parse("завтра", "днем")

        assert isinstance(result, ParsedDelivery)
        assert isinstance(result.date, date)
        assert isinstance(result.time, str)
        assert isinstance(result.iso_datetime, str)
        assert isinstance(result.original_date, str)
        assert isinstance(result.original_time, str)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
