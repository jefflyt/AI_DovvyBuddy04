"""
Type definitions for RAG services.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
    source_citation: Optional[str] = None  # Source path for RAF citation tracking

    def __post_init__(self):
        """Extract citation from metadata if not explicitly provided."""
        if self.source_citation is None and "content_path" in self.metadata:
            self.source_citation = self.metadata["content_path"]


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
    citations: List[str] = field(default_factory=list)  # Source citations for RAF
    has_data: bool = True  # False when NO_DATA signal returned
