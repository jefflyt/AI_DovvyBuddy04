"""Integration tests for ingestion workflow using in-memory test doubles."""

from __future__ import annotations

import math
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from scripts.ingest_content import ingest_file


class InMemoryRAGRepository:
    """Lightweight in-memory substitute for ingestion workflow tests."""

    def __init__(self):
        self._rows: List[Dict[str, Any]] = []
        self._next_id = 1

    def insert_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        for chunk in chunks:
            self._rows.append(
                {
                    "id": self._next_id,
                    "text": chunk["text"],
                    "embedding": chunk["embedding"],
                    "metadata": chunk.get("metadata", {}),
                }
            )
            self._next_id += 1

    def delete_by_content_path(self, content_path: str) -> int:
        before = len(self._rows)
        self._rows = [
            row
            for row in self._rows
            if row.get("metadata", {}).get("content_path") != content_path
        ]
        return before - len(self._rows)

    def delete_all(self) -> int:
        count = len(self._rows)
        self._rows = []
        return count

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._rows)

    def search_by_metadata(self, metadata_filter: Dict[str, Any], limit: int = 10):
        matches = []
        for row in self._rows:
            metadata = row.get("metadata", {})
            if all(str(metadata.get(k)) == str(v) for k, v in metadata_filter.items()):
                matches.append(row)
            if len(matches) >= limit:
                break
        return matches

    def search_by_similarity(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        scored = []
        for row in self._rows:
            similarity = self._cosine_similarity(query_embedding, row["embedding"])
            if similarity >= similarity_threshold:
                scored.append(
                    {
                        "id": row["id"],
                        "text": row["text"],
                        "metadata": row["metadata"],
                        "similarity": similarity,
                    }
                )
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
        norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (norm_a * norm_b)


class FakeEmbeddingProvider:
    """Deterministic embedding provider for offline test execution."""

    def __init__(self, dim: int = 12):
        self.dim = dim

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dim
        text = text or ""
        for i, ch in enumerate(text):
            vector[i % self.dim] += (ord(ch) % 31) / 31.0
        length_norm = max(1.0, len(text) / 32.0)
        return [v / length_norm for v in vector]


@pytest.fixture
def repository():
    return InMemoryRAGRepository()


@pytest.fixture
def embedding_provider():
    return FakeEmbeddingProvider()


@pytest.fixture
def test_content_dir():
    """Create a temporary content directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        file1 = tmp_path / "guide1.md"
        file1.write_text(
            """---
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
"""
        )

        file2 = tmp_path / "advanced.md"
        file2.write_text(
            """---
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
"""
        )

        yield tmp_path


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_ingestion_workflow(
    repository: InMemoryRAGRepository,
    embedding_provider: FakeEmbeddingProvider,
    test_content_dir: Path,
):
    repository.delete_all()

    test_files = list(test_content_dir.glob("*.md"))
    assert len(test_files) == 2

    file1 = test_files[0]
    result1 = await ingest_file(
        file1,
        test_content_dir,
        embedding_provider,
        repository,
        incremental=False,
        dry_run=False,
    )

    assert result1["skipped"] is False
    assert result1["chunks_created"] > 0
    assert result1.get("error") is None

    all_embeddings = repository.get_all()
    assert len(all_embeddings) == result1["chunks_created"]
    first_embedding = all_embeddings[0]
    assert "metadata" in first_embedding
    assert "content_path" in first_embedding["metadata"]
    assert "file_hash" in first_embedding["metadata"]

    file2 = test_files[1]
    result2 = await ingest_file(
        file2,
        test_content_dir,
        embedding_provider,
        repository,
        incremental=False,
        dry_run=False,
    )

    assert result2["skipped"] is False
    assert result2["chunks_created"] > 0

    all_embeddings = repository.get_all()
    expected_total = result1["chunks_created"] + result2["chunks_created"]
    assert len(all_embeddings) == expected_total


@pytest.mark.integration
@pytest.mark.asyncio
async def test_incremental_ingestion(
    repository: InMemoryRAGRepository,
    embedding_provider: FakeEmbeddingProvider,
    test_content_dir: Path,
):
    repository.delete_all()
    test_file = list(test_content_dir.glob("*.md"))[0]

    result1 = await ingest_file(
        test_file,
        test_content_dir,
        embedding_provider,
        repository,
        incremental=True,
        dry_run=False,
    )
    assert result1["skipped"] is False
    chunks_created = result1["chunks_created"]
    assert chunks_created > 0

    result2 = await ingest_file(
        test_file,
        test_content_dir,
        embedding_provider,
        repository,
        incremental=True,
        dry_run=False,
    )
    assert result2["skipped"] is True
    assert result2["chunks_created"] == 0

    all_embeddings = repository.get_all()
    assert len(all_embeddings) == chunks_created


@pytest.mark.integration
@pytest.mark.asyncio
async def test_re_ingestion_replaces_chunks(
    repository: InMemoryRAGRepository,
    embedding_provider: FakeEmbeddingProvider,
    test_content_dir: Path,
):
    repository.delete_all()
    test_file = list(test_content_dir.glob("*.md"))[0]

    result1 = await ingest_file(
        test_file,
        test_content_dir,
        embedding_provider,
        repository,
        incremental=False,
        dry_run=False,
    )
    chunks_created_first = result1["chunks_created"]

    original_content = test_file.read_text()
    test_file.write_text(original_content + "\n\n## New Section\n\nAdditional content added.")

    result2 = await ingest_file(
        test_file,
        test_content_dir,
        embedding_provider,
        repository,
        incremental=False,
        dry_run=False,
    )

    assert result2["skipped"] is False
    assert result2["chunks_deleted"] == chunks_created_first
    assert result2["chunks_created"] > 0

    all_embeddings = repository.get_all()
    assert len(all_embeddings) == result2["chunks_created"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_after_ingestion(
    repository: InMemoryRAGRepository,
    embedding_provider: FakeEmbeddingProvider,
    test_content_dir: Path,
):
    repository.delete_all()

    for test_file in test_content_dir.glob("*.md"):
        await ingest_file(
            test_file,
            test_content_dir,
            embedding_provider,
            repository,
            incremental=False,
            dry_run=False,
        )

    query = "What equipment do I need for diving?"
    query_embedding = (await embedding_provider.embed_batch([query]))[0]
    results = repository.search_by_similarity(query_embedding, top_k=5)

    assert len(results) > 0
    for result in results:
        assert "text" in result
        assert "metadata" in result
        assert "similarity" in result
        assert result["similarity"] >= 0

