"""Unit tests for file_utils module."""

import tempfile
from pathlib import Path

import pytest

from scripts.common.file_utils import (
    calculate_file_hash,
    find_markdown_files,
    get_relative_path,
)


def test_calculate_file_hash():
    """Test file hash calculation."""
    # Create a temporary file with known content
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Hello, World!")
        temp_file = Path(f.name)
    
    try:
        # Calculate hash
        hash_value = calculate_file_hash(temp_file)
        
        # Verify it's a valid hex string
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 produces 64 hex characters
        int(hash_value, 16)  # Should not raise ValueError
        
        # Same file should produce same hash
        hash_value2 = calculate_file_hash(temp_file)
        assert hash_value == hash_value2
    finally:
        temp_file.unlink()


def test_calculate_file_hash_different_content():
    """Test that different content produces different hashes."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f1:
        f1.write("Content A")
        file1 = Path(f1.name)
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f2:
        f2.write("Content B")
        file2 = Path(f2.name)
    
    try:
        hash1 = calculate_file_hash(file1)
        hash2 = calculate_file_hash(file2)
        
        assert hash1 != hash2
    finally:
        file1.unlink()
        file2.unlink()


def test_find_markdown_files():
    """Test finding markdown files in directory."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create some markdown files
        (tmp_path / "file1.md").write_text("# File 1")
        (tmp_path / "file2.md").write_text("# File 2")
        (tmp_path / "readme.txt").write_text("Not markdown")
        
        # Create subdirectory with markdown file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.md").write_text("# File 3")
        
        # Find all markdown files
        markdown_files = find_markdown_files(tmp_path)
        
        # Should find 3 markdown files
        assert len(markdown_files) == 3
        
        # Verify they are all .md files
        for file in markdown_files:
            assert file.suffix == ".md"
            assert file.is_file()


def test_find_markdown_files_with_pattern():
    """Test finding markdown files with custom pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create files in subdirectories
        (tmp_path / "root.md").write_text("# Root")
        
        subdir1 = tmp_path / "docs"
        subdir1.mkdir()
        (subdir1 / "doc1.md").write_text("# Doc 1")
        
        subdir2 = tmp_path / "guides"
        subdir2.mkdir()
        (subdir2 / "guide1.md").write_text("# Guide 1")
        
        # Find only in docs directory
        docs_files = find_markdown_files(tmp_path, pattern="docs/**/*.md")
        
        assert len(docs_files) == 1
        assert docs_files[0].name == "doc1.md"


def test_find_markdown_files_nonexistent_dir():
    """Test finding files in nonexistent directory."""
    nonexistent = Path("/nonexistent/directory")
    
    with pytest.raises(FileNotFoundError):
        find_markdown_files(nonexistent)


def test_find_markdown_files_not_a_directory():
    """Test finding files when path is not a directory."""
    with tempfile.NamedTemporaryFile() as f:
        file_path = Path(f.name)
        
        with pytest.raises(NotADirectoryError):
            find_markdown_files(file_path)


def test_get_relative_path():
    """Test getting relative path from base directory."""
    base_dir = Path("/home/user/project")
    file_path = Path("/home/user/project/content/docs/file.md")
    
    rel_path = get_relative_path(file_path, base_dir)
    
    assert rel_path == "content/docs/file.md"
    assert "/" in rel_path  # Uses forward slashes


def test_get_relative_path_not_relative():
    """Test getting relative path when file is not under base dir."""
    base_dir = Path("/home/user/project")
    file_path = Path("/other/location/file.md")
    
    # Should return absolute path if not relative
    rel_path = get_relative_path(file_path, base_dir)
    
    assert str(file_path) in rel_path
