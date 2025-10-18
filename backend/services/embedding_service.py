"""
Embedding Service - generates CLIP embeddings for images using Hugging Face API

Provides functions to generate 512-dimensional CLIP embeddings from image files or URLs.
Used for visual similarity search of products.
"""

import os
import io
import asyncio
import requests
import numpy as np
from typing import Optional, List
from PIL import Image
import structlog

logger = structlog.get_logger()

# Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN", "")
EMBEDDING_DIM = 512

# Similarity thresholds
SIMILARITY_THRESHOLD_HIGH = 0.7  # Very similar (top results)
SIMILARITY_THRESHOLD_LOW = 0.5   # Moderately similar (acceptable)


class EmbeddingError(Exception):
    """Raised when embedding generation fails"""
    pass


def validate_image_quality(image_bytes: bytes, max_size_mb: float = 10) -> bool:
    """
    Validate image quality and size

    Args:
        image_bytes: Image data as bytes
        max_size_mb: Maximum allowed file size in MB

    Returns:
        True if image is valid, False otherwise
    """
    try:
        # Check file size
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.warning(
                "image_too_large",
                size_mb=size_mb,
                max_size_mb=max_size_mb
            )
            return False

        # Try to open image to validate format
        image = Image.open(io.BytesIO(image_bytes))

        # Check minimum dimensions (must be at least 32x32)
        if image.width < 32 or image.height < 32:
            logger.warning(
                "image_too_small",
                width=image.width,
                height=image.height
            )
            return False

        # Convert RGBA to RGB if needed (CLIP expects RGB)
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image

        return True

    except Exception as e:
        logger.error("image_validation_failed", error=str(e))
        return False


def generate_clip_embedding(image_bytes: bytes, retries: int = 3) -> Optional[List[float]]:
    """
    Generate CLIP embedding from image bytes using Hugging Face API

    Args:
        image_bytes: Image data as bytes
        retries: Number of retries on failure

    Returns:
        List of 512 floats representing the embedding, or None on failure

    Raises:
        EmbeddingError: If all retries fail
    """
    if not HF_TOKEN:
        raise EmbeddingError("HUGGING_FACE_TOKEN environment variable not set")

    # Validate image
    if not validate_image_quality(image_bytes):
        raise EmbeddingError("Invalid image: failed quality checks")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    for attempt in range(retries):
        try:
            logger.info(
                "generating_embedding",
                attempt=attempt + 1,
                retries=retries,
                image_size_bytes=len(image_bytes)
            )

            response = requests.post(
                HF_API_URL,
                headers=headers,
                data=image_bytes,
                timeout=30
            )

            if response.status_code == 200:
                embedding = response.json()

                # Validate embedding
                if not isinstance(embedding, list) or len(embedding) != EMBEDDING_DIM:
                    raise EmbeddingError(
                        f"Invalid embedding dimensions: expected {EMBEDDING_DIM}, "
                        f"got {len(embedding) if isinstance(embedding, list) else 'unknown'}"
                    )

                # Normalize embedding to unit vector (important for cosine similarity)
                embedding_array = np.array(embedding, dtype=np.float32)
                norm = np.linalg.norm(embedding_array)
                if norm > 0:
                    embedding_array = embedding_array / norm

                logger.info(
                    "embedding_generated_success",
                    embedding_dim=len(embedding_array),
                    norm_before=float(np.linalg.norm(np.array(embedding))),
                    norm_after=float(np.linalg.norm(embedding_array))
                )

                return embedding_array.tolist()

            elif response.status_code == 429:  # Rate limited
                logger.warning(
                    "hf_api_rate_limited",
                    attempt=attempt + 1,
                    retry_after=response.headers.get('Retry-After', 'unknown')
                )
                if attempt < retries - 1:
                    wait_time = int(response.headers.get('Retry-After', '5'))
                    asyncio.sleep(wait_time)
                    continue
                else:
                    raise EmbeddingError(f"Rate limited after {retries} retries")

            elif response.status_code == 503:  # Service unavailable
                logger.warning(
                    "hf_api_unavailable",
                    attempt=attempt + 1,
                    status_code=response.status_code
                )
                if attempt < retries - 1:
                    asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise EmbeddingError(f"Service unavailable after {retries} retries")

            else:
                error_msg = f"HF API error {response.status_code}: {response.text[:200]}"
                logger.error("hf_api_error", error=error_msg, status_code=response.status_code)

                if attempt < retries - 1 and response.status_code >= 500:
                    asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise EmbeddingError(error_msg)

        except requests.exceptions.Timeout:
            logger.warning("hf_api_timeout", attempt=attempt + 1)
            if attempt < retries - 1:
                asyncio.sleep(2 ** attempt)
                continue
            else:
                raise EmbeddingError("API timeout after all retries")

        except requests.exceptions.RequestException as e:
            logger.error("hf_api_request_error", error=str(e), attempt=attempt + 1)
            if attempt < retries - 1:
                asyncio.sleep(2 ** attempt)
                continue
            else:
                raise EmbeddingError(f"Request failed: {str(e)}")

    raise EmbeddingError("Failed to generate embedding after all retries")


def download_image_from_url(url: str, timeout: int = 10) -> Optional[bytes]:
    """
    Download image from URL

    Args:
        url: Image URL
        timeout: Request timeout in seconds

    Returns:
        Image bytes or None on failure
    """
    try:
        logger.info("downloading_image", url=url[:100])  # Log first 100 chars only

        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
            raise EmbeddingError(f"Invalid content type: {content_type}")

        # Read image data
        image_data = b''
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                image_data += chunk
                if len(image_data) > 10 * 1024 * 1024:  # 10 MB limit
                    raise EmbeddingError("Image too large")

        logger.info("image_downloaded_success", size_bytes=len(image_data))
        return image_data

    except requests.exceptions.RequestException as e:
        logger.error("image_download_failed", error=str(e), url=url[:100])
        return None
    except EmbeddingError as e:
        logger.error("image_download_error", error=str(e))
        return None


def calculate_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings

    Args:
        embedding1: First embedding (512-dim)
        embedding2: Second embedding (512-dim)

    Returns:
        Cosine similarity score between -1 and 1 (typically 0 to 1 for normalized vectors)
    """
    arr1 = np.array(embedding1, dtype=np.float32)
    arr2 = np.array(embedding2, dtype=np.float32)

    # Normalize
    arr1 = arr1 / (np.linalg.norm(arr1) + 1e-8)
    arr2 = arr2 / (np.linalg.norm(arr2) + 1e-8)

    similarity = np.dot(arr1, arr2)
    return float(similarity)


def embedding_vector_to_db_format(embedding: List[float]) -> str:
    """
    Convert embedding vector to database storage format

    For PostgreSQL with pgvector: stored as native vector type
    For SQLite: stored as JSON string

    Args:
        embedding: List of 512 floats

    Returns:
        Database representation (for SQLite, returns JSON string)
    """
    # PostgreSQL pgvector will handle it natively
    # For SQLite, we store as JSON string
    import json
    return json.dumps(embedding)


def db_format_to_embedding_vector(db_value: any) -> Optional[List[float]]:
    """
    Convert database value to embedding vector

    Args:
        db_value: Value from database (native vector or JSON string)

    Returns:
        List of 512 floats or None
    """
    if db_value is None:
        return None

    # If it's already a list, return it
    if isinstance(db_value, list):
        return db_value

    # If it's a string (SQLite JSON), parse it
    if isinstance(db_value, str):
        import json
        try:
            return json.loads(db_value)
        except:
            return None

    # If it's a pgvector Vector object, convert to list
    try:
        return list(db_value)
    except:
        return None
