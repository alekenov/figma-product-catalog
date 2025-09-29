"""
Utility functions for the flower shop backend
"""

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