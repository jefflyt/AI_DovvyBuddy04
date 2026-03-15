"""Content ingestion script.

Ingests markdown content files by:
- Reading and parsing markdown
- Chunking text using RAG chunker
- Generating embeddings
- Inserting into database
- Supporting incremental mode (skip unchanged files)
"""

import argparse
import asyncio
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Optional

from app.core.config import settings
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.services.embeddings import create_embedding_provider_from_env
from app.infrastructure.services.rag import chunk_text
from app.infrastructure.services.rag.types import ChunkingOptions
from app.infrastructure.services.rag.repository import RAGRepository
from scripts.common import (
    calculate_file_hash,
    confirm,
    error,
    find_markdown_files,
    FrontmatterError,
    get_relative_path,
    info,
    MarkdownParseError,
    parse_markdown,
    progress_bar,
    success,
    warning,
)


class IngestionStats:
    """Statistics for ingestion run."""
    
    def __init__(self):
        """Initialize statistics."""
        self.files_processed = 0
        self.files_skipped = 0
        self.chunks_created = 0
        self.chunks_deleted = 0
        self.embeddings_generated = 0
        self.errors = 0
        self.start_time = time.time()
    
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    def print_summary(self):
        """Print statistics summary."""
        elapsed = self.elapsed_time()
        print()
        success(f"Ingestion completed in {elapsed:.2f}s")
        info(f"  Files processed: {self.files_processed}")
        if self.files_skipped > 0:
            info(f"  Files skipped (unchanged): {self.files_skipped}")
        info(f"  Chunks created: {self.chunks_created}")
        if self.chunks_deleted > 0:
            info(f"  Chunks deleted (replaced): {self.chunks_deleted}")
        info(f"  Embeddings generated: {self.embeddings_generated}")
        if self.errors > 0:
            warning(f"  Errors: {self.errors}")


def _normalize_frontmatter_value(value):
    """Convert frontmatter values to JSON-serializable primitives."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (date, datetime)):
        return str(value)
    if isinstance(value, list):
        return [_normalize_frontmatter_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _normalize_frontmatter_value(v) for k, v in value.items()}
    return str(value)


def get_stored_file_hash(
    repository: RAGRepository,
    content_path: str,
) -> Optional[str]:
    """Get stored file hash from database metadata.
    
    Args:
        repository: RAG repository
        content_path: Relative content path
        
    Returns:
        File hash if found, None otherwise
    """
    # Query first chunk for this file to get metadata
    chunks = repository.search_by_metadata({"content_path": content_path}, limit=1)
    
    if not chunks:
        return None
    
    metadata = chunks[0].get("metadata", {})
    return metadata.get("file_hash")


def delete_existing_chunks(
    repository: RAGRepository,
    content_path: str,
) -> int:
    """Delete existing chunks for a content file.
    
    Args:
        repository: RAG repository
        content_path: Relative content path
        
    Returns:
        Number of chunks deleted
    """
    return repository.delete_by_content_path(content_path)


async def ingest_file(
    file_path: Path,
    content_dir: Path,
    embedding_provider,
    repository: RAGRepository,
    incremental: bool = False,
    dry_run: bool = False,
) -> Dict[str, any]:
    """Ingest a single markdown file.
    
    Args:
        file_path: Path to markdown file
        content_dir: Root content directory
        embedding_provider: Embedding provider (async)
        repository: RAG repository
        incremental: Enable incremental mode (check file hash)
        dry_run: Dry run mode (no database writes)
        
    Returns:
        Dictionary with ingestion results
    """
    rel_path = get_relative_path(file_path, content_dir)
    
    # Calculate file hash
    file_hash = calculate_file_hash(file_path)
    
    # Check if file changed (incremental mode)
    if incremental and not dry_run:
        stored_hash = get_stored_file_hash(repository, rel_path)
        if stored_hash == file_hash:
            return {
                "skipped": True,
                "chunks_created": 0,
                "chunks_deleted": 0,
            }
    
    # Parse markdown
    try:
        parsed = parse_markdown(file_path)
    except (MarkdownParseError, FrontmatterError) as e:
        return {
            "error": str(e),
            "skipped": False,
        }
    
    frontmatter = parsed["frontmatter"]
    content = parsed["content"]
    
    # Preserve filterable frontmatter metadata used by retrieval filters.
    frontmatter_metadata = {
        key: _normalize_frontmatter_value(value)
        for key, value in frontmatter.items()
    }

    # Prepare metadata
    metadata = {
        "content_path": rel_path,
        "file_hash": file_hash,
        **frontmatter_metadata,
        "title": frontmatter_metadata.get("title", ""),
        "description": frontmatter_metadata.get("description", ""),
        "tags": frontmatter_metadata.get("tags", []),
    }
    
    chunk_options = ChunkingOptions(
        target_tokens=max(50, int(settings.rag_chunk_size)),
        max_tokens=max(
            int(settings.rag_chunk_size),
            int(settings.rag_chunk_size) + max(0, int(settings.rag_chunk_overlap)),
        ),
        min_tokens=max(20, min(100, int(settings.rag_chunk_overlap))),
        overlap_tokens=max(0, int(settings.rag_chunk_overlap)),
    )

    # Chunk text using configured RAG chunk settings.
    chunk_objects = chunk_text(
        content,
        rel_path,
        frontmatter=metadata,
        options=chunk_options,
    )
    
    if not chunk_objects:
        return {
            "error": "No chunks generated (content too short?)",
            "skipped": False,
        }
    
    # Convert to dictionaries
    chunks = [
        {
            "text": chunk.text,
            "metadata": chunk.metadata,
        }
        for chunk in chunk_objects
    ]
    
    # Generate embeddings (async)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = await embedding_provider.embed_batch(texts)
    
    if len(embeddings) != len(chunks):
        return {
            "error": f"Embedding count mismatch: {len(embeddings)} != {len(chunks)}",
            "skipped": False,
        }
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
    
    chunks_deleted = 0
    
    if not dry_run:
        # Delete existing chunks
        chunks_deleted = delete_existing_chunks(repository, rel_path)
        
        # Insert new chunks
        repository.insert_chunks(chunks)
    
    return {
        "skipped": False,
        "chunks_created": len(chunks),
        "chunks_deleted": chunks_deleted,
        "embeddings_generated": len(embeddings),
    }


def main():
    """Main entry point for ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest content files into database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Incremental ingestion (default - skip unchanged files)
  python -m scripts.ingest_content
  
  # Full re-ingestion (ignore file hashes)
  python -m scripts.ingest_content --full
  
  # Dry run (preview without database writes)
  python -m scripts.ingest_content --dry-run
  
  # Clear existing embeddings first
  python -m scripts.ingest_content --clear
        """,
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=Path("../../content/source"),
        help="Content directory to ingest (default: ../../content/source)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.md",
        help="File pattern to match (default: **/*.md)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full re-ingestion mode (ignore file hashes, re-ingest all files)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (no database writes)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing embeddings before ingestion",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Embedding batch size (default: 10)",
    )
    
    args = parser.parse_args()
    
    # Resolve content directory
    content_dir = args.content_dir.resolve()
    
    if args.dry_run:
        warning("DRY RUN MODE: No database writes will be performed")
    
    info(f"Ingesting content from: {content_dir}")
    
    # Determine incremental mode (default: True, unless --full flag is set)
    incremental = not args.full
    if args.full:
        info("Full re-ingestion mode: will re-ingest all files")
    else:
        info("Incremental mode: will skip unchanged files (use --full to re-ingest all)")
    
    # Find markdown files
    try:
        markdown_files = find_markdown_files(content_dir, args.pattern)
    except (FileNotFoundError, NotADirectoryError) as e:
        error(str(e))
        sys.exit(1)
    
    if not markdown_files:
        warning(f"No markdown files found matching pattern: {args.pattern}")
        sys.exit(0)
    
    info(f"Found {len(markdown_files)} markdown file(s)")
    
    # Initialize services
    embedding_provider = create_embedding_provider_from_env()
    db = SessionLocal()
    try:
        repository = RAGRepository(db)
        
        # Clear existing embeddings if requested
        if args.clear and not args.dry_run:
            if not confirm("Clear all existing embeddings?", default=False):
                error("Aborted by user")
                sys.exit(1)
            
            deleted_count = repository.delete_all()
            success(f"Deleted {deleted_count} existing embedding(s)")
        
        # Ingest files
        stats = IngestionStats()
        
        with progress_bar(
            total=len(markdown_files),
            description="Ingesting content"
        ) as bar:
            for file_path in markdown_files:
                result = asyncio.run(ingest_file(
                    file_path,
                    content_dir,
                    embedding_provider,
                    repository,
                    incremental=incremental,
                    dry_run=args.dry_run,
                ))
                
                if result.get("error"):
                    rel_path = get_relative_path(file_path, content_dir)
                    error(f"{rel_path}: {result['error']}")
                    stats.errors += 1
                elif result.get("skipped"):
                    stats.files_skipped += 1
                else:
                    stats.files_processed += 1
                    stats.chunks_created += result.get("chunks_created", 0)
                    stats.chunks_deleted += result.get("chunks_deleted", 0)
                    stats.embeddings_generated += result.get("embeddings_generated", 0)
                
                bar.update()
        
        # Print summary
        stats.print_summary()
        
        # Exit with error if any errors occurred
        if stats.errors > 0:
            sys.exit(1)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
