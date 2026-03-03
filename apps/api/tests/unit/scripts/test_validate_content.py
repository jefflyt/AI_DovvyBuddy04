"""Unit tests for validate_content script."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.validate_content import validate_file, ValidationError


def test_validate_file_valid():
    """Test validating a valid markdown file."""
    content = """---
title: Test Document
description: A test document
---

# Test Heading

Some content here.
"""
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        is_valid, errors = validate_file(temp_file, required_fields=["title", "description"])
        
        assert is_valid
        assert errors == []
    finally:
        temp_file.unlink()


def test_validate_file_missing_frontmatter():
    """Test validating file with no frontmatter."""
    content = "# Just Content\n\nNo frontmatter here."
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        is_valid, errors = validate_file(temp_file, required_fields=["title"])
        
        assert not is_valid
        assert len(errors) > 0
        assert any("frontmatter" in str(e).lower() for e in errors)
    finally:
        temp_file.unlink()


def test_validate_file_missing_required_field():
    """Test validating file with missing required field."""
    content = """---
title: Test Document
---

# Content
"""
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        is_valid, errors = validate_file(
            temp_file,
            required_fields=["title", "description"]
        )
        
        assert not is_valid
        assert len(errors) >= 1
        assert any("description" in str(e) for e in errors)
    finally:
        temp_file.unlink()


def test_validate_file_structure_warnings():
    """Test validating file with structure issues."""
    content = """---
title: Test
description: Test
---

# Heading 1
## Heading 2

Content between headings is missing above.
"""
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        is_valid, errors = validate_file(
            temp_file,
            required_fields=["title", "description"],
            check_structure=True
        )
        
        # Structure warnings should be reported as errors
        assert not is_valid
        assert any("consecutive" in str(e).lower() for e in errors)
    finally:
        temp_file.unlink()


def test_validate_file_skip_structure_check():
    """Test validating file while skipping structure check."""
    content = """---
title: Test
description: Test
---

# Heading 1
## Heading 2
"""
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        is_valid, errors = validate_file(
            temp_file,
            required_fields=["title", "description"],
            check_structure=False
        )
        
        # Should be valid when structure check is skipped
        assert is_valid
        assert errors == []
    finally:
        temp_file.unlink()


def test_validation_error_string_representation():
    """Test ValidationError string representation."""
    error = ValidationError(Path("/path/to/file.md"), "Test error message", line=42)
    
    error_str = str(error)
    
    assert "/path/to/file.md" in error_str
    assert ":42" in error_str
    assert "Test error message" in error_str


def test_validation_error_no_line_number():
    """Test ValidationError without line number."""
    error = ValidationError(Path("/path/to/file.md"), "Test error")
    
    error_str = str(error)
    
    assert "/path/to/file.md" in error_str
    assert "Test error" in error_str
    # Should not have line number suffix
    assert error_str.count(":") == 0 or not error_str.split(": ")[0].endswith(":0")
