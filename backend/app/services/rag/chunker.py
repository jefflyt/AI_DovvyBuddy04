"""
Text chunking for RAG.

Implements hybrid chunking strategy:
1. Split into sections by markdown headers
2. Check if section fits within max_tokens
3. If yes, keep intact; if no, split into paragraphs
4. Combine paragraphs into chunks with token limits
"""

import logging
import re
from typing import Any, Dict, List, Optional

import tiktoken

from .types import ChunkingOptions, ContentChunk

logger = logging.getLogger(__name__)

# Use GPT-3.5 tokenizer as approximation for Gemini
# (Gemini's tokenizer isn't available in tiktoken, but token counts are close enough)
_tokenizer = None
_tokenizer_failed = False
_FALLBACK_TOKENS_PER_CHAR_ESTIMATE = 0.25


def get_tokenizer():
    """Get or create tiktoken tokenizer."""
    global _tokenizer, _tokenizer_failed
    if _tokenizer_failed:
        return None

    if _tokenizer is None:
        try:
            _tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except Exception as exc:
            _tokenizer_failed = True
            logger.warning(
                "Tokenizer initialization failed, using approximate token counting: %s",
                exc,
            )
            return None
    return _tokenizer


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for

    Returns:
        Token count
    """
    if not text:
        return 0

    encoder = get_tokenizer()
    if encoder is not None:
        return len(encoder.encode(text))

    # Fallback for restricted/offline environments where tiktoken assets are unavailable.
    return max(1, int(len(text) * _FALLBACK_TOKENS_PER_CHAR_ESTIMATE))


def split_into_sections(text: str) -> List[Dict[str, str]]:
    """
    Split text into sections based on markdown headers (## or ###).

    Args:
        text: Markdown text to split

    Returns:
        List of dicts with 'header' and 'content' keys
    """
    sections = []
    lines = text.split("\n")
    current_header = ""
    current_content: list[str] = []

    for line in lines:
        # Check if line is a header (## or ###)
        header_match = re.match(r"^(#{2,3})\s+(.+)$", line)

        if header_match:
            # Save previous section if it has content
            if current_content:
                sections.append(
                    {
                        "header": current_header,
                        "content": "\n".join(current_content).strip(),
                    }
                )

            # Start new section
            current_header = line
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections.append(
            {"header": current_header, "content": "\n".join(current_content).strip()}
        )

    return sections


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs by double newline.

    Args:
        text: Text to split

    Returns:
        List of paragraphs
    """
    return [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]


def combine_paragraphs_into_chunks(
    paragraphs: List[str], header: str, options: ChunkingOptions
) -> List[str]:
    """
    Combine paragraphs into chunks that fit within token limits.

    Args:
        paragraphs: List of paragraphs to combine
        header: Section header to include in each chunk
        options: Chunking options

    Returns:
        List of chunk texts
    """
    chunks = []
    current_chunk: list[str] = []
    current_tokens = 0

    # Add header token count if present
    header_tokens = count_tokens(header + "\n\n") if header else 0

    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)

        # If single paragraph exceeds max tokens, include it as its own chunk
        if paragraph_tokens > options.max_tokens:
            # Save current chunk if it has content
            if current_chunk:
                chunk_text = (
                    f"{header}\n\n{chr(10).join(current_chunk)}"
                    if header
                    else "\n\n".join(current_chunk)
                )
                chunks.append(chunk_text)
                current_chunk = []
                current_tokens = 0

            # Add oversized paragraph as its own chunk
            chunk_text = f"{header}\n\n{paragraph}" if header else paragraph
            chunks.append(chunk_text)
            continue

        # Check if adding this paragraph would exceed target
        potential_tokens = current_tokens + paragraph_tokens + (2 if current_chunk else 0)

        if potential_tokens > options.target_tokens and current_chunk:
            # Save current chunk
            chunk_text = (
                f"{header}\n\n{chr(10).join(current_chunk)}"
                if header
                else "\n\n".join(current_chunk)
            )
            chunks.append(chunk_text)

            # Start new chunk with this paragraph
            current_chunk = [paragraph]
            current_tokens = header_tokens + paragraph_tokens
        else:
            # Add paragraph to current chunk
            current_chunk.append(paragraph)
            current_tokens += paragraph_tokens + (2 if len(current_chunk) > 1 else 0)

    # Save last chunk
    if current_chunk:
        chunk_text = (
            f"{header}\n\n{chr(10).join(current_chunk)}"
            if header
            else "\n\n".join(current_chunk)
        )
        chunks.append(chunk_text)

    return chunks


def chunk_text(
    text: str,
    content_path: str,
    frontmatter: Optional[Dict[str, Any]] = None,
    options: Optional[ChunkingOptions] = None,
) -> List[ContentChunk]:
    """
    Chunk text using hybrid strategy.

    1. Split into sections by markdown headers
    2. For each section, check if it fits within max_tokens
    3. If yes, keep section intact
    4. If no, split section into paragraphs and combine into chunks

    Args:
        text: Text to chunk
        content_path: Path to content file (for metadata)
        frontmatter: Frontmatter metadata (default: {})
        options: Chunking options (default: ChunkingOptions())

    Returns:
        List of ContentChunk objects
    """
    if options is None:
        options = ChunkingOptions()
    if frontmatter is None:
        frontmatter = {}

    chunks = []
    chunk_index = 0

    # Split into sections
    sections = split_into_sections(text)

    for section in sections:
        section_text = (
            f"{section['header']}\n\n{section['content']}"
            if section["header"]
            else section["content"]
        )

        # Skip empty sections
        if not section_text.strip():
            continue

        section_tokens = count_tokens(section_text)

        # If section fits within max tokens, keep it intact
        if section_tokens <= options.max_tokens:
            chunks.append(
                ContentChunk(
                    text=section_text,
                    metadata={
                        "content_path": content_path,
                        "chunk_index": chunk_index,
                        "section_header": section["header"] or None,
                        **frontmatter,
                    },
                )
            )
            chunk_index += 1
        else:
            # Split section into paragraphs and combine into chunks
            paragraphs = split_into_paragraphs(section["content"])
            section_chunks = combine_paragraphs_into_chunks(
                paragraphs, section["header"], options
            )

            for chunk_text in section_chunks:
                chunks.append(
                    ContentChunk(
                        text=chunk_text,
                        metadata={
                            "content_path": content_path,
                            "chunk_index": chunk_index,
                            "section_header": section["header"] or None,
                            **frontmatter,
                        },
                    )
                )
                chunk_index += 1

    logger.info(f"Chunked {content_path} into {len(chunks)} chunks")
    return chunks
