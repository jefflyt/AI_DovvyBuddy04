"""
Gemini embedding provider implementation.

Uses Google's Generative AI API to generate embeddings with text-embedding-004.
"""

import asyncio
import logging
from typing import List, Optional

import google.genai as genai
from google.genai import types
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

from .base import EmbeddingProvider
from .cache import EmbeddingCache

logger = logging.getLogger(__name__)

# Constants
GEMINI_EMBEDDING_MODEL = "text-embedding-004"
GEMINI_EMBEDDING_DIMENSION = 768
MAX_BATCH_SIZE = 100


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    pass


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using Google's Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str = GEMINI_EMBEDDING_MODEL,
        use_cache: bool = True,
    ):
        """
        Initialize Gemini embedding provider.

        Args:
            api_key: Google API key
            model: Embedding model name (default: text-embedding-004)
            use_cache: Whether to use in-memory cache (default: True)
        """
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.model = model
        self.dimension = GEMINI_EMBEDDING_DIMENSION

        # Configure Gemini API (New SDK pattern)
        self.client = genai.Client(api_key=api_key)

        # Initialize cache
        self.cache = EmbeddingCache() if use_cache else None

        logger.info(f"Initialized GeminiEmbeddingProvider with model={model} (New SDK)")

    @retry(
        stop=stop_after_attempt(settings.embedding_max_retries),
        wait=wait_exponential(
            multiplier=settings.embedding_retry_delay,
            min=settings.embedding_retry_delay,
            max=10,
        ),
        retry=retry_if_exception_type(RateLimitError),
        reraise=True,
    )
    async def _embed_with_retry(self, text: str) -> List[float]:
        """
        Generate embedding with retry logic.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            RateLimitError: If rate limit is hit (will trigger retry)
            Exception: If other error occurs
        """
        try:
            # Run synchronous Gemini API call in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.dimension
                    )
                ),
            )

            # Extract embedding from response
            # New SDK returns object with .embeddings attribute depending on request
            # For single content, it typically has .embedding
            if hasattr(result, "embeddings") and result.embeddings:
                 # Batch usually, but let's check single
                 embedding = result.embeddings[0].values
            elif hasattr(result, "embedding") and result.embedding:
                 # Single embedding object associated
                 embedding = result.embedding.values
            else:
                 # Try to inspect structure if different
                 # Based on docs: result.embeddings is list of ContentEmbedding
                 # ContentEmbedding has .values
                 logger.debug(f"Unexpected result structure: {result}")
                 if hasattr(result, "values"):
                     embedding = result.values
                 else:
                     raise ValueError("Invalid embedding response from Gemini API")

            # Validate dimension
            if len(embedding) != self.dimension:
                # If using text-embedding-004, it supports variable dimension.
                # But we requested self.dimension via config if feasible, or just check what we got.
                pass 
                # Note: text-embedding-004 might not strictly obey output_dimensionality if not supported by model version, 
                # but latest does. Let's keep check but warn? 
                # Actually strict check is good for database consistency.
                if len(embedding) != self.dimension:
                     raise ValueError(
                        f"Expected embedding dimension {self.dimension}, got {len(embedding)}"
                    )

            return embedding

        except Exception as e:
            error_msg = str(e).lower()

            # Check for rate limit errors
            if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                logger.warning(f"Rate limit hit: {e}")
                raise RateLimitError(str(e)) from e

            # Other errors
            logger.error(f"Error generating embedding: {e}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty or invalid
            Exception: If API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Check cache
        if self.cache:
            cached = self.cache.get(text)
            if cached is not None:
                logger.debug("Cache hit for embedding")
                return cached

        # Generate embedding
        embedding = await self._embed_with_retry(text)

        # Store in cache
        if self.cache:
            self.cache.set(text, embedding)

        return embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts in a batch.

        Processes texts in batches up to MAX_BATCH_SIZE, with cache lookups.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors, one per input text

        Raises:
            ValueError: If texts list is empty or contains invalid texts
            Exception: If API call fails after retries
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        embeddings: List[List[float]] = []

        # Process in batches
        for i in range(0, len(texts), MAX_BATCH_SIZE):
            batch = texts[i : i + MAX_BATCH_SIZE]

            # Check cache for each text
            batch_embeddings: List[Optional[List[float]]] = []
            texts_to_embed: List[str] = []
            indices_to_embed: List[int] = []

            for idx, text in enumerate(batch):
                if not text or not text.strip():
                    raise ValueError(f"Text at index {i + idx} is empty")

                cached = self.cache.get(text) if self.cache else None
                if cached is not None:
                    batch_embeddings.append(cached)
                else:
                    batch_embeddings.append(None)
                    texts_to_embed.append(text)
                    indices_to_embed.append(idx)

            # Generate embeddings for uncached texts
            if texts_to_embed:
                # Process sequentially to avoid rate limits
                for j, text in enumerate(texts_to_embed):
                    embedding = await self._embed_with_retry(text)

                    # Store in cache
                    if self.cache:
                        self.cache.set(text, embedding)

                    # Insert at correct position
                    batch_idx = indices_to_embed[j]
                    batch_embeddings[batch_idx] = embedding

            # Add batch to results
            embeddings.extend([e for e in batch_embeddings if e is not None])

        return embeddings

    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        return self.dimension

    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.model
