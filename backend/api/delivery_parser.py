"""
Natural language delivery date/time parser for backend API.

Migrated from MCP server to centralize parsing logic.
Supports Russian and English natural language expressions.
"""
from datetime import datetime, timedelta, date, time
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedDelivery:
    """Result of parsing delivery date/time from natural language."""

    date: date
    time: str  # HH:MM format
    iso_datetime: str  # ISO 8601 format
    original_date: str
    original_time: str


class DeliveryParser:
    """
    Parses natural language delivery dates and times.

    Supports Russian and English natural language:
    - Dates: "сегодня", "завтра", "послезавтра", "через N дней", YYYY-MM-DD
    - Times: "утром", "днем", "вечером", "как можно скорее", HH:MM
    """

    # Natural language mappings
    DATE_KEYWORDS = {
        "today": ("сегодня", "today"),
        "tomorrow": ("завтра", "tomorrow"),
        "day_after": ("послезавтра", "day after tomorrow"),
    }

    TIME_KEYWORDS = {
        "morning": ("утром", "утро", "morning"),  # → 10:00
        "afternoon": ("днем", "день", "afternoon"),  # → 14:00
        "evening": ("вечером", "вечер", "evening"),  # → 18:00
        "asap": ("как можно скорее", "asap", "скорее", "срочно"),  # → nearest
        "manager_will_clarify": (  # → 14:00 (default fallback)
            "уточнит менеджер",
            "менеджер уточнит",
            "позвоните и уточните",
            "позвонит и уточнит",
            "сам уточнит",
            "сам спросит",
            "manager will call",
            "call and clarify",
        ),
    }

    @classmethod
    def parse_date(cls, date_str: str) -> date:
        """
        Parse natural language date to Python date object.

        Args:
            date_str: Natural language date or YYYY-MM-DD format

        Returns:
            Python date object

        Examples:
            >>> parse_date("сегодня")
            date(2025, 1, 15)
            >>> parse_date("завтра")
            date(2025, 1, 16)
            >>> parse_date("через 3 дня")
            date(2025, 1, 18)
        """
        today = datetime.now().date()
        date_lower = date_str.lower().strip()

        # Today
        if date_lower in cls.DATE_KEYWORDS["today"]:
            return today

        # Tomorrow
        if date_lower in cls.DATE_KEYWORDS["tomorrow"]:
            return today + timedelta(days=1)

        # Day after tomorrow
        if date_lower in cls.DATE_KEYWORDS["day_after"]:
            return today + timedelta(days=2)

        # "через N дней" (in N days)
        if date_lower.startswith("через "):
            try:
                parts = date_lower.split()
                days = int(parts[1])
                return today + timedelta(days=days)
            except (IndexError, ValueError):
                logger.warning(f"Could not parse 'через' format: {date_str}")
                return today

        # YYYY-MM-DD format
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
            return parsed
        except ValueError:
            logger.warning(f"Could not parse date: {date_str}, defaulting to today")
            return today

    @classmethod
    def parse_time(cls, time_str: str) -> str:
        """
        Parse natural language time to HH:MM format.

        Args:
            time_str: Natural language time or HH:MM format

        Returns:
            Time in HH:MM format

        Examples:
            >>> parse_time("утром")
            "10:00"
            >>> parse_time("днем")
            "14:00"
            >>> parse_time("как можно скорее")
            "16:00"  # (depends on current hour)
        """
        time_lower = time_str.lower().strip()

        # Morning
        if time_lower in cls.TIME_KEYWORDS["morning"]:
            return "10:00"

        # Afternoon
        if time_lower in cls.TIME_KEYWORDS["afternoon"]:
            return "14:00"

        # Evening
        if time_lower in cls.TIME_KEYWORDS["evening"]:
            return "18:00"

        # ASAP - calculate nearest available slot
        if time_lower in cls.TIME_KEYWORDS["asap"]:
            current_hour = datetime.now().hour
            if current_hour < 12:
                return "12:00"
            elif current_hour < 16:
                return "16:00"
            else:
                return "18:00"

        # Manager will clarify - default to afternoon
        if time_lower in cls.TIME_KEYWORDS["manager_will_clarify"]:
            logger.info(f"🕐 Manager will clarify time: '{time_str}' → defaulting to afternoon (14:00)")
            return "14:00"

        # Assume HH:MM format already
        return time_str

    @classmethod
    def to_iso_datetime(cls, parsed_date: date, parsed_time: str) -> str:
        """
        Combine parsed date and time into ISO 8601 datetime string.

        Args:
            parsed_date: Python date object
            parsed_time: Time in HH:MM format

        Returns:
            ISO 8601 datetime string (e.g., "2025-01-15T14:00:00")
        """
        return f"{parsed_date.strftime('%Y-%m-%d')}T{parsed_time}:00"

    @classmethod
    def parse(cls, date_str: str, time_str: str) -> ParsedDelivery:
        """
        Parse natural language date and time into structured format.

        Args:
            date_str: Natural language date or YYYY-MM-DD
            time_str: Natural language time or HH:MM

        Returns:
            ParsedDelivery with all fields populated

        Example:
            >>> parser = DeliveryParser()
            >>> result = parser.parse("завтра", "днем")
            >>> result.iso_datetime
            "2025-01-16T14:00:00"
        """
        parsed_date = cls.parse_date(date_str)
        parsed_time = cls.parse_time(time_str)
        iso_datetime = cls.to_iso_datetime(parsed_date, parsed_time)

        logger.debug(
            f"📅 Parsed '{date_str}' '{time_str}' → {iso_datetime}"
        )

        return ParsedDelivery(
            date=parsed_date,
            time=parsed_time,
            iso_datetime=iso_datetime,
            original_date=date_str,
            original_time=time_str,
        )
