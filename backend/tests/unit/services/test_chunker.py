"""
Unit tests for text chunking.

Tests chunking logic with various markdown inputs.
"""

import pytest

from app.services.rag.chunker import (
    chunk_text,
    count_tokens,
    split_into_paragraphs,
    split_into_sections,
)
from app.services.rag.types import ChunkingOptions


class TestTokenCounting:
    """Test token counting."""

    def test_count_tokens_simple(self):
        """Test token counting for simple text."""
        text = "Hello world"
        count = count_tokens(text)
        assert count > 0
        assert count < 10  # Rough approximation

    def test_count_tokens_empty(self):
        """Test token counting for empty text."""
        assert count_tokens("") == 0

    def test_count_tokens_long_text(self):
        """Test token counting for longer text."""
        text = "This is a longer text " * 100
        count = count_tokens(text)
        assert count > 100


class TestSectionSplitting:
    """Test section splitting."""

    def test_split_simple_sections(self):
        """Test splitting text with simple headers."""
        text = """## Section 1
Content 1

## Section 2
Content 2"""

        sections = split_into_sections(text)

        assert len(sections) == 2
        assert sections[0]["header"] == "## Section 1"
        assert "Content 1" in sections[0]["content"]
        assert sections[1]["header"] == "## Section 2"
        assert "Content 2" in sections[1]["content"]

    def test_split_nested_headers(self):
        """Test splitting with nested headers."""
        text = """## Main Section
Intro

### Subsection
Details"""

        sections = split_into_sections(text)

        assert len(sections) == 2
        assert sections[0]["header"] == "## Main Section"
        assert sections[1]["header"] == "### Subsection"

    def test_split_no_headers(self):
        """Test splitting text without headers."""
        text = "Just some content\nwithout headers"

        sections = split_into_sections(text)

        assert len(sections) == 1
        assert sections[0]["header"] == ""
        assert "Just some content" in sections[0]["content"]


class TestParagraphSplitting:
    """Test paragraph splitting."""

    def test_split_paragraphs(self):
        """Test splitting into paragraphs."""
        text = """First paragraph.

Second paragraph.

Third paragraph."""

        paragraphs = split_into_paragraphs(text)

        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."

    def test_split_single_paragraph(self):
        """Test single paragraph."""
        text = "Just one paragraph"

        paragraphs = split_into_paragraphs(text)

        assert len(paragraphs) == 1
        assert paragraphs[0] == "Just one paragraph"

    def test_split_empty_text(self):
        """Test empty text."""
        paragraphs = split_into_paragraphs("")
        assert len(paragraphs) == 0


class TestChunking:
    """Test text chunking."""

    def test_chunk_small_text(self):
        """Test chunking text that fits in one chunk."""
        text = "## Small Section\n\nThis is a small text that fits in one chunk."
        options = ChunkingOptions(target_tokens=500, max_tokens=800)

        chunks = chunk_text(text, "test.md", {}, options)

        assert len(chunks) == 1
        assert chunks[0].text == text.strip()
        assert chunks[0].metadata["content_path"] == "test.md"
        assert chunks[0].metadata["chunk_index"] == 0

    def test_chunk_multiple_sections(self):
        """Test chunking text with multiple sections."""
        text = """## Section 1
Content for section 1.

## Section 2
Content for section 2.

## Section 3
Content for section 3."""

        options = ChunkingOptions(target_tokens=50, max_tokens=100)
        chunks = chunk_text(text, "test.md", {}, options)

        assert len(chunks) >= 3
        assert all("## Section" in chunk.text for chunk in chunks)

    def test_chunk_with_frontmatter(self):
        """Test chunking with frontmatter metadata."""
        text = "## Test\n\nContent"
        frontmatter = {"doc_type": "faq", "tags": ["diving", "safety"]}

        chunks = chunk_text(text, "test.md", frontmatter)

        assert len(chunks) == 1
        assert chunks[0].metadata["doc_type"] == "faq"
        assert chunks[0].metadata["tags"] == ["diving", "safety"]

    def test_chunk_preserves_section_headers(self):
        """Test that section headers are preserved in chunks."""
        text = """## Important Section

This is important content that should keep its header."""

        chunks = chunk_text(text, "test.md")

        assert len(chunks) == 1
        assert "## Important Section" in chunks[0].text
        assert chunks[0].metadata["section_header"] == "## Important Section"

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunks = chunk_text("", "test.md")
        assert len(chunks) == 0

    def test_chunk_index_increments(self):
        """Test that chunk indices increment correctly."""
        text = """## Section 1
Content 1

## Section 2
Content 2

## Section 3
Content 3"""

        options = ChunkingOptions(target_tokens=50, max_tokens=100)
        chunks = chunk_text(text, "test.md", {}, options)

        # Check that chunk indices are sequential
        indices = [chunk.metadata["chunk_index"] for chunk in chunks]
        assert indices == list(range(len(chunks)))
