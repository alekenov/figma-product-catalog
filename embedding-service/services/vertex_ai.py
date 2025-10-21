"""
Vertex AI Client for Multimodal Embeddings

This module handles communication with Google Vertex AI for generating
image and text embeddings using the multimodal-embedding model.

Requirements:
- GCP service account with Vertex AI permissions
- Service account key (JSON) as environment variable
"""

import json
import logging
import base64
from typing import List, Optional
import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class VertexAIClient:
    """
    Client for Google Vertex AI Multimodal Embeddings API.

    This client handles authentication and embedding generation for images
    using Google's multimodal-embedding@001 model.

    Attributes:
        project_id: GCP project ID
        location: GCP region (e.g., us-central1)
        model: Model name (default: multimodalembedding@001)
        embedding_dimension: Vector dimensions (512 for multimodal-embedding@001)
    """

    EMBEDDING_MODEL = "multimodalembedding@001"
    EMBEDDING_DIMENSION = 512
    API_VERSION = "v1"

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        service_account_key: str = None
    ):
        """
        Initialize Vertex AI client.

        Args:
            project_id: GCP project ID
            location: GCP region (default: us-central1)
            service_account_key: Service account JSON key as string

        Raises:
            ValueError: If credentials are invalid
        """
        self.project_id = project_id
        self.location = location
        self.model = self.EMBEDDING_MODEL

        # Parse service account credentials
        try:
            if service_account_key:
                credentials_dict = json.loads(service_account_key)
                self.credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
            else:
                raise ValueError("Service account key is required")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse service account key: {e}")
            raise ValueError("Invalid service account key JSON")

        # Build API endpoint
        self.endpoint = (
            f"https://{location}-aiplatform.googleapis.com/{self.API_VERSION}/"
            f"projects/{project_id}/locations/{location}/publishers/google/models/{self.model}:predict"
        )

        logger.info(f"Vertex AI client initialized (project: {project_id}, location: {location})")

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token for API requests.

        Returns:
            str: Valid access token

        Raises:
            Exception: If token refresh fails
        """
        try:
            # Refresh token if expired
            if not self.credentials.valid:
                self.credentials.refresh(Request())

            return self.credentials.token

        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise

    async def generate_image_embedding(
        self,
        image_bytes: bytes,
        dimension: Optional[int] = None
    ) -> List[float]:
        """
        Generate embedding for an image.

        Args:
            image_bytes: Image data as bytes
            dimension: Optional custom embedding dimension (default: 512)

        Returns:
            List[float]: Normalized embedding vector (512D by default)

        Raises:
            Exception: If API request fails
        """
        if dimension is None:
            dimension = self.EMBEDDING_DIMENSION

        try:
            # Get access token
            access_token = self._get_access_token()

            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            # Build request payload
            payload = {
                "instances": [
                    {
                        "image": {
                            "bytesBase64Encoded": image_base64
                        }
                    }
                ],
                "parameters": {
                    "dimension": dimension
                }
            }

            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()

            # Parse response
            result = response.json()

            # Extract embedding from response
            if "predictions" in result and len(result["predictions"]) > 0:
                prediction = result["predictions"][0]

                # Handle both response formats
                if "imageEmbedding" in prediction:
                    embedding = prediction["imageEmbedding"]
                elif "embeddings" in prediction:
                    embedding = prediction["embeddings"]
                else:
                    raise ValueError("Unexpected API response format")

                # Normalize embedding (L2 normalization)
                embedding = self._normalize_vector(embedding)

                logger.debug(f"Generated embedding: {len(embedding)} dimensions")
                return embedding

            else:
                raise ValueError("No predictions in API response")

        except httpx.HTTPError as e:
            logger.error(f"Vertex AI API request failed: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response: {e.response.text}")
            raise

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}", exc_info=True)
            raise

    async def generate_text_embedding(
        self,
        text: str,
        dimension: Optional[int] = None
    ) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text
            dimension: Optional custom embedding dimension (default: 512)

        Returns:
            List[float]: Normalized embedding vector (512D by default)

        Raises:
            Exception: If API request fails
        """
        if dimension is None:
            dimension = self.EMBEDDING_DIMENSION

        try:
            # Get access token
            access_token = self._get_access_token()

            # Build request payload
            payload = {
                "instances": [
                    {
                        "text": text
                    }
                ],
                "parameters": {
                    "dimension": dimension
                }
            }

            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()

            # Parse response
            result = response.json()

            # Extract embedding from response
            if "predictions" in result and len(result["predictions"]) > 0:
                prediction = result["predictions"][0]

                # Handle both response formats
                if "textEmbedding" in prediction:
                    embedding = prediction["textEmbedding"]
                elif "embeddings" in prediction:
                    embedding = prediction["embeddings"]
                else:
                    raise ValueError("Unexpected API response format")

                # Normalize embedding (L2 normalization)
                embedding = self._normalize_vector(embedding)

                logger.debug(f"Generated text embedding: {len(embedding)} dimensions")
                return embedding

            else:
                raise ValueError("No predictions in API response")

        except httpx.HTTPError as e:
            logger.error(f"Vertex AI API request failed: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response: {e.response.text}")
            raise

        except Exception as e:
            logger.error(f"Text embedding generation failed: {e}", exc_info=True)
            raise

    @staticmethod
    def _normalize_vector(vector: List[float]) -> List[float]:
        """
        Normalize vector to unit length (L2 normalization).

        This is important for cosine similarity search, as it allows us
        to use dot product instead of cosine distance.

        Args:
            vector: Input vector

        Returns:
            List[float]: Normalized vector
        """
        import math

        # Calculate L2 norm (Euclidean length)
        norm = math.sqrt(sum(x * x for x in vector))

        # Avoid division by zero
        if norm == 0:
            return vector

        # Normalize
        return [x / norm for x in vector]
