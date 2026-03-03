"""Markdown parsing utilities for content processing."""

import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class FrontmatterError(Exception):
    """Error parsing or validating frontmatter."""
    pass


class MarkdownParseError(Exception):
    """Error parsing markdown content."""
    pass


def parse_markdown(file_path: Path) -> Dict[str, Any]:
    """Parse markdown file and extract frontmatter and content.
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        Dictionary with 'frontmatter' (dict) and 'content' (str) keys
        
    Raises:
        MarkdownParseError: If file cannot be parsed
        FrontmatterError: If frontmatter is invalid
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        raise MarkdownParseError(f"Failed to read file {file_path}: {e}")
    
    # Check for frontmatter (YAML between --- delimiters)
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(frontmatter_pattern, raw_content, re.DOTALL)
    
    if not match:
        # No frontmatter found
        return {
            "frontmatter": {},
            "content": raw_content.strip(),
        }
    
    frontmatter_text = match.group(1)
    content = match.group(2).strip()
    
    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as e:
        raise FrontmatterError(f"Invalid YAML in frontmatter: {e}")
    
    if not isinstance(frontmatter, dict):
        raise FrontmatterError(
            f"Frontmatter must be a YAML object, got {type(frontmatter).__name__}"
        )
    
    return {
        "frontmatter": frontmatter,
        "content": content,
    }


def validate_frontmatter(
    frontmatter: Dict[str, Any],
    required_fields: Optional[list[str]] = None,
) -> list[str]:
    """Validate frontmatter fields.
    
    Args:
        frontmatter: Frontmatter dictionary
        required_fields: List of required field names (default: title, description)
        
    Returns:
        List of error messages (empty if valid)
    """
    if required_fields is None:
        required_fields = ["title", "description"]
    
    errors = []
    
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
        elif not frontmatter[field]:
            errors.append(f"Empty required field: {field}")
    
    # Validate specific field types
    if "tags" in frontmatter:
        tags = frontmatter["tags"]
        if not isinstance(tags, list):
            errors.append(f"Field 'tags' must be a list, got {type(tags).__name__}")
        elif tags and not all(isinstance(t, str) for t in tags):
            errors.append("Field 'tags' must contain only strings")
    
    if "date" in frontmatter:
        date_value = frontmatter["date"]
        if not isinstance(date_value, (str, int)):
            errors.append(f"Field 'date' must be a string or number, got {type(date_value).__name__}")
    
    return errors


def check_markdown_structure(content: str) -> list[str]:
    """Check markdown content for structural issues.
    
    Args:
        content: Markdown content
        
    Returns:
        List of warning messages (empty if valid)
    """
    warnings = []
    
    # Check for broken links (basic check for [text]( pattern without closing )
    broken_link_pattern = r"\[([^\]]+)\]\([^)]*$"
    if re.search(broken_link_pattern, content, re.MULTILINE):
        warnings.append("Found potentially broken markdown link")
    
    # Check for consecutive headers without content between them
    lines = content.split("\n")
    prev_was_header = False
    for i, line in enumerate(lines, 1):
        is_header = line.strip().startswith("#")
        if is_header and prev_was_header:
            warnings.append(f"Line {i}: Consecutive headers without content")
        prev_was_header = is_header
    
    # Check for empty content
    if not content.strip():
        warnings.append("Content is empty")
    
    return warnings
