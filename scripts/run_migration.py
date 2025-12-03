"""
Script to run Supabase migrations.

Usage:
    python scripts/run_migration.py migrations/001_create_licenses_table.sql
"""

import sys
from pathlib import Path

from app.core.database import get_supabase_client


def run_migration(sql_file: str):
    """Run SQL migration file on Supabase."""
    
    # Read SQL file
    sql_path = Path(sql_file)
    if not sql_path.exists():
        print(f"Error: File {sql_file} not found")
        sys.exit(1)
    
    sql_content = sql_path.read_text()
    
    # Get Supabase client
    client = get_supabase_client()
    
    # Execute SQL (using RPC or direct query)
    # Note: Supabase Python client doesn't support direct SQL execution
    # You need to run this via Supabase Dashboard or psql
    
    print(f"Migration file: {sql_file}")
    print("=" * 60)
    print(sql_content)
    print("=" * 60)
    print("\nPlease run this SQL in Supabase Dashboard:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to SQL Editor")
    print("4. Paste and run the SQL above")
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_migration.py <sql_file>")
        sys.exit(1)
    
    run_migration(sys.argv[1])
