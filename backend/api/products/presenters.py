"""
Product Presenters - Response formatting and data transformation

Consolidates response building logic to eliminate duplication.
Handles mapping between backend models and frontend expectations.
"""

from typing import List, Dict, Any, Tuple
from models import (
    Product, ProductType, ProductImage, ProductVariant, ProductAddon,
    ProductRecipe, ProductReview, CompanyReview, PickupLocation,
    ProductDetailRead, ProductBundleItemRead, CompositionItemRead
)


def extract_unique_tags(products: List[Product]) -> List[str]:
    """
    Extract unique tags from a list of products.

    Args:
        products: List of Product instances

    Returns:
        Sorted list of unique tags
    """
    tags = set()
    for product in products:
        if product.tags:
            tags.update(product.tags)
    return sorted(list(tags))


def extract_unique_cities(products: List[Product]) -> List[str]:
    """
    Extract unique cities from a list of products.

    Args:
        products: List of Product instances

    Returns:
        Sorted list of unique cities
    """
    cities = set()
    for product in products:
        if product.cities:
            cities.update(product.cities)
    return sorted(list(cities))


def calculate_price_range(products: List[Product]) -> Dict[str, int]:
    """
    Calculate price range from a list of products.

    Args:
        products: List of Product instances

    Returns:
        Dictionary with min/max prices in kopecks and tenge
    """
    if not products:
        return {
            "min": 0,
            "max": 0,
            "min_tenge": 0,
            "max_tenge": 0
        }

    prices = [p.price for p in products]
    min_price = min(prices)
    max_price = max(prices)

    return {
        "min": min_price,
        "max": max_price,
        "min_tenge": min_price // 100,
        "max_tenge": max_price // 100
    }


def build_home_response(
    featured_products: List[Product],
    available_tags: List[str]
) -> Dict[str, Any]:
    """
    Build response for homepage endpoint.

    Args:
        featured_products: List of featured/filtered products
        available_tags: List of all available tags

    Returns:
        Dictionary with featured products, available tags, and bestsellers
    """
    return {
        "featured": featured_products,
        "available_tags": available_tags,
        "bestsellers": featured_products  # Same as featured for now
    }


def build_filters_response(
    tags: List[str],
    cities: List[str],
    price_range: Dict[str, int]
) -> Dict[str, Any]:
    """
    Build response for filters endpoint.

    Args:
        tags: List of unique tags
        cities: List of unique cities
        price_range: Price range dictionary

    Returns:
        Dictionary with filter options
    """
    return {
        "tags": tags,
        "cities": cities,
        "price_range": price_range,
        "product_types": [t.value for t in ProductType]
    }


def format_composition(recipes: List[ProductRecipe]) -> List[CompositionItemRead]:
    """
    Format product recipes into composition items.

    Args:
        recipes: List of ProductRecipe instances with warehouse items loaded

    Returns:
        List of CompositionItemRead instances
    """
    return [
        CompositionItemRead(
            id=recipe.warehouse_item.id,
            name=recipe.warehouse_item.name,
            quantity=recipe.quantity
        )
        for recipe in recipes
        if recipe.warehouse_item
    ]


def format_bundles(
    bundle_rows: List[Tuple[Any, Product]]
) -> List[ProductBundleItemRead]:
    """
    Format product bundles into frequently bought items.

    Args:
        bundle_rows: List of (ProductBundle, Product) tuples

    Returns:
        List of ProductBundleItemRead instances
    """
    return [
        ProductBundleItemRead(
            id=bundled_product.id,
            name=bundled_product.name,
            price=bundled_product.price,
            image=bundled_product.image
        )
        for _, bundled_product in bundle_rows
    ]


def format_pickup_locations(locations: List[PickupLocation]) -> List[str]:
    """
    Format pickup locations as strings.

    Args:
        locations: List of PickupLocation instances

    Returns:
        List of formatted location strings
    """
    return [
        f"{loc.address}{f' ({loc.landmark})' if loc.landmark else ''}"
        for loc in locations
    ]


def calculate_review_aggregates(
    reviews: List[ProductReview]
) -> Dict[str, Any]:
    """
    Calculate review aggregates: count, average rating, breakdown, photos.

    Args:
        reviews: List of ProductReview instances with photos loaded

    Returns:
        Dictionary with review statistics
    """
    review_count = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / review_count if review_count > 0 else 0.0

    # Rating breakdown
    breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in reviews:
        breakdown[review.rating] += 1

    # Collect review photos
    review_photos = []
    for review in reviews:
        if hasattr(review, 'photos') and review.photos:
            for photo in review.photos:
                review_photos.append(photo.url)

    return {
        "count": review_count,
        "average_rating": round(avg_rating, 1),
        "breakdown": breakdown,
        "photos": review_photos[:6],  # Limit to 6 photos
        "items": reviews[:5]  # Limit to 5 reviews initially
    }


def calculate_company_review_aggregates(
    reviews: List[CompanyReview]
) -> Dict[str, Any]:
    """
    Calculate company review aggregates.

    Args:
        reviews: List of CompanyReview instances

    Returns:
        Dictionary with review statistics
    """
    review_count = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / review_count if review_count > 0 else 0.0

    # Rating breakdown
    breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in reviews:
        breakdown[review.rating] += 1

    return {
        "count": review_count,
        "average_rating": round(avg_rating, 1),
        "breakdown": breakdown,
        "photos": [],  # Company reviews don't have photos
        "items": reviews[:5]  # Limit to 5 reviews initially
    }


def build_product_detail_read(
    product: Product,
    images: List[ProductImage],
    variants: List[ProductVariant],
    addons: List[ProductAddon],
    composition: List[CompositionItemRead],
    frequently_bought: List[ProductBundleItemRead],
    pickup_locations: List[str],
    product_reviews: List[ProductReview],
    company_reviews: List[CompanyReview]
) -> ProductDetailRead:
    """
    Build complete ProductDetailRead response with all relationships.

    Args:
        product: Product instance
        images: List of product images
        variants: List of product variants
        addons: List of product addons
        composition: Formatted composition items
        frequently_bought: Formatted bundle items
        pickup_locations: Formatted pickup location strings
        product_reviews: List of product reviews with photos
        company_reviews: List of company reviews

    Returns:
        ProductDetailRead instance with all enriched data
    """
    # Calculate product review aggregates
    product_aggregates = calculate_review_aggregates(product_reviews)
    company_aggregates = calculate_company_review_aggregates(company_reviews)

    return ProductDetailRead(
        id=product.id,
        name=product.name,
        price=product.price,
        type=product.type,
        description=product.description,
        image=product.image,
        enabled=product.enabled,
        is_featured=product.is_featured,
        colors=product.colors,
        occasions=product.occasions,
        cities=product.cities,
        tags=product.tags,
        manufacturingTime=product.manufacturingTime,
        width=product.width,
        height=product.height,
        shelfLife=product.shelfLife,
        rating=round(product_aggregates["average_rating"], 1) if product_aggregates["count"] > 0 else None,
        review_count=product_aggregates["count"],
        rating_count=product_aggregates["count"],  # Simplified: same as review_count
        images=images,
        variants=variants,
        composition=composition,
        addons=addons,
        frequently_bought=frequently_bought,
        pickup_locations=pickup_locations,
        reviews={
            "product": product_aggregates,
            "company": company_aggregates
        }
    )


def build_product_stats_response(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build product statistics response.

    Args:
        stats: Statistics dictionary from helpers

    Returns:
        Formatted statistics response
    """
    return {
        "total_products": stats["total"],
        "enabled_products": stats["enabled"],
        "disabled_products": stats["disabled"],
        "by_type": stats["by_type"]
    }
