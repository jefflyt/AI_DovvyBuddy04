"""
Type definitions for RAG services.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ContentChunk:
    """A chunk of content with metadata."""

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkingOptions:
    """Options for text chunking."""

    target_tokens: int = 650
    max_tokens: int = 800
    min_tokens: int = 100
    overlap_tokens: int = 50


@dataclass
class RetrievalResult:
    """Result from vector similarity search."""

    chunk_id: str
    text: str
    similarity: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalOptions:
    """Options for vector retrieval."""

    top_k: int = 5
    min_similarity: float = 0.0
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGContext:
    """Context retrieved for RAG."""

    query: str
    results: List[RetrievalResult]
    formatted_context: str
