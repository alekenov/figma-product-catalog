"""Authentication utilities."""

from typing import Literal


def validate_token(token: str, expected_token: str) -> bool:
    """
    Validate API token using constant-time comparison to prevent timing attacks.

    Args:
        token: Token to validate
        expected_token: Expected valid token

    Returns:
        True if tokens match, False otherwise

    Example:
        if not validate_token(request_token, CVETY_PRODUCTION_TOKEN):
            raise HTTPException(401, "Invalid token")
    """
    import hmac
    return hmac.compare_digest(token, expected_token)


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to consistent format.

    Converts:
    - +77088888888 -> 77088888888
    - 77088888888 -> 77088888888
    - +7 (708) 888-88-88 -> 77088888888

    Args:
        phone: Phone number in any format

    Returns:
        Normalized phone number (without + prefix, digits only)

    Example:
        normalize_phone("+7 (701) 521-15-45")  # "77015211545"
    """
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')

    # Remove +7 prefix if present
    if cleaned.startswith('+7'):
        cleaned = '7' + cleaned[2:]
    elif cleaned.startswith('+'):
        cleaned = cleaned[1:]

    return cleaned


def extract_shop_id_from_context(context: dict) -> int:
    """
    Extract shop_id from request context (JWT token, headers, etc.).

    Args:
        context: Request context dictionary

    Returns:
        Shop ID

    Raises:
        ValueError: If shop_id not found or invalid
    """
    shop_id = context.get("shop_id")

    if shop_id is None:
        raise ValueError("shop_id not found in context")

    try:
        return int(shop_id)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid shop_id: {shop_id}")
