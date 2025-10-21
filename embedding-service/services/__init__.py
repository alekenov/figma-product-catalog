"""
Services package for Embedding Service.

This package contains core services for ML embedding generation.
"""

from .vertex_ai import VertexAIClient
from .embedding import EmbeddingService

__all__ = ["VertexAIClient", "EmbeddingService"]
