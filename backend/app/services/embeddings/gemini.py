"""
Gemini embedding provider implementation.

Uses Google's Generative AI API to generate embeddings with text-embedding-004.
"""

import asyncio
import logging
import time
from collections import deque
from typing import Deque, List, Optional, Tuple

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
MAX_EMBEDDING_BATCH_SIZE = 250
TOKENS_PER_CHAR_ESTIMATE = 0.25


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    pass


class _EmbeddingRateLimiter:
    """Simple sliding-window limiter for requests and tokens."""

    def __init__(self, rpm_limit: int, tpm_limit: int, window_seconds: int) -> None:
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.window_seconds = window_seconds
        self._lock = asyncio.Lock()
        self._events: Deque[Tuple[float, int]] = deque()

    def _prune(self, now: float) -> None:
        while self._events and now - self._events[0][0] >= self.window_seconds:
            self._events.popleft()

    def _current_usage(self, now: float) -> Tuple[int, int]:
        self._prune(now)
        tokens_used = sum(tokens for _, tokens in self._events)
        return len(self._events), tokens_used

    def _time_until_tokens_available(self, now: float, needed_tokens: int) -> float:
        if needed_tokens <= 0:
            return 0.0

        running = 0
        for timestamp, tokens in self._events:
            running += tokens
            if running >= needed_tokens:
                return max(0.0, (timestamp + self.window_seconds) - now)
        return 0.0

    async def wait_for_slot(self, request_tokens: int) -> None:
        async with self._lock:
            while True:
                now = time.time()
                request_count, tokens_used = self._current_usage(now)

                under_rpm = request_count < self.rpm_limit
                under_tpm = (tokens_used + request_tokens) <= self.tpm_limit

                if under_rpm and under_tpm:
                    self._events.append((now, request_tokens))
                    return

                wait_for_rpm = 0.0
                if not under_rpm and self._events:
                    wait_for_rpm = (self._events[0][0] + self.window_seconds) - now

                required_tokens = (tokens_used + request_tokens) - self.tpm_limit
                wait_for_tpm = self._time_until_tokens_available(now, required_tokens)

                sleep_for = max(0.0, wait_for_rpm, wait_for_tpm)
                if sleep_for > 0:
                    await asyncio.sleep(sleep_for)
                else:
                    await asyncio.sleep(0.01)


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using Google's Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
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

        resolved_model = model or settings.embedding_model or GEMINI_EMBEDDING_MODEL
        self.model = resolved_model
        self.dimension = GEMINI_EMBEDDING_DIMENSION

        # Configure Gemini API (New SDK pattern)
        self.client = genai.Client(api_key=api_key)

        # Initialize cache
        self.cache = EmbeddingCache() if use_cache else None
        self.rate_limiter = _EmbeddingRateLimiter(
            rpm_limit=settings.embedding_rpm_limit,
            tpm_limit=settings.embedding_tpm_limit,
            window_seconds=settings.embedding_rate_window_seconds,
        )

        logger.info(
            "Initialized GeminiEmbeddingProvider with model=%s (New SDK)",
            self.model,
        )

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
            request_tokens = self._estimate_tokens(text)
            await self.rate_limiter.wait_for_slot(request_tokens)

            # Run synchronous Gemini API call in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.dimension,
                        task_type="RETRIEVAL_DOCUMENT"
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

    async def _embed_batch_with_retry(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts with retry logic.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            request_tokens = sum(self._estimate_tokens(text) for text in texts)
            await self.rate_limiter.wait_for_slot(request_tokens)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.model,
                    contents=texts,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.dimension,
                        task_type="RETRIEVAL_DOCUMENT"
                    ),
                ),
            )

            if not hasattr(result, "embeddings") or not result.embeddings:
                raise ValueError("Invalid embedding response from Gemini API")

            embeddings = [item.values for item in result.embeddings]
            for embedding in embeddings:
                if len(embedding) != self.dimension:
                    raise ValueError(
                        f"Expected embedding dimension {self.dimension}, got {len(embedding)}"
                    )

            return embeddings
        except Exception as e:
            error_msg = str(e).lower()

            if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                logger.warning(f"Rate limit hit: {e}")
                raise RateLimitError(str(e)) from e

            logger.error(f"Error generating embeddings: {e}")
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

        batch_size = min(settings.embedding_batch_size, MAX_EMBEDDING_BATCH_SIZE)

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

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
                embeddings_to_insert = await self._embed_batch_with_retry(texts_to_embed)

                for j, embedding in enumerate(embeddings_to_insert):
                    text = texts_to_embed[j]

                    if self.cache:
                        self.cache.set(text, embedding)

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

    def _estimate_tokens(self, text: str) -> int:
        estimated = max(1, int(len(text) * TOKENS_PER_CHAR_ESTIMATE))
        return estimated
