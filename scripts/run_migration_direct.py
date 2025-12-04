"""
Script to run SQL migrations directly on Supabase PostgreSQL.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration(migration_file):
    """Run a SQL migration file on Supabase."""
    
    # Get database URL
    db_url = os.getenv("DIRECT_URL")
    
    if not db_url:
        print("ERROR: DIRECT_URL not found in .env")
        sys.exit(1)
    
    # Read migration file
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
    except FileNotFoundError:
        print(f"ERROR: Migration file not found: {migration_file}")
        sys.exit(1)
    
    # Connect to database
    print(f"Connecting to Supabase...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"Running migration: {migration_file}")
        cursor.execute(sql)
        
        print("✅ Migration executed successfully!")
        
        # Test the function
        print("\nTesting deduct_credits function...")
        cursor.execute("SELECT routine_name FROM information_schema.routines WHERE routine_name = 'deduct_credits' AND routine_schema = 'public';")
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Function 'deduct_credits' exists in database")
        else:
            print("⚠️  Function not found - check migration")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration_direct.py <migration_file>")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    run_migration(migration_file)
