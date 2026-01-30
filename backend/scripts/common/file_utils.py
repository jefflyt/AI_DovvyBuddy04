"""File utilities for content processing scripts."""

import hashlib
from pathlib import Path
from typing import List


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def find_markdown_files(content_dir: Path, pattern: str = "**/*.md") -> List[Path]:
    """Find all markdown files in a directory.
    
    Args:
        content_dir: Root content directory
        pattern: Glob pattern for matching files (default: **/*.md)
        
    Returns:
        List of Path objects for markdown files
    """
    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory not found: {content_dir}")
    
    if not content_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {content_dir}")
    
    markdown_files = sorted(content_dir.glob(pattern))
    return [f for f in markdown_files if f.is_file()]


def get_relative_path(file_path: Path, base_dir: Path) -> str:
    """Get relative path from base directory.
    
    Args:
        file_path: Absolute file path
        base_dir: Base directory
        
    Returns:
        Relative path as string with forward slashes
    """
    try:
        rel_path = file_path.relative_to(base_dir)
        # Use forward slashes for cross-platform compatibility
        return str(rel_path).replace("\\", "/")
    except ValueError:
        # If file_path is not relative to base_dir, return absolute path
        return str(file_path)
