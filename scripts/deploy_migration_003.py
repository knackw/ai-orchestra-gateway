#!/usr/bin/env python3
"""
Deploy and test migration 003 to Supabase.

This script:
1. Checks Supabase connectivity
2. Applies migration 003 (apps + usage_logs)
3. Verifies schema was created correctly
4. Runs automated tests

Usage:
    python scripts/deploy_migration_003.py
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_supabase_client


def check_connectivity():
    """Check if Supabase is accessible."""
    print("🔍 Checking Supabase connectivity...")
    try:
        client = get_supabase_client()
        # Simple query to test connection
        result = client.table("tenants").select("id").limit(1).execute()
        print("✅ Connected to Supabase")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("\nPlease check:")
        print("  1. .env file exists with SUPABASE_URL and SUPABASE_KEY")
        print("  2. Supabase instance is running")
        return False


def read_migration():
    """Read migration 003 SQL file."""
    print("\n📄 Reading migration file...")
    migration_path = Path(__file__).parent.parent / "migrations" / "003_create_apps_and_usage_logs.sql"
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return None
    
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"✅ Loaded migration ({len(sql)} characters)")
    return sql


def apply_migration(client, sql):
    """Apply migration SQL to Supabase."""
    print("\n🚀 Applying migration to Supabase...")
    print("   This may take 10-15 seconds...")
    
    try:
        # Supabase Python client doesn't have direct SQL execution
        # We need to use RPC or guide user to dashboard
        print("\n⚠️  Important: The Python Supabase client doesn't support direct SQL execution.")
        print("   You have two options:")
        print("\n   Option 1: Supabase Dashboard (Recommended)")
        print("   1. Open: https://supabase.com/dashboard")
        print("   2. Go to: Database → SQL Editor")
        print("   3. Copy migration from: migrations/003_create_apps_and_usage_logs.sql")
        print("   4. Paste and click 'Run'")
        
        print("\n   Option 2: Supabase CLI")
        print("   Run: npx supabase db push")
        
        print("\n   After applying migration, run this script again to verify.")
        
        return False  # Not applied via Python
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_schema(client):
    """Verify that migration was applied successfully."""
    print("\n🔍 Verifying schema...")
    
    checks = []
    
    # Check 1: apps table exists
    try:
        result = client.table("apps").select("*").limit(1).execute()
        checks.append(("apps table exists", True))
        print("  ✅ apps table exists")
    except Exception as e:
        checks.append(("apps table exists", False))
        print(f"  ❌ apps table missing: {e}")
    
    # Check 2: usage_logs table exists
    try:
        result = client.table("usage_logs").select("*").limit(1).execute()
        checks.append(("usage_logs table exists", True))
        print("  ✅ usage_logs table exists")
    except Exception as e:
        checks.append(("usage_logs table exists", False))
        print(f"  ❌ usage_logs table missing: {e}")
    
    # Check 3: Demo app exists
    try:
        result = client.table("apps").select("*").eq(
            "id", "00000000-0000-0000-0000-000000000010"
        ).execute()
        if result.data:
            checks.append(("demo app exists", True))
            print(f"  ✅ Demo app exists: {result.data[0]['app_name']}")
        else:
            checks.append(("demo app exists", False))
            print("  ❌ Demo app not found")
    except Exception as e:
        checks.append(("demo app exists", False))
        print(f"  ❌ Error checking demo app: {e}")
    
    # Check 4: Licenses have app_id
    try:
        result = client.table("licenses").select("app_id").limit(1).execute()
        if result.data and result.data[0].get("app_id"):
            checks.append(("licenses have app_id", True))
            print("  ✅ licenses.app_id column exists")
        else:
            checks.append(("licenses have app_id", False))
            print("  ❌ licenses.app_id column missing")
    except Exception as e:
        checks.append(("licenses have app_id", False))
        print(f"  ❌ Error checking licenses: {e}")
    
    # Check 5: Usage logs exist
    try:
        result = client.table("usage_logs").select("id").execute()
        count = len(result.data) if result.data else 0
        checks.append(("usage logs created", count >= 5))
        print(f"  {'✅' if count >= 5 else '❌'} {count} usage logs found (expected ≥5)")
    except Exception as e:
        checks.append(("usage logs created", False))
        print(f"  ❌ Error counting usage logs: {e}")
    
    # Summary
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\n📊 Verification: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ Migration successfully applied!")
        return True
    else:
        print("⚠️  Migration incomplete or not yet applied")
        return False


def run_tests():
    """Run automated tests."""
    print("\n🧪 Running automated tests...")
    print("   Command: pytest app/tests/test_db_schema.py -v")
    
    import subprocess
    try:
        result = subprocess.run(
            ["pytest", "app/tests/test_db_schema.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed (exit code: {result.returncode})")
            return False
            
    except FileNotFoundError:
        print("⚠️  pytest not found. Run manually:")
        print("   pytest app/tests/test_db_schema.py -v")
        return None


def main():
    """Main deployment workflow."""
    print("=" * 60)
    print("  Migration 003 Deployment & Testing")
    print("  AI Legal Ops Gateway - Database Schema")
    print("=" * 60)
    
    # Step 1: Check connectivity
    if not check_connectivity():
        print("\n❌ Deployment aborted: Cannot connect to Supabase")
        sys.exit(1)
    
    client = get_supabase_client()
    
    # Step 2: Check if migration already applied
    print("\n🔍 Checking if migration already applied...")
    try:
        result = client.table("apps").select("id").limit(1).execute()
        print("⚠️  Migration appears to already be applied (apps table exists)")
        print("   Proceeding to verification...")
        migration_applied = True
    except:
        print("✅ Migration not yet applied")
        migration_applied = False
    
    # Step 3: Apply migration (guide user)
    if not migration_applied:
        sql = read_migration()
        if sql:
            apply_migration(client, sql)
            print("\n⏸️  Pausing for manual migration...")
            print("   After applying migration, press Enter to continue verification...")
            input()
    
    # Step 4: Verify schema
    if verify_schema(client):
        # Step 5: Run tests
        test_result = run_tests()
        
        if test_result:
            print("\n" + "=" * 60)
            print("  ✅ DEPLOYMENT SUCCESSFUL!")
            print("  Migration 003 applied and tested successfully")
            print("=" * 60)
            sys.exit(0)
        elif test_result is None:
            print("\n" + "=" * 60)
            print("  ⚠️  DEPLOYMENT COMPLETE (tests need manual run)")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("  ❌ TESTS FAILED")
            print("=" * 60)
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("  ❌ VERIFICATION FAILED")
        print("  Migration not fully applied")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
