"""Integration tests for full content ingestion workflow."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.chunking import ChunkingService, EmbeddingService
from app.services.rag.repository import RAGRepository
from scripts.ingest_content import ingest_file


@pytest.fixture
def test_db():
    """Provide a test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_content_dir():
    """Create a temporary content directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create test markdown files
        file1 = tmp_path / "guide1.md"
        file1.write_text("""---
title: Beginner's Guide to Scuba Diving
description: Complete guide for diving beginners
tags:
  - beginner
  - guide
category: education
---

# Introduction to Scuba Diving

Scuba diving is an exciting underwater activity. This guide will help you get started.

## Equipment Overview

Essential equipment includes:
- Mask
- Fins
- Regulator
- BCD (Buoyancy Control Device)

## Safety Considerations

Always dive with a buddy and follow proper safety protocols.
""")
        
        file2 = tmp_path / "advanced.md"
        file2.write_text("""---
title: Advanced Diving Techniques
description: Techniques for experienced divers
tags:
  - advanced
  - techniques
category: education
---

# Advanced Diving

For experienced divers looking to improve their skills.

## Deep Diving

Proper planning is essential for deep dives beyond 30 meters.
""")
        
        yield tmp_path


@pytest.mark.integration
def test_full_ingestion_workflow(test_db: Session, test_content_dir: Path):
    """Test complete ingestion workflow from files to database."""
    # Initialize services
    chunking_service = ChunkingService()
    embedding_service = EmbeddingService()
    repository = RAGRepository(test_db)
    
    # Clear any existing test data
    repository.delete_all()
    
    # Get test files
    test_files = list(test_content_dir.glob("*.md"))
    assert len(test_files) == 2
    
    # Ingest first file
    file1 = test_files[0]
    result1 = ingest_file(
        file1,
        test_content_dir,
        chunking_service,
        embedding_service,
        repository,
        incremental=False,
        dry_run=False,
    )
    
    assert result1["skipped"] is False
    assert result1["chunks_created"] > 0
    assert result1.get("error") is None
    
    # Verify embeddings were inserted
    all_embeddings = repository.get_all()
    assert len(all_embeddings) == result1["chunks_created"]
    
    # Verify metadata
    first_embedding = all_embeddings[0]
    assert "metadata" in first_embedding
    assert "content_path" in first_embedding["metadata"]
    assert "file_hash" in first_embedding["metadata"]
    
    # Ingest second file
    file2 = test_files[1]
    result2 = ingest_file(
        file2,
        test_content_dir,
        chunking_service,
        embedding_service,
        repository,
        incremental=False,
        dry_run=False,
    )
    
    assert result2["skipped"] is False
    assert result2["chunks_created"] > 0
    
    # Verify total count
    all_embeddings = repository.get_all()
    expected_total = result1["chunks_created"] + result2["chunks_created"]
    assert len(all_embeddings) == expected_total


@pytest.mark.integration
def test_incremental_ingestion(test_db: Session, test_content_dir: Path):
    """Test incremental ingestion skips unchanged files."""
    # Initialize services
    chunking_service = ChunkingService()
    embedding_service = EmbeddingService()
    repository = RAGRepository(test_db)
    
    # Clear existing data
    repository.delete_all()
    
    test_file = list(test_content_dir.glob("*.md"))[0]
    
    # First ingestion
    result1 = ingest_file(
        test_file,
        test_content_dir,
        chunking_service,
        embedding_service,
        repository,
        incremental=True,
        dry_run=False,
    )
    
    assert result1["skipped"] is False
    chunks_created = result1["chunks_created"]
    assert chunks_created > 0
    
    # Second ingestion (file unchanged)
    result2 = ingest_file(
        test_file,
        test_content_dir,
        chunking_service,
        embedding_service,
        repository,
        incremental=True,
        dry_run=False,
    )
    
    # Should be skipped
    assert result2["skipped"] is True
    assert result2["chunks_created"] == 0
    
    # Total count should remain the same
    all_embeddings = repository.get_all()
    assert len(all_embeddings) == chunks_created


@pytest.mark.integration
def test_re_ingestion_replaces_chunks(test_db: Session, test_content_dir: Path):
    """Test that re-ingesting a file replaces old chunks."""
    # Initialize services
    chunking_service = ChunkingService()
    embedding_service = EmbeddingService()
    repository = RAGRepository(test_db)
    
    # Clear existing data
    repository.delete_all()
    
    test_file = list(test_content_dir.glob("*.md"))[0]
    
    # First ingestion
    result1 = ingest_file(
        test_file,
        test_content_dir,
        chunking_service,
        embedding_service,
        repository,
        incremental=False,
        dry_run=False,
    )
    
    chunks_created_first = result1["chunks_created"]
    
    # Modify the file
    original_content = test_file.read_text()
    modified_content = original_content + "\n\n## New Section\n\nAdditional content added."
    test_file.write_text(modified_content)
    
    # Re-ingest
    result2 = ingest_file(
        test_file,
        test_content_dir,
        chunking_service,
        embedding_service,
        repository,
        incremental=False,
        dry_run=False,
    )
    
    assert result2["skipped"] is False
    assert result2["chunks_deleted"] == chunks_created_first
    assert result2["chunks_created"] > 0
    
    # Total count should reflect new chunks only
    all_embeddings = repository.get_all()
    assert len(all_embeddings) == result2["chunks_created"]


@pytest.mark.integration
def test_search_after_ingestion(test_db: Session, test_content_dir: Path):
    """Test that ingested content is searchable."""
    # Initialize services
    chunking_service = ChunkingService()
    embedding_service = EmbeddingService()
    repository = RAGRepository(test_db)
    
    # Clear existing data
    repository.delete_all()
    
    # Ingest all test files
    for test_file in test_content_dir.glob("*.md"):
        ingest_file(
            test_file,
            test_content_dir,
            chunking_service,
            embedding_service,
            repository,
            incremental=False,
            dry_run=False,
        )
    
    # Generate query embedding
    query = "What equipment do I need for diving?"
    query_embedding = embedding_service.generate_embeddings([query])[0]
    
    # Search
    results = repository.search_by_similarity(query_embedding, top_k=5)
    
    assert len(results) > 0
    
    # Verify results have expected structure
    for result in results:
        assert "text" in result
        assert "metadata" in result
        assert "similarity" in result
        assert result["similarity"] >= 0
