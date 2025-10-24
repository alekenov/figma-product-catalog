"""
Visual search tools for MCP server.
Handles AI-powered visual product search using pgvector PostgreSQL.
"""
from typing import Dict, Any
import httpx
import base64
import os
from core.registry import ToolRegistry
from core.logging import get_logger

logger = get_logger(__name__)

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "https://figma-product-catalog-production.up.railway.app/api/v1")


@ToolRegistry.register(domain="visual_search", requires_auth=False, is_public=True)
async def search_similar_bouquets(
    image_url: str,
    shop_id: int,
    topK: int = 5,
) -> Dict[str, Any]:
    """
    Find similar bouquets using AI-powered visual search.

    This tool uses Google Vertex AI multimodal embeddings to analyze flower bouquet
    images and find visually similar products in the catalog. Perfect for helping
    customers find bouquets when they have a reference photo.

    The search uses PostgreSQL pgvector to efficiently find similar products based on
    visual similarity. Results are filtered by shop_id for multi-tenancy support.

    Args:
        image_url: URL of the bouquet image to search for.
                   Must be a valid HTTP/HTTPS URL to a flower bouquet photo.
                   Supported formats: PNG, JPEG, WebP.
                   Example: "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png"

        shop_id: Shop ID to search within (required for multi-tenancy).
                 Example: 17008 for production shop, 8 for development shop.

        topK: Maximum number of similar products to return (1-20).
              Default is 5. Higher values return more results but may include less relevant matches.

    Returns:
        Dictionary with search results:
        {
            "success": bool,
            "exact": [  # Products with 85%+ similarity (very similar)
                {
                    "id": int,
                    "name": str,
                    "price": int,  # Price in kopecks (divide by 100 for tenge)
                    "image": str,
                    "similarity": float  # 0.85-1.0 (85%-100% match)
                }
            ],
            "similar": [  # Products with 70-85% similarity (somewhat similar)
                # Same structure as exact
            ],
            "search_time_ms": int,  # How long the search took
            "total_indexed": int,  # Total products available for search
            "method": "pgvector"  # Search method used
        }

    Example usage:
        # Customer sends a photo of a bouquet they like
        result = await search_similar_bouquets(
            image_url="https://example.com/customer-bouquet.jpg",
            shop_id=17008,
            topK=3
        )

        # Response:
        # {
        #   "success": true,
        #   "exact": [
        #     {"id": 5, "name": "Букет роз", "price": 15000, "similarity": 0.92}
        #   ],
        #   "similar": [
        #     {"id": 8, "name": "Букет тюльпанов", "price": 12000, "similarity": 0.78}
        #   ]
        # }

    Use cases:
        - Customer: "Найди букет похожий на этот" + photo
        - Customer: "Хочу что-то такое же" + photo
        - Customer sends bouquet photo without text
        - Customer: "Есть ли у вас такой?" + photo

    Notes:
        - Uses Google Vertex AI embeddings via embedding-service
        - Filtered by shop_id for data isolation
        - Similarity thresholds: >0.85 exact, 0.70-0.85 similar, <0.70 excluded
        - First search may take longer due to embedding generation
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(
                f"Visual search request: image_url={image_url[:80]}..., "
                f"shop_id={shop_id}, topK={topK}"
            )

            # Download the image from URL
            logger.info(f"Downloading image from: {image_url}")
            img_response = await client.get(image_url)
            img_response.raise_for_status()
            image_bytes = img_response.content

            # Detect content type
            content_type = img_response.headers.get("content-type", "image/jpeg")
            logger.info(f"Downloaded {len(image_bytes)} bytes, content_type: {content_type}")

            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            # Format as data URI
            image_data_uri = f"data:{content_type};base64,{image_base64}"
            logger.info(f"Converted to base64 data URI, length: {len(image_data_uri)}")

            # Call Backend API pgvector endpoint
            response = await client.post(
                f"{BACKEND_API_URL}/products/search/similar",
                json={
                    "image_base64": image_data_uri,
                    "shop_id": shop_id,
                    "topK": topK,
                    "min_similarity": 0.70  # Match Cloudflare threshold
                }
            )
            response.raise_for_status()
            result = response.json()

            # Log results summary
            exact_count = len(result.get("exact", []))
            similar_count = len(result.get("similar", []))
            search_time = result.get("search_time_ms", 0)
            total_indexed = result.get("total_indexed", 0)
            method = result.get("method", "pgvector")

            logger.info(
                f"Visual search completed: "
                f"{exact_count} exact, {similar_count} similar, {search_time}ms, "
                f"{total_indexed} indexed, method={method}"
            )

            return result

        except httpx.HTTPError as e:
            logger.error(f"Visual search API error: {e}")
            return {
                "success": False,
                "error": f"Failed to search: {str(e)}",
                "exact": [],
                "similar": [],
                "method": "pgvector"
            }
        except Exception as e:
            logger.error(f"Unexpected error in visual search: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "exact": [],
                "similar": [],
                "method": "pgvector"
            }
