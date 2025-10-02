"""
Product Validations - Input validation and normalization

Provides validation helpers and input normalization functions.
"""

from typing import Dict, Any, List, Optional


def normalize_product_input(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize product input data before processing.

    Args:
        product_data: Raw product data dictionary

    Returns:
        Normalized product data dictionary
    """
    # Ensure enabled field has a default
    if 'enabled' not in product_data:
        product_data['enabled'] = True

    # Ensure is_featured has a default
    if 'is_featured' not in product_data:
        product_data['is_featured'] = False

    # Normalize empty lists
    for field in ['tags', 'cities', 'colors', 'occasions']:
        if field in product_data and product_data[field] is None:
            product_data[field] = []

    return product_data


def validate_recipe_data(recipes: List[Dict[str, Any]]) -> List[str]:
    """
    Validate recipe/composition data for a product.

    Args:
        recipes: List of recipe dictionaries

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not recipes:
        return errors

    for idx, recipe in enumerate(recipes):
        # Check required fields
        if 'warehouse_item_id' not in recipe:
            errors.append(f"Recipe {idx + 1}: missing warehouse_item_id")

        if 'quantity' not in recipe:
            errors.append(f"Recipe {idx + 1}: missing quantity")
        elif recipe['quantity'] <= 0:
            errors.append(f"Recipe {idx + 1}: quantity must be positive")

    return errors


def validate_price(price: Optional[int]) -> Optional[str]:
    """
    Validate product price.

    Args:
        price: Price in kopecks

    Returns:
        Error message if invalid, None if valid
    """
    if price is None:
        return None

    if price < 0:
        return "Price cannot be negative"

    if price == 0:
        return "Price cannot be zero"

    return None


def parse_tag_list(tags_str: Optional[str]) -> List[str]:
    """
    Parse comma-separated tags string into list.

    Args:
        tags_str: Comma-separated tags string

    Returns:
        List of trimmed tag strings
    """
    if not tags_str:
        return []

    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]
