"""
Chunking comparison tests - Python vs TypeScript.

Verifies that Python chunking matches TypeScript chunking.
"""

import pytest
import os

from app.services.rag.chunker import chunk_text, count_tokens
from app.services.rag.types import ChunkingOptions


# Sample markdown content (similar to actual content files)
SAMPLE_MARKDOWN_1 = """## PADI Open Water Certification

PADI Open Water Diver is the first scuba certification level. It allows you to dive to 18 meters (60 feet).

### Requirements

- Minimum age: 10 years
- Basic swimming skills
- Medical clearance

### Course Duration

The course typically takes 3-4 days and includes:

1. Knowledge development (online or classroom)
2. Confined water dives (pool)
3. Open water dives (4 dives)

## Course Content

You will learn essential diving skills including:

- Buoyancy control
- Underwater navigation
- Equipment management
- Safety procedures
"""

SAMPLE_MARKDOWN_2 = """## Tioman Island Dive Sites

Tioman Island offers diverse dive sites for all levels.

### Beginner Sites

**Renggis Island**: Shallow coral gardens, perfect for new divers. Depth: 5-12m.

**Malang Rocks**: Easy drift dive with good visibility. Depth: 8-15m.

### Advanced Sites

**Tiger Reef**: Strong currents, large pelagics. Depth: 18-30m.

Requires Advanced Open Water certification.
"""


class TestChunkingComparison:
    """Test chunking to verify consistency with TypeScript implementation."""

    def test_token_counting_consistency(self):
        """Test that token counting is consistent."""
        texts = [
            "Hello world",
            "What is PADI Open Water?",
            "This is a longer text with multiple sentences. It should have more tokens.",
            SAMPLE_MARKDOWN_1[:200],
        ]

        for text in texts:
            count = count_tokens(text)
            assert count > 0
            # Rough check: 4 chars per token on average
            expected_range = (len(text) // 6, len(text) // 2)
            assert expected_range[0] <= count <= expected_range[1]

    def test_chunk_small_document(self):
        """Test chunking small document (fits in one chunk)."""
        text = "## Small Section\n\nThis is a small document."
        
        chunks = chunk_text(text, "test.md")
        
        assert len(chunks) == 1
        assert "## Small Section" in chunks[0].text
        assert chunks[0].metadata["content_path"] == "test.md"
        assert chunks[0].metadata["chunk_index"] == 0

    def test_chunk_with_multiple_sections(self):
        """Test chunking document with multiple sections."""
        chunks = chunk_text(SAMPLE_MARKDOWN_1, "padi-ow.md")
        
        # Should produce multiple chunks
        assert len(chunks) >= 2
        
        # Check that section headers are preserved
        headers_found = []
        for chunk in chunks:
            if "##" in chunk.text:
                headers_found.append(True)
        
        assert any(headers_found)
        
        # Check chunk indices are sequential
        indices = [c.metadata["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_chunk_boundaries_deterministic(self):
        """Test that chunking is deterministic."""
        options = ChunkingOptions(target_tokens=200, max_tokens=300)
        
        chunks1 = chunk_text(SAMPLE_MARKDOWN_2, "tioman.md", options=options)
        chunks2 = chunk_text(SAMPLE_MARKDOWN_2, "tioman.md", options=options)
        
        # Same input should produce same chunks
        assert len(chunks1) == len(chunks2)
        for c1, c2 in zip(chunks1, chunks2):
            assert c1.text == c2.text
            assert c1.metadata["chunk_index"] == c2.metadata["chunk_index"]

    def test_chunk_preserves_markdown_structure(self):
        """Test that markdown structure is preserved in chunks."""
        chunks = chunk_text(SAMPLE_MARKDOWN_2, "tioman.md")
        
        # Check that headers are included with their content
        for chunk in chunks:
            # If chunk has a list, it should have the header too
            if "**Renggis Island**" in chunk.text or "**Malang Rocks**" in chunk.text:
                assert "##" in chunk.text  # Should have section header
            
            # If chunk has multiple paragraphs, they should be properly separated
            if "\n\n" in chunk.text:
                paragraphs = chunk.text.split("\n\n")
                assert all(p.strip() for p in paragraphs)  # No empty paragraphs

    def test_chunk_token_limits_respected(self):
        """Test that chunks respect token limits."""
        options = ChunkingOptions(target_tokens=100, max_tokens=150)
        
        chunks = chunk_text(SAMPLE_MARKDOWN_1, "test.md", options=options)
        
        # Most chunks should be under max_tokens
        for chunk in chunks:
            token_count = count_tokens(chunk.text)
            # Allow some overflow for cases where single paragraph is too large
            assert token_count <= options.max_tokens * 1.5

    def test_chunk_with_frontmatter(self):
        """Test that frontmatter metadata is included."""
        frontmatter = {
            "doc_type": "certification",
            "tags": ["padi", "beginner"],
            "destination": None,
        }
        
        chunks = chunk_text(SAMPLE_MARKDOWN_1, "padi-ow.md", frontmatter=frontmatter)
        
        for chunk in chunks:
            assert chunk.metadata["doc_type"] == "certification"
            assert chunk.metadata["tags"] == ["padi", "beginner"]

    def test_chunk_comparison_metrics(self):
        """Generate metrics for comparison with TypeScript."""
        options = ChunkingOptions(target_tokens=650, max_tokens=800, overlap_tokens=50)
        
        test_docs = [
            ("sample1.md", SAMPLE_MARKDOWN_1),
            ("sample2.md", SAMPLE_MARKDOWN_2),
        ]
        
        print("\n=== Python Chunking Metrics ===")
        for doc_path, content in test_docs:
            chunks = chunk_text(content, doc_path, options=options)
            
            print(f"\nDocument: {doc_path}")
            print(f"Total chunks: {len(chunks)}")
            print(f"Chunk sizes (tokens): {[count_tokens(c.text) for c in chunks]}")
            print(f"First chunk preview: {chunks[0].text[:100]}...")
            
            if len(chunks) > 1:
                print(f"Last chunk preview: {chunks[-1].text[:100]}...")


# Manual comparison instructions
"""
To compare with TypeScript chunking:

1. Generate TypeScript chunks:
   cd /path/to/project
   pnpm tsx scripts/test-chunking.ts

2. Compare outputs:
   - Number of chunks
   - Chunk boundaries (where splits occur)
   - Token counts per chunk
   - Section header preservation

Acceptance criteria:
- ≥90% chunk boundary match
- Token counts within 5% tolerance
"""
