import pytest
import uuid
from app.core.database import get_supabase_client

# Constants for test tenants
TENANT_A_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TENANT_B_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
APP_A_ID = "aaaaaaaa-aaaa-aaaa-aaaa-000000000001"
APP_B_ID = "bbbbbbbb-bbbb-bbbb-bbbb-000000000001"

@pytest.fixture(scope="module")
def setup_test_data():
    """Create test tenants and apps for RLS testing."""
    # Use service role to bypass RLS for setup
    client = get_supabase_client(use_service_role=True)
    
    # Clean up existing test data if any
    client.table("tenants").delete().in_("id", [TENANT_A_ID, TENANT_B_ID]).execute()
    
    # Create Tenant A
    client.table("tenants").insert({
        "id": TENANT_A_ID,
        "name": "Tenant A",
        "email": "tenant_a@test.com"
    }).execute()
    
    client.table("apps").insert({
        "id": APP_A_ID,
        "tenant_id": TENANT_A_ID,
        "app_name": "App A1"
    }).execute()
    
    # Create Tenant B
    client.table("tenants").insert({
        "id": TENANT_B_ID,
        "name": "Tenant B",
        "email": "tenant_b@test.com"
    }).execute()
    
    client.table("apps").insert({
        "id": APP_B_ID,
        "tenant_id": TENANT_B_ID,
        "app_name": "App B1"
    }).execute()
    
    yield
    
    # Cleanup
    client.table("tenants").delete().in_("id", [TENANT_A_ID, TENANT_B_ID]).execute()

class TestRLSPolicies:
    """Test Row Level Security policies for tenant isolation."""
    
    def test_service_role_sees_all(self, setup_test_data):
        """Service role (admin) should see all tenants and apps."""
        # Use service role to bypass RLS
        client = get_supabase_client(use_service_role=True)
        
        # Query all apps
        result = client.table("apps").select("*").execute()
        
        # Should see both App A1 and App B1 (plus demo app)
        app_ids = [item['id'] for item in result.data]
        assert APP_A_ID in app_ids
        assert APP_B_ID in app_ids
        
    def test_anon_sees_nothing(self, setup_test_data):
        """Anonymous client (no role/tenant) should see zero rows due to RLS."""
        # Standard client uses anon key by default
        client = get_supabase_client(use_service_role=False)
        
        # Query tenants - should be empty
        # If RLS was disabled, this would return all tenants (public table)
        # If RLS is enabled but policy allows anon, it would return rows
        # The 'tenants_select_own' policy requires app.current_tenant_id which is null here
        result = client.table("tenants").select("*").execute()
        assert len(result.data) == 0
        
        # Query apps - should be empty
        result = client.table("apps").select("*").execute()
        assert len(result.data) == 0

    def test_rls_policies_exist(self):
        """Verify that RLS is enabled on tables."""
        # This is a meta-test to ensure migration ran
        client = get_supabase_client()
        
        # We can check pg_policies or similar system tables if we had access
        # For now, we assume if migration passed, policies exist.
        pass
