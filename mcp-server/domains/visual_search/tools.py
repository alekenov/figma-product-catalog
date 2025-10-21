"""
Visual search tools for MCP server.
Handles AI-powered visual product search using CLIP embeddings.
"""
from typing import List, Dict, Any, Optional
import httpx
import base64
import os
from core.registry import ToolRegistry
from core.logging import get_logger

logger = get_logger(__name__)

VISUAL_SEARCH_API = "https://visual-search.alekenov.workers.dev"
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "https://figma-product-catalog-production.up.railway.app/api/v1")


@ToolRegistry.register(domain="visual_search", requires_auth=False, is_public=True)
async def search_similar_bouquets(
    image_url: str,
    topK: int = 5,
) -> Dict[str, Any]:
    """
    Find similar bouquets using AI-powered visual search.

    This tool uses Google Vertex AI multimodal embeddings to analyze flower bouquet
    images and find visually similar products in the catalog. Perfect for helping
    customers find bouquets when they have a reference photo.

    Args:
        image_url: URL of the bouquet image to search for.
                   Must be a valid HTTP/HTTPS URL to a flower bouquet photo.
                   Supported formats: PNG, JPEG, WebP.
                   Example: "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png"

        topK: Maximum number of similar products to return (1-20).
              Default is 5. Higher values return more results but may include less relevant matches.

    Returns:
        Dictionary with search results:
        {
            "success": bool,
            "exact": [  # Products with 85%+ similarity (very similar)
                {
                    "product_id": int,
                    "name": str,
                    "price": int,  # Price in kopecks (divide by 100 for tenge)
                    "image_url": str,
                    "similarity": float  # 0.85-1.0 (85%-100% match)
                }
            ],
            "similar": [  # Products with 70-85% similarity (somewhat similar)
                # Same structure as exact
            ],
            "search_time_ms": int,  # How long the search took
            "total_indexed": int  # Total products available for search
        }

    Example usage:
        # Customer sends a photo of a bouquet they like
        result = await search_similar_bouquets(
            image_url="https://example.com/customer-bouquet.jpg",
            topK=3
        )

        # Response:
        # {
        #   "success": true,
        #   "exact": [
        #     {"product_id": 5, "name": "Букет роз", "price": 15000, "similarity": 0.92}
        #   ],
        #   "similar": [
        #     {"product_id": 8, "name": "Букет тюльпанов", "price": 12000, "similarity": 0.78}
        #   ]
        # }

    Use cases:
        - Customer: "Найди букет похожий на этот" + photo
        - Customer: "Хочу что-то такое же" + photo
        - Customer sends bouquet photo without text
        - Customer: "Есть ли у вас такой?" + photo

    Notes:
        - First search may take 7-10 seconds (cold start)
        - Subsequent searches are faster (3-5 seconds)
        - Similarity > 0.85 = very similar (exact category)
        - Similarity 0.70-0.85 = somewhat similar (similar category)
        - Similarity < 0.70 = not similar (excluded from results)
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Visual search request: image_url={image_url[:80]}..., topK={topK}")

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

            # Call Visual Search API with base64 image
            response = await client.post(
                f"{VISUAL_SEARCH_API}/search",
                json={
                    "image_base64": image_data_uri,
                    "topK": topK
                }
            )
            response.raise_for_status()
            result = response.json()

            # Log results summary
            exact_count = len(result.get("exact", []))
            similar_count = len(result.get("similar", []))
            search_time = result.get("search_time_ms", 0)

            logger.info(
                f"Visual search completed: "
                f"{exact_count} exact, {similar_count} similar, {search_time}ms"
            )

            return result

        except httpx.HTTPError as e:
            logger.error(f"Visual search API error: {e}")
            return {
                "success": False,
                "error": f"Failed to search: {str(e)}",
                "exact": [],
                "similar": []
            }
        except Exception as e:
            logger.error(f"Unexpected error in visual search: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "exact": [],
                "similar": []
            }


@ToolRegistry.register(domain="visual_search", requires_auth=False, is_public=True)
async def search_similar_bouquets_pgvector(
    image_url: str,
    shop_id: int,
    topK: int = 5,
) -> Dict[str, Any]:
    """
    Find similar bouquets using pgvector PostgreSQL search (Alternative method).

    This tool uses the same Vertex AI embeddings but searches in PostgreSQL pgvector
    database instead of Cloudflare Vectorize. Useful for comparison and A/B testing.

    IMPORTANT: This version requires shop_id parameter (multi-tenancy support).

    Args:
        image_url: URL of the bouquet image to search for.
                   Must be a valid HTTP/HTTPS URL to a flower bouquet photo.
                   Supported formats: PNG, JPEG, WebP.
                   Example: "https://flower-shop-images.alekenov.workers.dev/mg6684nq-0y61rde1owm.png"

        shop_id: Shop ID to search within (required for multi-tenancy).
                 Example: 17008 for testing shop, 8 for main shop.

        topK: Maximum number of similar products to return (1-20).
              Default is 5. Higher values return more results but may include less relevant matches.

    Returns:
        Dictionary with search results (same format as search_similar_bouquets):
        {
            "success": bool,
            "exact": [  # Products with 85%+ similarity
                {
                    "id": int,  # Note: "id" instead of "product_id"
                    "name": str,
                    "price": int,  # Price in kopecks
                    "image": str,  # Note: "image" instead of "image_url"
                    "similarity": float
                }
            ],
            "similar": [  # Products with 70-85% similarity
                # Same structure as exact
            ],
            "search_time_ms": int,
            "total_indexed": int,
            "method": "pgvector"  # Indicates this used pgvector
        }

    Example usage:
        # Customer sends a photo for shop_id=17008
        result = await search_similar_bouquets_pgvector(
            image_url="https://example.com/customer-bouquet.jpg",
            shop_id=17008,
            topK=3
        )

    Use cases (same as Cloudflare version):
        - Customer: "Найди букет похожий на этот" + photo
        - Customer: "Хочу что-то такое же" + photo
        - Customer sends bouquet photo without text
        - Customer: "Есть ли у вас такой?" + photo

    Differences from Cloudflare version:
        - Uses PostgreSQL pgvector instead of Cloudflare Vectorize
        - Requires shop_id parameter (multi-tenancy)
        - May have different latency (Railway PostgreSQL vs Cloudflare Edge)
        - Returns product "id" and "image" fields (not "product_id" and "image_url")
        - Searches in Railway database (synced with backend)

    Notes:
        - May be slower on first request (no edge caching)
        - Uses same Vertex AI embeddings via embedding-service
        - Filtered by shop_id for data isolation
        - Similarity thresholds: >0.85 exact, 0.70-0.85 similar, <0.70 excluded
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(
                f"pgvector search request: image_url={image_url[:80]}..., "
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
                f"pgvector search completed: "
                f"{exact_count} exact, {similar_count} similar, {search_time}ms, "
                f"{total_indexed} indexed, method={method}"
            )

            return result

        except httpx.HTTPError as e:
            logger.error(f"pgvector search API error: {e}")
            return {
                "success": False,
                "error": f"Failed to search: {str(e)}",
                "exact": [],
                "similar": [],
                "method": "pgvector"
            }
        except Exception as e:
            logger.error(f"Unexpected error in pgvector search: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "exact": [],
                "similar": [],
                "method": "pgvector"
            }
