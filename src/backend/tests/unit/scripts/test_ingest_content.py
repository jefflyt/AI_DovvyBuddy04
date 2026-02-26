"""Unit tests for ingest_content script."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.ingest_content import (
    delete_existing_chunks,
    get_stored_file_hash,
    ingest_file,
    IngestionStats,
)


def test_ingestion_stats():
    """Test IngestionStats tracking."""
    stats = IngestionStats()
    
    assert stats.files_processed == 0
    assert stats.files_skipped == 0
    assert stats.chunks_created == 0
    assert stats.errors == 0
    
    stats.files_processed = 5
    stats.chunks_created = 42
    stats.errors = 1
    
    assert stats.files_processed == 5
    assert stats.chunks_created == 42
    assert stats.errors == 1
    
    elapsed = stats.elapsed_time()
    assert elapsed >= 0


def test_get_stored_file_hash_found():
    """Test getting stored file hash when it exists."""
    mock_repository = MagicMock()
    mock_repository.search_by_metadata.return_value = [
        {
            "metadata": {
                "content_path": "test/file.md",
                "file_hash": "abc123",
            }
        }
    ]
    
    result = get_stored_file_hash(mock_repository, "test/file.md")
    
    assert result == "abc123"
    mock_repository.search_by_metadata.assert_called_once()


def test_get_stored_file_hash_not_found():
    """Test getting stored file hash when it doesn't exist."""
    mock_repository = MagicMock()
    mock_repository.search_by_metadata.return_value = []
    
    result = get_stored_file_hash(mock_repository, "test/file.md")
    
    assert result is None


def test_delete_existing_chunks():
    """Test deleting existing chunks."""
    mock_repository = MagicMock()
    mock_repository.delete_by_content_path.return_value = 5
    
    count = delete_existing_chunks(mock_repository, "test/file.md")
    
    assert count == 5
    mock_repository.delete_by_content_path.assert_called_once_with("test/file.md")


@patch("scripts.ingest_content.calculate_file_hash")
@patch("scripts.ingest_content.parse_markdown")
@patch("scripts.ingest_content.chunk_text")
def test_ingest_file_success(mock_chunk_text, mock_parse, mock_hash):
    """Test successful file ingestion."""
    # Setup mocks
    mock_hash.return_value = "file_hash_123"
    mock_parse.return_value = {
        "frontmatter": {
            "title": "Test",
            "description": "Test doc",
            "tags": ["test"],
        },
        "content": "# Test\n\nContent here.",
    }
    
    mock_chunk_text.return_value = [
        MagicMock(text="Chunk 1", metadata={}),
        MagicMock(text="Chunk 2", metadata={}),
    ]

    mock_embedding = MagicMock()
    mock_embedding.embed_batch = AsyncMock(return_value=[
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ])
    
    mock_repository = MagicMock()
    mock_repository.delete_by_content_path.return_value = 0
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("# Test\n\nContent")
        temp_file = Path(f.name)
    
    try:
        result = asyncio.run(ingest_file(
            temp_file,
            temp_file.parent,
            mock_embedding,
            mock_repository,
            incremental=False,
            dry_run=False,
        ))
        
        assert result["skipped"] is False
        assert result["chunks_created"] == 2
        assert result["embeddings_generated"] == 2
        
        mock_chunk_text.assert_called_once()
        mock_embedding.embed_batch.assert_awaited_once()
        mock_repository.insert_chunks.assert_called_once()
    finally:
        temp_file.unlink()


@patch("scripts.ingest_content.calculate_file_hash")
@patch("scripts.ingest_content.get_stored_file_hash")
def test_ingest_file_incremental_skip(mock_get_hash, mock_calc_hash):
    """Test incremental ingestion skips unchanged files."""
    # Setup mocks - same hash
    mock_calc_hash.return_value = "same_hash"
    mock_get_hash.return_value = "same_hash"
    
    mock_embedding = MagicMock()
    mock_repository = MagicMock()
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("# Test\n\nContent")
        temp_file = Path(f.name)
    
    try:
        result = asyncio.run(ingest_file(
            temp_file,
            temp_file.parent,
            mock_embedding,
            mock_repository,
            incremental=True,
            dry_run=False,
        ))
        
        assert result["skipped"] is True
        assert result["chunks_created"] == 0
        
        # Should not call chunking or embedding services
        mock_embedding.embed_batch.assert_not_called()
    finally:
        temp_file.unlink()


@patch("scripts.ingest_content.calculate_file_hash")
@patch("scripts.ingest_content.parse_markdown")
@patch("scripts.ingest_content.chunk_text")
def test_ingest_file_dry_run(mock_chunk_text, mock_parse, mock_hash):
    """Test dry run mode doesn't write to database."""
    # Setup mocks
    mock_hash.return_value = "file_hash"
    mock_parse.return_value = {
        "frontmatter": {"title": "Test", "description": "Test"},
        "content": "Content",
    }
    
    mock_chunk_text.return_value = [MagicMock(text="Chunk", metadata={})]
    
    mock_embedding = MagicMock()
    mock_embedding.embed_batch = AsyncMock(return_value=[[0.1, 0.2]])
    
    mock_repository = MagicMock()
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("# Test")
        temp_file = Path(f.name)
    
    try:
        result = asyncio.run(ingest_file(
            temp_file,
            temp_file.parent,
            mock_embedding,
            mock_repository,
            incremental=False,
            dry_run=True,
        ))
        
        assert result["chunks_created"] == 1
        
        # Should not write to database
        mock_repository.delete_by_content_path.assert_not_called()
        mock_repository.insert_chunks.assert_not_called()
    finally:
        temp_file.unlink()
