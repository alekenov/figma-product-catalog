"""
Utility functions for the flower shop backend
"""
import re
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to Kazakhstan format (+7XXXXXXXXXX).

    Accepts various input formats:
    - +77015211545
    - 77015211545
    - 87015211545  (converts 8 to 7)
    - 7015211545   (adds +7 prefix)
    - +7 701 521 15 45 (removes spaces)

    Args:
        phone: Phone number in any Kazakhstan format

    Returns:
        Normalized phone number in format +7XXXXXXXXXX

    Raises:
        ValueError: If phone number format is invalid
    """
    if not phone:
        raise ValueError("Phone number cannot be empty")

    # Remove all non-digit characters except leading +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Remove + if present for easier processing
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]

    # Convert 8 prefix to 7 (Kazakhstan legacy format)
    if cleaned.startswith('8'):
        cleaned = '7' + cleaned[1:]

    # Add 7 prefix if missing (10-digit number)
    if len(cleaned) == 10:
        cleaned = '7' + cleaned

    # Validate format: should be 11 digits starting with 7
    if not re.match(r'^7\d{10}$', cleaned):
        raise ValueError(
            f"Invalid Kazakhstan phone number format: {phone}. "
            "Expected format: +7XXXXXXXXXX (11 digits total, starting with 7)"
        )

    return '+' + cleaned


def validate_phone_number(phone: str) -> bool:
    """
    Validate Kazakhstan phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        normalize_phone_number(phone)
        return True
    except ValueError:
        return False


def tenge_to_kopecks(tenge_amount: int) -> int:
    """
    Convert tenge to kopecks

    Args:
        tenge_amount: Amount in tenge (integer)

    Returns:
        Amount in kopecks (tenge * 100)
    """
    return tenge_amount * 100


def kopecks_to_tenge(kopeck_amount: int) -> int:
    """
    Convert kopecks to tenge (rounded down)

    Args:
        kopeck_amount: Amount in kopecks (integer)

    Returns:
        Amount in tenge (kopecks // 100)
    """
    return kopeck_amount // 100


def format_price_tenge(kopeck_amount: int) -> str:
    """
    Format kopeck amount as tenge string

    Args:
        kopeck_amount: Amount in kopecks

    Returns:
        Formatted string like "250₸"
    """
    tenge = kopecks_to_tenge(kopeck_amount)
    return f"{tenge}₸"


def validate_tenge_amount(amount: int) -> bool:
    """
    Validate that a tenge amount is reasonable

    Args:
        amount: Amount in tenge

    Returns:
        True if valid, False otherwise
    """
    return 0 <= amount <= 10_000_000  # Max 10M tenge seems reasonable


def validate_kopeck_amount(amount: int) -> bool:
    """
    Validate that a kopeck amount is reasonable

    Args:
        amount: Amount in kopecks

    Returns:
        True if valid, False otherwise
    """
    return 0 <= amount <= 1_000_000_000  # Max 10M tenge in kopecks