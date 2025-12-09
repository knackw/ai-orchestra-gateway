-- Migration: Fix RLS policies to allow full access for service_role
-- Version: 005
-- Date: 2025-12-05
-- Description: Adds missing INSERT/UPDATE/DELETE policies for service_role

-- ============================================================================
-- TENANTS TABLE
-- ============================================================================

-- Allow service_role to INSERT
DROP POLICY IF EXISTS tenants_service_insert ON tenants;
CREATE POLICY tenants_service_insert ON tenants
    FOR INSERT
    WITH CHECK (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Allow service_role to UPDATE
DROP POLICY IF EXISTS tenants_service_update ON tenants;
CREATE POLICY tenants_service_update ON tenants
    FOR UPDATE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Allow service_role to DELETE
DROP POLICY IF EXISTS tenants_service_delete ON tenants;
CREATE POLICY tenants_service_delete ON tenants
    FOR DELETE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- ============================================================================
-- APPS TABLE
-- ============================================================================

-- Allow service_role to INSERT
DROP POLICY IF EXISTS apps_service_insert ON apps;
CREATE POLICY apps_service_insert ON apps
    FOR INSERT
    WITH CHECK (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Allow service_role to UPDATE
DROP POLICY IF EXISTS apps_service_update ON apps;
CREATE POLICY apps_service_update ON apps
    FOR UPDATE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Allow service_role to DELETE
DROP POLICY IF EXISTS apps_service_delete ON apps;
CREATE POLICY apps_service_delete ON apps
    FOR DELETE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- ============================================================================
-- LICENSES TABLE
-- ============================================================================

-- Allow service_role to INSERT
DROP POLICY IF EXISTS licenses_service_insert ON licenses;
CREATE POLICY licenses_service_insert ON licenses
    FOR INSERT
    WITH CHECK (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Allow service_role to UPDATE
DROP POLICY IF EXISTS licenses_service_update ON licenses;
CREATE POLICY licenses_service_update ON licenses
    FOR UPDATE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Allow service_role to DELETE
DROP POLICY IF EXISTS licenses_service_delete ON licenses;
CREATE POLICY licenses_service_delete ON licenses
    FOR DELETE
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- ============================================================================
-- USAGE_LOGS TABLE
-- ============================================================================

-- Allow service_role to INSERT (already allowed by generic insert policy, but good to be explicit)
-- usage_logs_insert_only allows ALL inserts currently.

-- Allow service_role to UPDATE (override immutability for admin if needed, or keep immutable)
-- For now, we keep usage_logs immutable even for admin to ensure audit integrity.
-- If admin needs to correct data, they can use SQL Editor (postgres role).
