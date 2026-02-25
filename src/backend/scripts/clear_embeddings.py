"""Clear embeddings script.

Utility for clearing embeddings from the database:
- Delete all embeddings
- Delete embeddings matching a content path pattern
- Confirmation prompt before deletion
"""

import argparse
import sys
from pathlib import Path

from app.db.session import SessionLocal
from app.services.rag.repository import RAGRepository
from scripts.common import confirm, error, info, success, warning


def main():
    """Main entry point for clear embeddings script."""
    parser = argparse.ArgumentParser(
        description="Clear embeddings from database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all embeddings (with confirmation)
  python -m scripts.clear_embeddings
  
  # Clear embeddings for specific path pattern
  python -m scripts.clear_embeddings --pattern "certifications/*"
  
  # Force clear without confirmation (use with caution!)
  python -m scripts.clear_embeddings --force
        """,
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default=None,
        help="Content path pattern to match (e.g., 'certifications/*')",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt (use with caution)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        warning("DRY RUN MODE: No deletions will be performed")
    
    # Initialize repository
    db = SessionLocal()
    try:
        repository = RAGRepository(db)
        
        # Get count of embeddings to delete
        if args.pattern:
            info(f"Finding embeddings matching pattern: {args.pattern}")
            # Note: This requires a method to count by pattern
            # For now, we'll use a simple approach
            count = repository.count_by_pattern(args.pattern)
            scope = f"embeddings matching '{args.pattern}'"
        else:
            count = repository.count_all()
            scope = "all embeddings"
        
        if count == 0:
            info(f"No embeddings found to delete")
            sys.exit(0)
        
        info(f"Found {count} embedding(s) to delete")
        
        # Confirm deletion
        if not args.force and not args.dry_run:
            if not confirm(f"Delete {scope}?", default=False):
                error("Aborted by user")
                sys.exit(1)
        
        # Perform deletion
        if not args.dry_run:
            if args.pattern:
                deleted_count = repository.delete_by_pattern(args.pattern)
            else:
                deleted_count = repository.delete_all()
            
            success(f"Deleted {deleted_count} embedding(s)")
        else:
            info(f"Would delete {count} embedding(s)")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
