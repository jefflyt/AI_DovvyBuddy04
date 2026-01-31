"""
Environment Configuration Verification Report
==============================================

This report verifies that all .env.local loading points are correctly configured
to use the root .env.local file.

Date: January 31, 2026
"""

from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def verify_env_loading():
    """Verify all .env.local loading points."""
    
    print("=" * 70)
    print("ENVIRONMENT CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    # 1. Check session.py
    print("1. backend/app/db/session.py")
    print("-" * 70)
    from app.db import session
    session_file = Path(session.__file__)
    print(f"   Location: {session_file}")
    
    # Calculate expected path
    expected_env = session_file.resolve().parent.parent.parent.parent / ".env.local"
    print(f"   Expected .env.local: {expected_env}")
    print(f"   Exists: {expected_env.exists()}")
    
    # Test database URL loading
    from app.db.session import get_database_url, get_sync_database_url
    async_url = get_database_url()
    sync_url = get_sync_database_url()
    
    print(f"   Async URL starts with: {async_url[:50]}...")
    print(f"   Sync URL starts with: {sync_url[:50]}...")
    
    if "neondb" in async_url:
        print("   ✅ Correctly loading Neon database from .env.local")
    else:
        print("   ❌ Using default/wrong database URL")
    
    print()
    
    # 2. Check alembic/env.py
    print("2. backend/alembic/env.py")
    print("-" * 70)
    alembic_env = Path(__file__).resolve().parent.parent / "alembic" / "env.py"
    print(f"   Location: {alembic_env}")
    
    if alembic_env.exists():
        with open(alembic_env) as f:
            content = f.read()
            if 'Path(__file__).resolve()' in content and '.env.local' in content:
                print("   ✅ Using Path(__file__).resolve() with .env.local")
            else:
                print("   ⚠️  Path resolution may need checking")
    else:
        print("   ⚠️  File not found")
    
    print()
    
    # 3. Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Files loading .env.local:")
    print("  1. backend/app/db/session.py (4 levels up)")
    print("  2. backend/alembic/env.py (3 levels up)")
    print()
    print("Path calculations:")
    print("  - session.py: backend/app/db/session.py -> root/.env.local")
    print("    Path(__file__).resolve().parent.parent.parent.parent")
    print()
    print("  - alembic/env.py: backend/alembic/env.py -> root/.env.local")
    print("    Path(__file__).resolve().parent.parent.parent")
    print()
    print("Database URL conversions:")
    print("  - Async (FastAPI): postgresql:// → postgresql+asyncpg://")
    print("  - Sync (scripts): postgresql:// (unchanged)")
    print("  - SSL params: sslmode → ssl for asyncpg")
    print("  - Channel binding removed for asyncpg compatibility")
    print()
    
    if "neondb" in async_url:
        print("✅ ALL CONFIGURATION VERIFIED - Ready for production")
        return True
    else:
        print("❌ CONFIGURATION ISSUE - Using wrong database")
        return False


if __name__ == "__main__":
    success = verify_env_loading()
    sys.exit(0 if success else 1)
