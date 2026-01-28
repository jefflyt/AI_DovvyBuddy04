"""Unit tests for markdown_parser module."""

import tempfile
from pathlib import Path

import pytest

from scripts.common.markdown_parser import (
    check_markdown_structure,
    FrontmatterError,
    MarkdownParseError,
    parse_markdown,
    validate_frontmatter,
)


def test_parse_markdown_with_frontmatter():
    """Test parsing markdown with valid frontmatter."""
    content = """---
title: Test Document
description: A test document
tags:
  - test
  - demo
---

# Heading

Some content here.
"""
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        result = parse_markdown(temp_file)
        
        assert "frontmatter" in result
        assert "content" in result
        
        frontmatter = result["frontmatter"]
        assert frontmatter["title"] == "Test Document"
        assert frontmatter["description"] == "A test document"
        assert frontmatter["tags"] == ["test", "demo"]
        
        content_text = result["content"]
        assert "# Heading" in content_text
        assert "Some content here." in content_text
    finally:
        temp_file.unlink()


def test_parse_markdown_without_frontmatter():
    """Test parsing markdown without frontmatter."""
    content = "# Heading\n\nJust content, no frontmatter."
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        result = parse_markdown(temp_file)
        
        assert result["frontmatter"] == {}
        assert "# Heading" in result["content"]
    finally:
        temp_file.unlink()


def test_parse_markdown_invalid_yaml():
    """Test parsing markdown with invalid YAML frontmatter."""
    content = """---
title: Test
invalid: [unclosed bracket
---

Content
"""
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write(content)
        temp_file = Path(f.name)
    
    try:
        with pytest.raises(FrontmatterError):
            parse_markdown(temp_file)
    finally:
        temp_file.unlink()


def test_parse_markdown_nonexistent_file():
    """Test parsing nonexistent file."""
    nonexistent = Path("/nonexistent/file.md")
    
    with pytest.raises(MarkdownParseError):
        parse_markdown(nonexistent)


def test_validate_frontmatter_valid():
    """Test validating valid frontmatter."""
    frontmatter = {
        "title": "Test Title",
        "description": "Test description",
        "tags": ["tag1", "tag2"],
    }
    
    errors = validate_frontmatter(frontmatter)
    
    assert errors == []


def test_validate_frontmatter_missing_required():
    """Test validating frontmatter with missing required fields."""
    frontmatter = {
        "title": "Test Title",
        # Missing description
    }
    
    errors = validate_frontmatter(frontmatter, required_fields=["title", "description"])
    
    assert len(errors) == 1
    assert "description" in errors[0]


def test_validate_frontmatter_empty_field():
    """Test validating frontmatter with empty required field."""
    frontmatter = {
        "title": "",  # Empty
        "description": "Test description",
    }
    
    errors = validate_frontmatter(frontmatter)
    
    assert len(errors) == 1
    assert "title" in errors[0]


def test_validate_frontmatter_invalid_tags():
    """Test validating frontmatter with invalid tags type."""
    frontmatter = {
        "title": "Test",
        "description": "Test",
        "tags": "not-a-list",  # Should be list
    }
    
    errors = validate_frontmatter(frontmatter)
    
    assert len(errors) == 1
    assert "tags" in errors[0]


def test_validate_frontmatter_tags_with_non_strings():
    """Test validating frontmatter with non-string items in tags."""
    frontmatter = {
        "title": "Test",
        "description": "Test",
        "tags": ["valid", 123, "another"],  # 123 is not a string
    }
    
    errors = validate_frontmatter(frontmatter)
    
    assert len(errors) == 1
    assert "tags" in errors[0]


def test_check_markdown_structure_valid():
    """Test checking valid markdown structure."""
    content = """# Main Heading

Some introductory content.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""
    
    warnings = check_markdown_structure(content)
    
    assert warnings == []


def test_check_markdown_structure_consecutive_headers():
    """Test checking markdown with consecutive headers."""
    content = """# Main Heading
## Subheading

No content between main and subheading above.
"""
    
    warnings = check_markdown_structure(content)
    
    assert len(warnings) > 0
    assert any("consecutive" in w.lower() for w in warnings)


def test_check_markdown_structure_empty_content():
    """Test checking empty markdown content."""
    content = ""
    
    warnings = check_markdown_structure(content)
    
    assert len(warnings) == 1
    assert "empty" in warnings[0].lower()


def test_check_markdown_structure_broken_link():
    """Test checking markdown with broken link."""
    content = """# Heading

Here is a [broken link](without-closing-paren
"""
    
    warnings = check_markdown_structure(content)
    
    assert len(warnings) > 0
    assert any("link" in w.lower() for w in warnings)
