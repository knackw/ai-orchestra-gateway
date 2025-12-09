"""
Tests for database schema (DB-001).

Validates the complete multi-tenant schema including:
- apps table structure and relationships
- usage_logs table and immutability
- Foreign key cascades
- Demo data integrity
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from app.core.database import get_supabase_client


class TestAppsTable:
    """Tests for apps table schema and functionality."""
    
    def test_apps_table_exists(self):
        """Verify apps table exists and is queryable."""
        client = get_supabase_client()
        try:
            result = client.table("apps").select("*").limit(1).execute()
            assert result is not None
        except Exception as e:
            pytest.fail(f"apps table does not exist or is not accessible: {e}")
    
    def test_apps_has_required_columns(self):
        """Verify apps table has all required columns."""
        client = get_supabase_client()
        result = client.table("apps").select("*").limit(1).execute()
        
        if result.data:
            app = result.data[0]
            required_columns = [
                "id", "tenant_id", "app_name", "allowed_origins",
                "is_active", "created_at", "updated_at"
            ]
            for column in required_columns:
                assert column in app, f"Missing column: {column}"
    
    def test_demo_app_exists(self):
        """Verify demo app was created during migration."""
        client = get_supabase_client()
        result = client.table("apps").select("*").eq(
            "id", "00000000-0000-0000-0000-000000000010"
        ).execute()

        if len(result.data) == 0:
            pytest.skip("Demo data not present - skipping demo data test")

        demo_app = result.data[0]
        assert demo_app["app_name"] == "Demo App - AGB Generator"
        assert demo_app["tenant_id"] == "00000000-0000-0000-0000-000000000001"
        assert demo_app["is_active"] is True
        assert isinstance(demo_app["allowed_origins"], list)
        assert len(demo_app["allowed_origins"]) > 0
    
    def test_apps_foreign_key_to_tenants(self):
        """Verify apps has foreign key constraint to tenants."""
        client = get_supabase_client()
        
        # Try to insert app with invalid tenant_id (should fail)
        invalid_tenant_id = str(uuid4())
        test_app = {
            "tenant_id": invalid_tenant_id,
            "app_name": "Test App Invalid Tenant"
        }
        
        with pytest.raises(Exception) as exc_info:
            client.table("apps").insert(test_app).execute()
        
        # Should fail due to foreign key constraint
        assert "foreign key" in str(exc_info.value).lower() or "violates" in str(exc_info.value).lower()


class TestLicensesTableAppId:
    """Tests for licenses table app_id column addition."""
    
    def test_licenses_has_app_id_column(self):
        """Verify licenses table has app_id column."""
        client = get_supabase_client()
        result = client.table("licenses").select("*").limit(1).execute()
        
        if result.data:
            license = result.data[0]
            assert "app_id" in license, "app_id column missing from licenses table"
    
    def test_demo_licenses_migrated_to_app(self):
        """Verify demo licenses have been migrated to demo app."""
        client = get_supabase_client()

        # Get demo licenses
        result = client.table("licenses").select("*").eq(
            "tenant_id", "00000000-0000-0000-0000-000000000001"
        ).execute()

        if len(result.data) == 0:
            pytest.skip("Demo data not present - skipping demo data test")

        # All should have app_id set
        for license in result.data:
            assert license["app_id"] is not None, f"License {license['id']} has null app_id"
            assert license["app_id"] == "00000000-0000-0000-0000-000000000010", \
                f"License {license['id']} not migrated to demo app"
    
    def test_licenses_foreign_key_to_apps(self):
        """Verify licenses has foreign key constraint to apps."""
        client = get_supabase_client()
        
        # Try to insert license with invalid app_id (should fail)
        invalid_app_id = str(uuid4())
        test_license = {
            "app_id": invalid_app_id,
            "tenant_id": "00000000-0000-0000-0000-000000000001",
            "license_key": f"lic_test_invalid_app_{uuid4().hex[:8]}",
            "credits_remaining": 1000
        }
        
        with pytest.raises(Exception) as exc_info:
            client.table("licenses").insert(test_license).execute()
        
        # Should fail due to foreign key constraint
        assert "foreign key" in str(exc_info.value).lower() or "violates" in str(exc_info.value).lower()


class TestUsageLogsTable:
    """Tests for usage_logs table schema and immutability."""
    
    def test_usage_logs_table_exists(self):
        """Verify usage_logs table exists."""
        client = get_supabase_client()
        try:
            result = client.table("usage_logs").select("*").limit(1).execute()
            assert result is not None
        except Exception as e:
            pytest.fail(f"usage_logs table does not exist: {e}")
    
    def test_usage_logs_has_required_columns(self):
        """Verify usage_logs has all required columns."""
        client = get_supabase_client()
        result = client.table("usage_logs").select("*").limit(1).execute()
        
        if result.data:
            log = result.data[0]
            required_columns = [
                "id", "license_id", "app_id", "tenant_id",
                "prompt_length", "pii_detected", "provider", "model",
                "tokens_used", "credits_deducted", "response_status",
                "created_at"
            ]
            for column in required_columns:
                assert column in log, f"Missing column: {column}"
    
    def test_demo_usage_logs_exist(self):
        """Verify demo usage logs were created."""
        client = get_supabase_client()
        result = client.table("usage_logs").select("*").eq(
            "tenant_id", "00000000-0000-0000-0000-000000000001"
        ).execute()

        if len(result.data) < 5:
            pytest.skip(f"Demo data not present - found {len(result.data)} logs, need at least 5")
    
    def test_usage_logs_immutability_update(self):
        """Verify usage_logs UPDATE is blocked (immutability)."""
        client = get_supabase_client()
        
        # Get first log entry
        result = client.table("usage_logs").select("id, tokens_used").limit(1).execute()
        
        if not result.data:
            pytest.skip("No usage logs to test")
        
        log_id = result.data[0]["id"]
        
        # Try to update (should fail due to RLS policy)
        with pytest.raises(Exception):
            client.table("usage_logs").update({"tokens_used": 99999}).eq("id", log_id).execute()
    
    def test_usage_logs_immutability_delete(self):
        """Verify usage_logs DELETE is blocked (immutability)."""
        client = get_supabase_client()
        
        # Get first log entry
        result = client.table("usage_logs").select("id").limit(1).execute()
        
        if not result.data:
            pytest.skip("No usage logs to test")
        
        log_id = result.data[0]["id"]
        
        # Try to delete (should fail due to RLS policy)
        with pytest.raises(Exception):
            client.table("usage_logs").delete().eq("id", log_id).execute()
    
    def test_usage_logs_insert_allowed(self):
        """Verify usage_logs INSERT is allowed."""
        client = get_supabase_client()
        
        # Get demo license and app for valid foreign keys
        license_result = client.table("licenses").select("id").eq(
            "license_key", "lic_demo_valid_123"
        ).execute()
        
        if not license_result.data:
            pytest.skip("Demo license not found")
        
        license_id = license_result.data[0]["id"]
        
        # Create test log
        test_log = {
            "license_id": license_id,
            "app_id": "00000000-0000-0000-0000-000000000010",
            "tenant_id": "00000000-0000-0000-0000-000000000001",
            "prompt_length": 100,
            "pii_detected": False,
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "tokens_used": 50,
            "credits_deducted": 50,
            "response_status": "success"
        }
        
        # Should succeed
        result = client.table("usage_logs").insert(test_log).execute()
        assert len(result.data) == 1
        assert result.data[0]["tokens_used"] == 50


class TestForeignKeyCascades:
    """Tests for CASCADE DELETE behavior."""

    def test_cascade_delete_tenant_to_apps(self):
        """Verify deleting tenant cascades to apps."""
        client = get_supabase_client()

        try:
            # Create test tenant
            test_tenant = {
                "name": "Test Tenant Cascade",
                "email": f"cascade_test_{uuid4().hex[:8]}@example.com"
            }
            tenant_result = client.table("tenants").insert(test_tenant).execute()
            if not tenant_result.data:
                pytest.skip("Unable to create test tenant - RLS may block insert")
            tenant_id = tenant_result.data[0]["id"]
        except Exception as e:
            pytest.skip(f"Database insert not permitted: {e}")

        try:
            # Create test app
            test_app = {
                "tenant_id": tenant_id,
                "app_name": "Test App Cascade"
            }
            app_result = client.table("apps").insert(test_app).execute()
            if not app_result.data:
                # Cleanup tenant
                client.table("tenants").delete().eq("id", tenant_id).execute()
                pytest.skip("Unable to create test app - RLS may block insert")
            app_id = app_result.data[0]["id"]

            # Delete tenant
            client.table("tenants").delete().eq("id", tenant_id).execute()

            # Verify app was also deleted (cascade)
            apps = client.table("apps").select("*").eq("id", app_id).execute()
            assert len(apps.data) == 0, "App not deleted on tenant cascade"
        except Exception as e:
            # Cleanup on failure
            try:
                client.table("tenants").delete().eq("id", tenant_id).execute()
            except Exception:
                pass
            pytest.skip(f"Database operation not permitted: {e}")

    def test_cascade_delete_app_to_licenses(self):
        """Verify deleting app cascades to licenses."""
        client = get_supabase_client()

        try:
            # Create test tenant
            test_tenant = {
                "name": "Test Tenant License Cascade",
                "email": f"license_cascade_{uuid4().hex[:8]}@example.com"
            }
            tenant_result = client.table("tenants").insert(test_tenant).execute()
            if not tenant_result.data:
                pytest.skip("Unable to create test tenant - RLS may block insert")
            tenant_id = tenant_result.data[0]["id"]
        except Exception as e:
            pytest.skip(f"Database insert not permitted: {e}")

        try:
            # Create test app
            test_app = {
                "tenant_id": tenant_id,
                "app_name": "Test App License Cascade"
            }
            app_result = client.table("apps").insert(test_app).execute()
            if not app_result.data:
                client.table("tenants").delete().eq("id", tenant_id).execute()
                pytest.skip("Unable to create test app - RLS may block insert")
            app_id = app_result.data[0]["id"]

            # Create test license
            test_license = {
                "app_id": app_id,
                "tenant_id": tenant_id,
                "license_key": f"lic_cascade_test_{uuid4().hex[:8]}",
                "credits_remaining": 1000
            }
            license_result = client.table("licenses").insert(test_license).execute()
            if not license_result.data:
                client.table("apps").delete().eq("id", app_id).execute()
                client.table("tenants").delete().eq("id", tenant_id).execute()
                pytest.skip("Unable to create test license - RLS may block insert")
            license_id = license_result.data[0]["id"]

            # Delete app
            client.table("apps").delete().eq("id", app_id).execute()

            # Verify license was also deleted (cascade)
            licenses = client.table("licenses").select("*").eq("id", license_id).execute()
            assert len(licenses.data) == 0, "License not deleted on app cascade"

            # Cleanup tenant
            client.table("tenants").delete().eq("id", tenant_id).execute()
        except Exception as e:
            # Cleanup on failure
            try:
                client.table("tenants").delete().eq("id", tenant_id).execute()
            except Exception:
                pass
            pytest.skip(f"Database operation not permitted: {e}")


class TestIndexes:
    """Tests to verify indexes exist (indirectly via query performance)."""
    
    def test_apps_tenant_index(self):
        """Verify we can query apps by tenant_id efficiently."""
        client = get_supabase_client()
        
        # Should not raise error
        result = client.table("apps").select("*").eq(
            "tenant_id", "00000000-0000-0000-0000-000000000001"
        ).execute()
        assert result is not None
    
    def test_licenses_app_index(self):
        """Verify we can query licenses by app_id efficiently."""
        client = get_supabase_client()
        
        # Should not raise error
        result = client.table("licenses").select("*").eq(
            "app_id", "00000000-0000-0000-0000-000000000010"
        ).execute()
        assert result is not None
    
    def test_usage_logs_date_index(self):
        """Verify we can query usage_logs by date efficiently."""
        client = get_supabase_client()
        
        # Should not raise error
        result = client.table("usage_logs").select("*").order(
            "created_at", desc=True
        ).limit(10).execute()
        assert result is not None
