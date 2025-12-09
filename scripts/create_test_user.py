"""
Script to create a test user with password for Supabase Auth.

This script:
1. Creates a Tenant in public.tenants
2. Creates an App for that Tenant
3. Creates a License for that App
4. Creates a Supabase Auth User with Email/Password
5. Prints all credentials
"""

import os
import sys
import secrets
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    print("Please ensure you have a .env file with these variables.")
    sys.exit(1)

def get_supabase_admin() -> Client:
    """Get Supabase client with Service Role (Admin) privileges."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def generate_password(length=12):
    """Generate a secure random password."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))

def create_test_integration():
    client = get_supabase_admin()
    
    # 1. Generate Test Data
    test_id = secrets.token_hex(4)
    email = f"test_user_{test_id}@example.com"
    password = generate_password()
    tenant_name = f"Test Tenant {test_id}"
    app_name = "Test App (Default)"
    
    print(f"🚀 Creating test environment for: {email}")
    
    try:
        # 2. Create Tenant (public schema)
        print("Creating Tenant...")
        tenant_res = client.table("tenants").insert({
            "name": tenant_name,
            "email": email,
            "is_active": True
        }).execute()
        
        tenant_id = tenant_res.data[0]["id"]
        
        # 3. Create App
        print("Creating App...")
        app_res = client.table("apps").insert({
            "tenant_id": tenant_id,
            "app_name": app_name,
            "is_active": True
        }).execute()
        
        app_id = app_res.data[0]["id"]
        
        # 4. Create License
        print("Creating License...")
        license_key = f"lic_test_{secrets.token_urlsafe(16)}"
        client.table("licenses").insert({
            "tenant_id": tenant_id, # Keep for backward compatibility if needed
            "app_id": app_id,
            "license_key": license_key,
            "credits_remaining": 5000,
            "is_active": True
        }).execute()
        
        # 5. Create Supabase Auth User
        print("Creating Supabase Auth User...")
        try:
            auth_res = client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "tenant_id": tenant_id,
                    "role": "admin"
                }
            })
            user_id = auth_res.user.id
            print("✅ Auth User created successfully.")
            
        except Exception as e:
            print(f"⚠️ Warning creating Auth User (might already exist): {e}")
            user_id = "UNKNOWN"

        # 6. Output Credentials
        print("\n" + "="*50)
        print("✅ TEST USER CREATED SUCCESSFULLY")
        print("="*50)
        print(f"Email:        {email}")
        print(f"Password:     {password}")
        print("-" * 50)
        print(f"Tenant ID:    {tenant_id}")
        print(f"App ID:       {app_id}")
        print(f"License Key:  {license_key}")
        print("="*50)
        print("\nSave these credentials! You can use them to login to the frontend.")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_test_integration()
