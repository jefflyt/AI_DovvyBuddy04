"""Content validation script.

Validates markdown files in the content directory for:
- Valid frontmatter (YAML)
- Required fields (title, description, etc.)
- Markdown structure (headers, links)
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from scripts.common import (
    error,
    find_markdown_files,
    FrontmatterError,
    get_relative_path,
    info,
    MarkdownParseError,
    parse_markdown,
    success,
    validate_frontmatter,
    warning,
)
from scripts.common.markdown_parser import check_markdown_structure


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, file_path: Path, message: str, line: int = 0):
        """Initialize validation error.
        
        Args:
            file_path: Path to the file with error
            message: Error message
            line: Line number (0 if not applicable)
        """
        self.file_path = file_path
        self.message = message
        self.line = line
    
    def __str__(self) -> str:
        """Format error message."""
        line_info = f":{self.line}" if self.line > 0 else ""
        return f"{self.file_path}{line_info}: {self.message}"


def validate_file(
    file_path: Path,
    required_fields: List[str],
    check_structure: bool = True,
) -> Tuple[bool, List[ValidationError]]:
    """Validate a single markdown file.
    
    Args:
        file_path: Path to markdown file
        required_fields: List of required frontmatter fields
        check_structure: Whether to check markdown structure
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []
    
    # Parse markdown file
    try:
        parsed = parse_markdown(file_path)
    except MarkdownParseError as e:
        errors.append(ValidationError(file_path, str(e)))
        return False, errors
    except FrontmatterError as e:
        errors.append(ValidationError(file_path, f"Frontmatter error: {e}"))
        return False, errors
    
    frontmatter = parsed["frontmatter"]
    content = parsed["content"]
    
    # Check for missing frontmatter
    if not frontmatter:
        errors.append(
            ValidationError(file_path, "No frontmatter found (expected YAML between --- delimiters)")
        )
    
    # Validate frontmatter fields
    frontmatter_errors = validate_frontmatter(frontmatter, required_fields)
    for err_msg in frontmatter_errors:
        errors.append(ValidationError(file_path, f"Frontmatter: {err_msg}"))
    
    # Check markdown structure
    if check_structure:
        structure_warnings = check_markdown_structure(content)
        for warn_msg in structure_warnings:
            errors.append(ValidationError(file_path, f"Structure: {warn_msg}"))
    
    return len(errors) == 0, errors


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description="Validate markdown content files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all content files
  python -m scripts.validate_content
  
  # Validate specific directory
  python -m scripts.validate_content --content-dir ../content/certifications
  
  # Skip structure checks
  python -m scripts.validate_content --no-structure-check
        """,
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=Path("../content"),
        help="Content directory to validate (default: ../content)",
    )
    parser.add_argument(
        "--required-fields",
        type=str,
        nargs="+",
        default=["title", "description"],
        help="Required frontmatter fields (default: title description)",
    )
    parser.add_argument(
        "--no-structure-check",
        action="store_true",
        help="Skip markdown structure checks",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.md",
        help="File pattern to match (default: **/*.md)",
    )
    
    args = parser.parse_args()
    
    # Resolve content directory
    content_dir = args.content_dir.resolve()
    
    info(f"Validating content in: {content_dir}")
    info(f"Required fields: {', '.join(args.required_fields)}")
    
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
    
    # Validate each file
    all_errors: List[ValidationError] = []
    valid_count = 0
    
    for file_path in markdown_files:
        is_valid, file_errors = validate_file(
            file_path,
            args.required_fields,
            check_structure=not args.no_structure_check,
        )
        
        if is_valid:
            valid_count += 1
        else:
            all_errors.extend(file_errors)
    
    # Report results
    print()  # Blank line before results
    
    if all_errors:
        error(f"Validation failed with {len(all_errors)} error(s):")
        print()
        
        # Group errors by file
        errors_by_file = {}
        for err in all_errors:
            rel_path = get_relative_path(err.file_path, content_dir)
            if rel_path not in errors_by_file:
                errors_by_file[rel_path] = []
            errors_by_file[rel_path].append(err)
        
        # Print errors grouped by file
        for rel_path, file_errors in sorted(errors_by_file.items()):
            error(f"{rel_path}:")
            for err in file_errors:
                print(f"  - {err.message}")
            print()
        
        error(f"Summary: {len(all_errors)} error(s) in {len(errors_by_file)} file(s)")
        sys.exit(1)
    else:
        success(f"All {valid_count} file(s) passed validation ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
