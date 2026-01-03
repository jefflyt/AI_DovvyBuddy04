"""
In-memory LRU cache for embeddings.

Provides TTL-based caching to reduce API calls for frequently embedded texts.
"""

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple, Union

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    Simple in-memory LRU cache with TTL for embeddings.

    Uses OrderedDict for LRU behavior and stores (embedding, timestamp) tuples.
    """

    def __init__(
            self, max_size: Optional[int] = None, ttl_seconds: Optional[int] = None
    ):
        """
        Initialize embedding cache.

        Args:
            max_size: Maximum number of entries (default: from settings)
            ttl_seconds: Time-to-live in seconds (default: from settings)
        """
        self.max_size = max_size or settings.embedding_cache_size
        self.ttl_seconds = ttl_seconds or settings.embedding_cache_ttl
        self.cache: OrderedDict[str, Tuple[List[float], float]] = OrderedDict()
        self.hits = 0
        self.misses = 0

        logger.info(
            f"Initialized EmbeddingCache with max_size={self.max_size}, ttl={self.ttl_seconds}s"
        )

    def _hash_text(self, text: str) -> str:
        """
        Generate a hash key for the text.

        Args:
            text: Text to hash

        Returns:
            SHA256 hash of the text
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[List[float]]:
        """
        Get embedding from cache.

        Args:
            text: Text to look up

        Returns:
            Embedding vector if found and not expired, None otherwise
        """
        key = self._hash_text(text)

        if key not in self.cache:
            self.misses += 1
            return None

        embedding, timestamp = self.cache[key]
        current_time = time.time()

        # Check if expired
        if current_time - timestamp > self.ttl_seconds:
            logger.debug("Cache entry expired")
            del self.cache[key]
            self.misses += 1
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1

        return embedding

    def set(self, text: str, embedding: List[float]) -> None:
        """
        Store embedding in cache.

        Args:
            text: Text key
            embedding: Embedding vector to store
        """
        key = self._hash_text(text)
        current_time = time.time()

        # Remove oldest entry if at capacity
        if key not in self.cache and len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry, size={len(self.cache)}")

        # Store embedding with timestamp
        self.cache[key] = (embedding, current_time)

        # Move to end (most recently used)
        self.cache.move_to_end(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (size, hits, misses, hit_rate)
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
