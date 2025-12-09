import os
import sys
import psycopg2
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

DIRECT_URL = os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL")

def check_schema():
    if not DIRECT_URL:
        print("❌ No DATABASE_URL/DIRECT_URL found")
        return

    try:
        conn = psycopg2.connect(DIRECT_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check column
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'tenants' 
            AND column_name = 'is_active';
        """)
        
        result = cur.fetchone()
        
        if result:
            print("✅ 'is_active' column found in 'tenants' table.")
            print("🔄 Triggering schema cache reload...")
            cur.execute("NOTIFY pgrst, 'reload schema';")
            print("✅ Reload signal sent.")
        else:
            print("❌ 'is_active' column NOT FOUND. Migration 001 fix missing?")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_schema()
