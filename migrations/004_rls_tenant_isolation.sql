-- Migration: Enable RLS and create policies for tenant isolation
-- Version: 004
-- Date: 2025-12-05
-- Description: Enforces strict tenant isolation using Row Level Security

-- ============================================================================
-- PART 1: ENABLE RLS ON ALL TABLES
-- ============================================================================

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;
-- usage_logs already has RLS enabled from migration 003

-- ============================================================================
-- PART 2: TENANTS TABLE POLICIES
-- ============================================================================

-- Policy: Tenants can SELECT their own record
DROP POLICY IF EXISTS tenants_select_own ON tenants;
CREATE POLICY tenants_select_own ON tenants
    FOR SELECT
    USING (id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Service role can SELECT all (for admin)
DROP POLICY IF EXISTS tenants_service_select_all ON tenants;
CREATE POLICY tenants_service_select_all ON tenants
    FOR SELECT
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Policy: Tenants can UPDATE their own record
DROP POLICY IF EXISTS tenants_update_own ON tenants;
CREATE POLICY tenants_update_own ON tenants
    FOR UPDATE
    USING (id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: No DELETE for tenants (admin only via service role)
DROP POLICY IF EXISTS tenants_no_delete ON tenants;
CREATE POLICY tenants_no_delete ON tenants
    FOR DELETE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- ============================================================================
-- PART 3: APPS TABLE POLICIES
-- ============================================================================

-- Policy: Tenants can SELECT their own apps
DROP POLICY IF EXISTS apps_select_own ON apps;
CREATE POLICY apps_select_own ON apps
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Service role can SELECT all
DROP POLICY IF EXISTS apps_service_select_all ON apps;
CREATE POLICY apps_service_select_all ON apps
    FOR SELECT
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Policy: Tenants can INSERT apps for themselves
DROP POLICY IF EXISTS apps_insert_own ON apps;
CREATE POLICY apps_insert_own ON apps
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Tenants can UPDATE their own apps
DROP POLICY IF EXISTS apps_update_own ON apps;
CREATE POLICY apps_update_own ON apps
    FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Tenants can DELETE their own apps (soft delete)
DROP POLICY IF EXISTS apps_delete_own ON apps;
CREATE POLICY apps_delete_own ON apps
    FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- ============================================================================
-- PART 4: LICENSES TABLE POLICIES
-- ============================================================================

-- Policy: Tenants can SELECT licenses for their apps
DROP POLICY IF EXISTS licenses_select_own ON licenses;
CREATE POLICY licenses_select_own ON licenses
    FOR SELECT
    USING (app_id IN (
        SELECT id FROM apps WHERE tenant_id = current_setting('app.current_tenant_id', true)::uuid
    ));

-- Policy: Service role can SELECT all
DROP POLICY IF EXISTS licenses_service_select_all ON licenses;
CREATE POLICY licenses_service_select_all ON licenses
    FOR SELECT
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Policy: Tenants can INSERT licenses for their apps
DROP POLICY IF EXISTS licenses_insert_own ON licenses;
CREATE POLICY licenses_insert_own ON licenses
    FOR INSERT
    WITH CHECK (app_id IN (
        SELECT id FROM apps WHERE tenant_id = current_setting('app.current_tenant_id', true)::uuid
    ));

-- Policy: Tenants can UPDATE their licenses
DROP POLICY IF EXISTS licenses_update_own ON licenses;
CREATE POLICY licenses_update_own ON licenses
    FOR UPDATE
    USING (app_id IN (
        SELECT id FROM apps WHERE tenant_id = current_setting('app.current_tenant_id', true)::uuid
    ));

-- Policy: Tenants can DELETE their licenses
DROP POLICY IF EXISTS licenses_delete_own ON licenses;
CREATE POLICY licenses_delete_own ON licenses
    FOR DELETE
    USING (app_id IN (
        SELECT id FROM apps WHERE tenant_id = current_setting('app.current_tenant_id', true)::uuid
    ));

-- ============================================================================
-- PART 5: USAGE LOGS POLICIES (UPDATE EXISTING)
-- ============================================================================

-- Update: Tenants can only SELECT their own logs
DROP POLICY IF EXISTS usage_logs_select_all ON usage_logs; -- Drop old permissive policy
DROP POLICY IF EXISTS usage_logs_select_own ON usage_logs;

CREATE POLICY usage_logs_select_own ON usage_logs
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Service role can SELECT all
DROP POLICY IF EXISTS usage_logs_service_select_all ON usage_logs;
CREATE POLICY usage_logs_service_select_all ON usage_logs
    FOR SELECT
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Keep existing: INSERT allowed for all (logging service needs to write)
-- Note: Ideally logging service uses a specific role, but for now we keep the existing INSERT policy
-- which allows INSERT with CHECK(true). We might want to restrict this later.

-- ============================================================================
-- PART 6: HELPER FUNCTION FOR CONTEXT SETTING
-- ============================================================================

CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', p_tenant_id::text, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION set_tenant_context IS 'Sets the current tenant ID for RLS policies';
