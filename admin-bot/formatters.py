"""
Formatters for Telegram bot messages and product displays.
"""
from typing import List, Dict, Any


def format_price(price: int) -> str:
    """
    Format price in kopecks to tenge with proper formatting.

    Args:
        price: Price in kopecks (smallest currency unit)

    Returns:
        Formatted price string like "10 000 ₸"
    """
    price_tenge = int(price) // 100 if isinstance(price, (int, float)) else 0
    return f"{price_tenge:,} ₸".replace(',', ' ')


def extract_product_images(products: List[Dict[str, Any]], max_products: int = 5) -> List[Dict[str, str]]:
    """
    Extract product images with captions for Telegram display.

    Args:
        products: List of product dictionaries from API
        max_products: Maximum number of products to include

    Returns:
        List of dicts with 'url' and 'caption' keys
    """
    images = []

    for product in products[:max_products]:
        # Check images array first, fallback to single image field
        product_images = product.get("images") or []
        image_url = None

        if product_images:
            image_url = product_images[0]["url"]
        elif product.get("image"):
            image_url = product.get("image")

        if image_url:
            price = product.get("price", 0)
            formatted_price = format_price(price)
            caption = f"{product.get('name', 'Товар')} - {formatted_price}"
            images.append({
                "url": image_url,
                "caption": caption
            })

    return images


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.

    Args:
        items: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
