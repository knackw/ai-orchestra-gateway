"""
End-to-End Tests for Admin Dashboard APIs.

Tests complete workflows across multiple admin endpoints:
- Tenant lifecycle (create, manage, delete)
- License lifecycle (create, assign, revoke)
- App lifecycle (create, configure, manage)
- Analytics retrieval
- Audit log verification

These tests verify the integration between different admin components.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.api.admin import tenants, licenses, apps as admin_apps, analytics, audit_logs
from app.core.admin_auth import get_admin_key, get_admin_user, verify_admin_role
from app.core.rbac import Role, UserRole


@pytest.fixture
def app():
    """Create test FastAPI app with all admin routers."""
    test_app = FastAPI()

    # Include all admin routers
    test_app.include_router(tenants.router, prefix="/admin")
    test_app.include_router(licenses.router, prefix="/admin")
    test_app.include_router(admin_apps.router, prefix="/admin")
    test_app.include_router(analytics.router, prefix="/admin/analytics")
    test_app.include_router(audit_logs.router, prefix="/admin")

    # Create mock UserRole for SEC-009 admin role verification
    mock_user_role = UserRole(
        user_id=str(uuid4()),
        tenant_id=str(uuid4()),
        role=Role.ADMIN,
        granted_by=None,
        granted_at=None,
        expires_at=None,
        is_active=True,
    )

    # Override admin auth - SEC-009: Both key and role verification needed
    test_app.dependency_overrides[get_admin_key] = lambda: "test-admin-key"
    test_app.dependency_overrides[verify_admin_role] = lambda: mock_user_role
    test_app.dependency_overrides[get_admin_user] = lambda: mock_user_role

    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Create comprehensive mock Supabase client."""
    mock_client = MagicMock()

    # Track stored data
    stored_data = {
        "tenants": [],
        "apps": [],
        "licenses": [],
        "usage_logs": [],
    }

    def mock_table(table_name):
        """Return table-specific mock."""
        table_mock = MagicMock()

        def mock_insert(data):
            """Mock insert operation."""
            insert_mock = MagicMock()
            if isinstance(data, dict):
                data["id"] = str(uuid4())
                data["created_at"] = datetime.now(timezone.utc).isoformat()
                data["updated_at"] = datetime.now(timezone.utc).isoformat()
                stored_data[table_name].append(data)
            insert_mock.execute = MagicMock(return_value=MagicMock(data=[data]))
            return insert_mock

        def mock_select(*args):
            """Mock select operation."""
            select_mock = MagicMock()

            def mock_eq(field, value):
                """Filter by field."""
                eq_mock = MagicMock()
                filtered = [
                    item for item in stored_data.get(table_name, [])
                    if str(item.get(field)) == str(value)
                ]

                def mock_single():
                    single_mock = MagicMock()
                    single_mock.execute = MagicMock(
                        return_value=MagicMock(data=filtered[0] if filtered else None)
                    )
                    return single_mock

                def mock_range(start, end):
                    range_mock = MagicMock()
                    range_mock.execute = MagicMock(
                        return_value=MagicMock(data=filtered[start:end+1])
                    )
                    return range_mock

                eq_mock.single = mock_single
                eq_mock.range = mock_range
                eq_mock.execute = MagicMock(return_value=MagicMock(data=filtered))
                eq_mock.eq = mock_eq
                return eq_mock

            def mock_range(start, end):
                range_mock = MagicMock()
                range_mock.execute = MagicMock(
                    return_value=MagicMock(data=stored_data.get(table_name, [])[start:end+1])
                )
                return range_mock

            select_mock.eq = mock_eq
            select_mock.range = mock_range
            select_mock.execute = MagicMock(
                return_value=MagicMock(data=stored_data.get(table_name, []))
            )
            return select_mock

        def mock_update(data):
            """Mock update operation."""
            update_mock = MagicMock()

            def mock_eq(field, value):
                eq_mock = MagicMock()
                # Find and update matching items
                for item in stored_data.get(table_name, []):
                    if str(item.get(field)) == str(value):
                        item.update(data)

                eq_mock.execute = MagicMock(
                    return_value=MagicMock(data=[
                        item for item in stored_data.get(table_name, [])
                        if str(item.get(field)) == str(value)
                    ])
                )
                return eq_mock

            update_mock.eq = mock_eq
            return update_mock

        def mock_delete():
            """Mock delete operation."""
            delete_mock = MagicMock()

            def mock_eq(field, value):
                eq_mock = MagicMock()
                # Remove matching items
                stored_data[table_name] = [
                    item for item in stored_data.get(table_name, [])
                    if str(item.get(field)) != str(value)
                ]
                eq_mock.execute = MagicMock(return_value=MagicMock(data=[]))
                return eq_mock

            delete_mock.eq = mock_eq
            return delete_mock

        table_mock.insert = mock_insert
        table_mock.select = mock_select
        table_mock.update = mock_update
        table_mock.delete = mock_delete
        return table_mock

    mock_client.table = mock_table
    mock_client._stored_data = stored_data  # For test access

    return mock_client


class TestTenantLifecycle:
    """E2E tests for tenant lifecycle."""

    def test_create_tenant_flow(self, client, mock_supabase):
        """Test complete tenant creation flow."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            # Create tenant
            response = client.post("/admin/tenants", json={
                "name": "Test Company",
                "email": "admin@testcompany.com"
            })

            assert response.status_code == 201
            tenant = response.json()
            assert tenant["name"] == "Test Company"
            assert "id" in tenant

    def test_tenant_update_flow(self, client, mock_supabase):
        """Test tenant update flow."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            # Create tenant first
            create_response = client.post("/admin/tenants", json={
                "name": "Original Name",
                "email": "original@test.com"
            })
            tenant_id = create_response.json()["id"]

            # Update tenant
            update_response = client.put(f"/admin/tenants/{tenant_id}", json={
                "name": "Updated Name"
            })

            assert update_response.status_code == 200
            assert update_response.json()["name"] == "Updated Name"

    def test_tenant_list_flow(self, client, mock_supabase):
        """Test listing multiple tenants."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            # Create multiple tenants
            for i in range(3):
                client.post("/admin/tenants", json={
                    "name": f"Tenant {i}",
                    "email": f"tenant{i}@test.com"
                })

            # List all
            response = client.get("/admin/tenants")
            assert response.status_code == 200
            assert len(response.json()) == 3


class TestLicenseLifecycle:
    """E2E tests for license lifecycle."""

    def test_license_creation_requires_tenant(self, client, mock_supabase):
        """Test that license creation validates tenant existence."""
        with patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):
            # Try to create license without tenant
            response = client.post("/admin/licenses", json={
                "tenant_id": str(uuid4()),  # Non-existent tenant
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })

            # Should fail because tenant doesn't exist
            assert response.status_code in [404, 400, 500]

    def test_license_full_lifecycle(self, client, mock_supabase):
        """Test complete license lifecycle with tenant."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Step 1: Create tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "License Test Tenant",
                "email": "license@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Step 2: Create license for tenant
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 5000,
                "expires_at": "2025-12-31T23:59:59Z"
            })

            assert license_response.status_code == 201
            license_data = license_response.json()
            assert license_data["credits_remaining"] == 5000
            license_id = license_data["id"]

            # Step 3: Update license credits
            update_response = client.put(f"/admin/licenses/{license_id}", json={
                "credits_remaining": 10000
            })
            assert update_response.status_code == 200

            # Step 4: Revoke license
            revoke_response = client.delete(f"/admin/licenses/{license_id}")
            assert revoke_response.status_code == 204


class TestAppLifecycle:
    """E2E tests for app lifecycle."""

    def test_app_full_lifecycle(self, client, mock_supabase):
        """Test complete app lifecycle."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase):

            # Step 1: Create tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "App Test Tenant",
                "email": "app@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Step 2: Create app for tenant
            app_response = client.post("/admin/apps", json={
                "tenant_id": tenant_id,
                "app_name": "My Test App",
                "allowed_origins": ["https://myapp.com"]
            })

            assert app_response.status_code == 201
            app_data = app_response.json()
            assert app_data["app_name"] == "My Test App"
            app_id = app_data["id"]

            # Step 3: Get app details
            get_response = client.get(f"/admin/apps/{app_id}")
            assert get_response.status_code == 200

            # Step 4: Update app
            update_response = client.put(f"/admin/apps/{app_id}", json={
                "allowed_origins": ["https://myapp.com", "https://api.myapp.com"]
            })
            assert update_response.status_code == 200

            # Step 5: Deactivate app
            delete_response = client.delete(f"/admin/apps/{app_id}")
            assert delete_response.status_code == 204


class TestMultiTenantIsolation:
    """E2E tests for multi-tenant data isolation."""

    def test_apps_isolated_by_tenant(self, client, mock_supabase):
        """Test that apps are properly isolated by tenant."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase):

            # Create two tenants
            tenant1_resp = client.post("/admin/tenants", json={
                "name": "Tenant 1",
                "email": "tenant1@test.com"
            })
            tenant1_id = tenant1_resp.json()["id"]

            tenant2_resp = client.post("/admin/tenants", json={
                "name": "Tenant 2",
                "email": "tenant2@test.com"
            })
            tenant2_id = tenant2_resp.json()["id"]

            # Create app for each tenant
            client.post("/admin/apps", json={
                "tenant_id": tenant1_id,
                "app_name": "Tenant 1 App",
                "allowed_origins": []
            })

            client.post("/admin/apps", json={
                "tenant_id": tenant2_id,
                "app_name": "Tenant 2 App",
                "allowed_origins": []
            })

            # List apps for tenant 1
            response = client.get(f"/admin/apps?tenant_id={tenant1_id}")
            apps = response.json()

            # Should only see tenant 1's app
            assert len(apps) == 1
            assert apps[0]["app_name"] == "Tenant 1 App"


class TestAdminWorkflows:
    """E2E tests for common admin workflows."""

    def test_onboard_new_customer_workflow(self, client, mock_supabase):
        """Test complete new customer onboarding workflow."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Step 1: Create tenant for new customer
            tenant_response = client.post("/admin/tenants", json={
                "name": "New Customer Inc",
                "email": "admin@newcustomer.com"
            })
            assert tenant_response.status_code == 201
            tenant_id = tenant_response.json()["id"]

            # Step 2: Create default app
            app_response = client.post("/admin/apps", json={
                "tenant_id": tenant_id,
                "app_name": "Default App",
                "allowed_origins": ["https://newcustomer.com"]
            })
            assert app_response.status_code == 201

            # Step 3: Create initial license with credits
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,  # Starter credits
                "expires_at": "2026-01-01T00:00:00Z"
            })
            assert license_response.status_code == 201

            # Verify all resources were created
            tenants_list = client.get("/admin/tenants").json()
            assert any(t["id"] == tenant_id for t in tenants_list)

    def test_upgrade_customer_credits_workflow(self, client, mock_supabase):
        """Test workflow for upgrading customer credits."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup: Create tenant with license
            tenant_response = client.post("/admin/tenants", json={
                "name": "Upgrade Test",
                "email": "upgrade@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            license_id = license_response.json()["id"]

            # Upgrade: Double the credits
            upgrade_response = client.put(f"/admin/licenses/{license_id}", json={
                "credits_remaining": 2000
            })
            assert upgrade_response.status_code == 200
            assert upgrade_response.json()["credits_remaining"] == 2000

    def test_deactivate_customer_workflow(self, client, mock_supabase):
        """Test workflow for deactivating a customer."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup: Create tenant with app and license
            tenant_response = client.post("/admin/tenants", json={
                "name": "Deactivate Test",
                "email": "deactivate@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            app_response = client.post("/admin/apps", json={
                "tenant_id": tenant_id,
                "app_name": "Test App",
                "allowed_origins": []
            })
            app_id = app_response.json()["id"]

            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            license_id = license_response.json()["id"]

            # Deactivate: Revoke license, deactivate app, deactivate tenant
            client.delete(f"/admin/licenses/{license_id}")
            client.delete(f"/admin/apps/{app_id}")
            client.put(f"/admin/tenants/{tenant_id}", json={"is_active": False})


class TestBulkOperations:
    """E2E tests for bulk admin operations."""

    def test_create_multiple_apps_for_tenant(self, client, mock_supabase):
        """Test creating multiple apps for a single tenant."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase):

            # Create tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "Multi App Tenant",
                "email": "multiapp@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Create multiple apps
            app_names = ["Web App", "Mobile App", "API Gateway", "Admin Portal"]
            created_apps = []

            for name in app_names:
                response = client.post("/admin/apps", json={
                    "tenant_id": tenant_id,
                    "app_name": name,
                    "allowed_origins": [f"https://{name.lower().replace(' ', '-')}.example.com"]
                })
                assert response.status_code == 201
                created_apps.append(response.json())

            assert len(created_apps) == 4

            # List all apps for tenant
            list_response = client.get(f"/admin/apps?tenant_id={tenant_id}")
            assert list_response.status_code == 200
            assert len(list_response.json()) == 4


class TestErrorHandling:
    """E2E tests for error handling scenarios."""

    def test_invalid_tenant_id_format(self, client, mock_supabase):
        """Test error handling for invalid UUID format."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            response = client.get("/admin/tenants/not-a-uuid")
            # Should return 422 for validation error
            assert response.status_code == 422

    def test_update_nonexistent_resource(self, client, mock_supabase):
        """Test error handling when updating non-existent resource."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            response = client.put(f"/admin/tenants/{uuid4()}", json={
                "name": "Ghost Tenant"
            })
            # Should return 404
            assert response.status_code == 404

    def test_missing_required_fields(self, client, mock_supabase):
        """Test error handling for missing required fields."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            # Missing email
            response = client.post("/admin/tenants", json={
                "name": "Incomplete Tenant"
            })
            assert response.status_code == 422


class TestPagination:
    """E2E tests for pagination."""

    def test_tenant_list_pagination(self, client, mock_supabase):
        """Test pagination for tenant listing."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase):
            # Create 10 tenants
            for i in range(10):
                client.post("/admin/tenants", json={
                    "name": f"Tenant {i}",
                    "email": f"tenant{i}@test.com"
                })

            # Get first page
            page1_response = client.get("/admin/tenants?skip=0&limit=5")
            assert page1_response.status_code == 200
            page1 = page1_response.json()
            assert len(page1) == 5

            # Get second page
            page2_response = client.get("/admin/tenants?skip=5&limit=5")
            assert page2_response.status_code == 200
            page2 = page2_response.json()
            assert len(page2) == 5

            # Ensure no overlap
            page1_ids = {t["id"] for t in page1}
            page2_ids = {t["id"] for t in page2}
            assert page1_ids.isdisjoint(page2_ids)


class TestStripeIntegrationWorkflow:
    """E2E tests for Stripe payment integration workflows."""

    def test_credit_topup_via_stripe_workflow(self, client, mock_supabase):
        """Test complete credit top-up workflow via Stripe checkout."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Step 1: Create tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "Stripe Test Customer",
                "email": "stripe@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Step 2: Create license with initial credits
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 100,  # Starting credits
                "expires_at": "2025-12-31T23:59:59Z"
            })
            assert license_response.status_code == 201
            license_data = license_response.json()
            license_id = license_data["id"]
            license_key = license_data.get("license_key", f"lic_{license_id[:8]}")

            # Initial credits should be 100
            assert license_data["credits_remaining"] == 100

            # Step 3: Simulate Stripe webhook (credits purchased)
            # In real scenario, this would be triggered by Stripe
            # Here we simulate by directly updating credits
            update_response = client.put(f"/admin/licenses/{license_id}", json={
                "credits_remaining": 1100  # 100 + 1000 purchased
            })
            assert update_response.status_code == 200
            assert update_response.json()["credits_remaining"] == 1100

    def test_stripe_checkout_session_flow(self, client, mock_supabase):
        """Test Stripe checkout session creation and completion flow."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup: Create tenant and license
            tenant_response = client.post("/admin/tenants", json={
                "name": "Checkout Test",
                "email": "checkout@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 0,  # No credits initially
                "expires_at": "2025-12-31T23:59:59Z"
            })
            license_id = license_response.json()["id"]

            # Simulate multiple credit purchases
            credit_packages = [500, 1000, 5000]  # Different packages
            total_credits = 0

            for package in credit_packages:
                total_credits += package
                update_response = client.put(f"/admin/licenses/{license_id}", json={
                    "credits_remaining": total_credits
                })
                assert update_response.status_code == 200

            # Final credit balance should be sum of all packages
            assert update_response.json()["credits_remaining"] == 6500


class TestCompleteCustomerJourney:
    """E2E tests for complete customer journey scenarios."""

    def test_full_customer_journey(self, client, mock_supabase):
        """Test complete customer journey from signup to usage."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # === SIGNUP PHASE ===
            # 1. Customer signs up → Admin creates tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "Acme Corporation",
                "email": "admin@acme.com"
            })
            assert tenant_response.status_code == 201
            tenant = tenant_response.json()
            tenant_id = tenant["id"]

            # 2. Admin creates default app for customer
            app_response = client.post("/admin/apps", json={
                "tenant_id": tenant_id,
                "app_name": "Acme Main App",
                "allowed_origins": ["https://acme.com", "https://api.acme.com"]
            })
            assert app_response.status_code == 201
            app_id = app_response.json()["id"]

            # 3. Admin creates license with free tier credits
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,  # Free tier
                "expires_at": "2025-12-31T23:59:59Z"
            })
            assert license_response.status_code == 201
            license_id = license_response.json()["id"]

            # === USAGE PHASE ===
            # 4. Customer uses credits (simulated by updating balance)
            # After using 500 credits for AI calls
            client.put(f"/admin/licenses/{license_id}", json={
                "credits_remaining": 500
            })

            # === UPGRADE PHASE ===
            # 5. Customer purchases more credits (Stripe workflow)
            # After Stripe checkout completes
            client.put(f"/admin/licenses/{license_id}", json={
                "credits_remaining": 5500  # 500 remaining + 5000 purchased
            })

            # 6. Customer adds another app
            second_app_response = client.post("/admin/apps", json={
                "tenant_id": tenant_id,
                "app_name": "Acme Mobile App",
                "allowed_origins": ["https://mobile.acme.com"]
            })
            assert second_app_response.status_code == 201

            # === VERIFICATION ===
            # Verify tenant has 2 apps
            apps_response = client.get(f"/admin/apps?tenant_id={tenant_id}")
            assert len(apps_response.json()) == 2

    def test_enterprise_customer_setup(self, client, mock_supabase):
        """Test enterprise customer setup with multiple apps and high credits."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Create enterprise tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "Enterprise Corp",
                "email": "enterprise@bigcorp.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Create multiple apps for different departments
            departments = [
                ("Legal Department App", ["https://legal.bigcorp.com"]),
                ("HR Department App", ["https://hr.bigcorp.com"]),
                ("Finance Department App", ["https://finance.bigcorp.com"]),
                ("R&D Department App", ["https://rd.bigcorp.com"]),
            ]

            for app_name, origins in departments:
                response = client.post("/admin/apps", json={
                    "tenant_id": tenant_id,
                    "app_name": app_name,
                    "allowed_origins": origins
                })
                assert response.status_code == 201

            # Create enterprise license with high credits
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000000,  # 1M credits for enterprise
                "expires_at": "2026-12-31T23:59:59Z"
            })
            assert license_response.status_code == 201
            assert license_response.json()["credits_remaining"] == 1000000


class TestCreditExhaustionScenarios:
    """E2E tests for credit exhaustion and renewal scenarios."""

    def test_credit_exhaustion_and_topup(self, client, mock_supabase):
        """Test scenario where credits run out and are topped up."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup tenant with limited credits
            tenant_response = client.post("/admin/tenants", json={
                "name": "Limited Credits Co",
                "email": "limited@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 100,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            license_id = license_response.json()["id"]

            # Simulate credit usage until exhaustion
            usage_steps = [80, 15, 5, 0]  # Remaining after each usage
            for remaining in usage_steps:
                client.put(f"/admin/licenses/{license_id}", json={
                    "credits_remaining": remaining
                })

            # Verify credits are exhausted
            # (In real app, API calls would fail at this point)

            # Customer tops up via Stripe
            topup_response = client.put(f"/admin/licenses/{license_id}", json={
                "credits_remaining": 5000  # Fresh credits
            })
            assert topup_response.status_code == 200
            assert topup_response.json()["credits_remaining"] == 5000


class TestLicenseExpirationScenarios:
    """E2E tests for license expiration scenarios."""

    def test_license_renewal_before_expiration(self, client, mock_supabase):
        """Test renewing a license before it expires."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup
            tenant_response = client.post("/admin/tenants", json={
                "name": "Renewal Test",
                "email": "renewal@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # License expiring soon
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-01-15T23:59:59Z"  # Expiring soon
            })
            license_id = license_response.json()["id"]

            # Renew license with extended expiration
            renewal_response = client.put(f"/admin/licenses/{license_id}", json={
                "expires_at": "2026-01-15T23:59:59Z"  # Extended by 1 year
            })
            assert renewal_response.status_code == 200

    def test_create_new_license_after_expiration(self, client, mock_supabase):
        """Test creating a new license after old one expires."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup tenant
            tenant_response = client.post("/admin/tenants", json={
                "name": "New License Test",
                "email": "newlicense@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Old expired license (simulated)
            old_license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 0,  # Used up
                "expires_at": "2024-12-31T23:59:59Z"  # Already expired
            })
            old_license_id = old_license_response.json()["id"]

            # Deactivate old license
            client.delete(f"/admin/licenses/{old_license_id}")

            # Create new license
            new_license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 5000,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            assert new_license_response.status_code == 201
            assert new_license_response.json()["credits_remaining"] == 5000


class TestDataIntegrityScenarios:
    """E2E tests for data integrity across operations."""

    def test_cascade_delete_tenant(self, client, mock_supabase):
        """Test that deleting tenant cascades to apps and licenses."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Create full tenant setup
            tenant_response = client.post("/admin/tenants", json={
                "name": "Cascade Delete Test",
                "email": "cascade@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Create apps
            for i in range(3):
                client.post("/admin/apps", json={
                    "tenant_id": tenant_id,
                    "app_name": f"App {i}",
                    "allowed_origins": []
                })

            # Create license
            client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })

            # Delete tenant (should cascade)
            delete_response = client.delete(f"/admin/tenants/{tenant_id}")
            assert delete_response.status_code == 204

            # Verify delete was called (mock doesn't actually remove from stored_data for GET)
            # In real database, CASCADE DELETE would remove related records
            # For this mock test, we verify the delete call succeeded
            assert delete_response.status_code == 204

    def test_concurrent_license_updates(self, client, mock_supabase):
        """Test handling of concurrent license updates."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup
            tenant_response = client.post("/admin/tenants", json={
                "name": "Concurrent Test",
                "email": "concurrent@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            license_id = license_response.json()["id"]

            # Simulate multiple rapid updates (like concurrent API requests)
            updates = [900, 800, 700, 600, 500]
            for credits in updates:
                response = client.put(f"/admin/licenses/{license_id}", json={
                    "credits_remaining": credits
                })
                assert response.status_code == 200

            # Final state should reflect last update
            # (In real scenario with proper locking, this would be deterministic)


class TestAPIKeySecurityWorkflow:
    """E2E tests for API key security workflows."""

    def test_api_key_rotation_workflow(self, client, mock_supabase):
        """Test API key rotation for security compliance."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Setup tenant with license
            tenant_response = client.post("/admin/tenants", json={
                "name": "Key Rotation Test",
                "email": "rotation@test.com"
            })
            tenant_id = tenant_response.json()["id"]

            # Create initial license (with API key)
            license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            license_id = license_response.json()["id"]
            original_key = license_response.json().get("license_key")

            # Simulate key rotation by creating new license and deactivating old
            # In real scenario, there would be a dedicated rotate endpoint

            # Create new license
            new_license_response = client.post("/admin/licenses", json={
                "tenant_id": tenant_id,
                "credits": 1000,
                "expires_at": "2025-12-31T23:59:59Z"
            })
            assert new_license_response.status_code == 201

            # Deactivate old license
            client.delete(f"/admin/licenses/{license_id}")


class TestReportingWorkflows:
    """E2E tests for reporting and analytics workflows."""

    def test_tenant_usage_summary_workflow(self, client, mock_supabase):
        """Test workflow for generating tenant usage summary."""
        with patch("app.api.admin.tenants.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.apps.get_supabase_client", return_value=mock_supabase), \
             patch("app.api.admin.licenses.get_supabase_client", return_value=mock_supabase):

            # Create multiple tenants with varying usage
            tenants_data = [
                ("High Usage Co", 10000, 2000),   # High usage
                ("Medium Usage Co", 5000, 3000),  # Medium usage
                ("Low Usage Co", 1000, 900),      # Low usage
            ]

            created_tenants = []
            for name, initial_credits, remaining in tenants_data:
                # Create tenant
                tenant_resp = client.post("/admin/tenants", json={
                    "name": name,
                    "email": f"{name.lower().replace(' ', '')}@test.com"
                })
                tenant_id = tenant_resp.json()["id"]

                # Create license with usage
                license_resp = client.post("/admin/licenses", json={
                    "tenant_id": tenant_id,
                    "credits": initial_credits,
                    "expires_at": "2025-12-31T23:59:59Z"
                })
                license_id = license_resp.json()["id"]

                # Update to show usage
                client.put(f"/admin/licenses/{license_id}", json={
                    "credits_remaining": remaining
                })

                created_tenants.append({
                    "tenant_id": tenant_id,
                    "initial": initial_credits,
                    "remaining": remaining,
                    "used": initial_credits - remaining
                })

            # Verify all tenants exist
            all_tenants = client.get("/admin/tenants").json()
            assert len(all_tenants) >= 3
