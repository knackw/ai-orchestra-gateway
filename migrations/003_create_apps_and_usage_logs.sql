-- Migration: Create apps and usage_logs tables for multi-tenant architecture
-- Version: 003
-- Date: 2025-12-05
-- Description: Extends schema to 3-tier (tenant → app → license) with audit logging

-- ============================================================================
-- PART 1: CREATE APPS TABLE
-- ============================================================================

-- Apps represent individual applications/products owned by tenants
CREATE TABLE IF NOT EXISTS apps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    app_name TEXT NOT NULL,
    allowed_origins TEXT[],  -- CORS whitelist for frontend apps
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_apps_tenant ON apps(tenant_id);
CREATE INDEX IF NOT EXISTS idx_apps_active ON apps(is_active) WHERE is_active = true;

-- Trigger for auto-updating updated_at
DROP TRIGGER IF EXISTS update_apps_updated_at ON apps;
CREATE TRIGGER update_apps_updated_at
    BEFORE UPDATE ON apps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE apps IS 'Applications/products owned by tenants. Each tenant can have multiple apps.';
COMMENT ON COLUMN apps.tenant_id IS 'Owner tenant of this application';
COMMENT ON COLUMN apps.app_name IS 'Human-readable name of the application';
COMMENT ON COLUMN apps.allowed_origins IS 'CORS whitelist (array of URLs allowed to call this app API)';
COMMENT ON COLUMN apps.is_active IS 'Whether this app is currently active (soft delete support)';

-- ============================================================================
-- PART 2: MODIFY LICENSES TABLE (ADD APP_ID)
-- ============================================================================

-- Add app_id column to licenses (nullable initially for migration)
ALTER TABLE licenses ADD COLUMN IF NOT EXISTS app_id UUID REFERENCES apps(id) ON DELETE CASCADE;

-- Create index for app lookups
CREATE INDEX IF NOT EXISTS idx_licenses_app ON licenses(app_id);

-- Add comment
COMMENT ON COLUMN licenses.app_id IS 'Application that this license belongs to (3-tier: tenant → app → license)';

-- ============================================================================
-- PART 3: CREATE USAGE_LOGS TABLE (IMMUTABLE AUDIT TRAIL)
-- ============================================================================

-- Usage logs are immutable audit records of all AI API calls
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys (denormalized for fast analytics)
    license_id UUID NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    app_id UUID NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Request details
    prompt_length INTEGER NOT NULL,
    pii_detected BOOLEAN DEFAULT false NOT NULL,
    provider TEXT NOT NULL,  -- 'anthropic', 'scaleway'
    model TEXT,  -- 'claude-3-5-sonnet-20241022', 'llama-3.1-70b', etc.
    
    -- Response details
    tokens_used INTEGER NOT NULL,
    credits_deducted INTEGER NOT NULL,
    response_status TEXT NOT NULL,  -- 'success', 'error'
    error_type TEXT,  -- NULL if success, otherwise error code
    
    -- Timestamp (immutable, no updated_at)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_usage_logs_license ON usage_logs(license_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_logs_app ON usage_logs(app_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_logs_tenant ON usage_logs(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_logs_date ON usage_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_logs_provider ON usage_logs(provider, created_at DESC);

-- Enable Row Level Security
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Allow INSERT only (for logging service)
DROP POLICY IF EXISTS usage_logs_insert_only ON usage_logs;
CREATE POLICY usage_logs_insert_only ON usage_logs
    FOR INSERT
    WITH CHECK (true);

-- Policy: Allow SELECT for analytics
DROP POLICY IF EXISTS usage_logs_select_all ON usage_logs;
CREATE POLICY usage_logs_select_all ON usage_logs
    FOR SELECT
    USING (true);

-- Policy: Prevent UPDATE (immutability)
DROP POLICY IF EXISTS usage_logs_immutable ON usage_logs;
CREATE POLICY usage_logs_immutable ON usage_logs
    FOR UPDATE
    USING (false);

-- Policy: Prevent DELETE (immutability)
DROP POLICY IF EXISTS usage_logs_no_delete ON usage_logs;
CREATE POLICY usage_logs_no_delete ON usage_logs
    FOR DELETE
    USING (false);

-- Comments
COMMENT ON TABLE usage_logs IS 'Immutable audit trail of all AI API calls. UPDATE and DELETE operations are blocked via RLS policies.';
COMMENT ON COLUMN usage_logs.license_id IS 'License used for this API call';
COMMENT ON COLUMN usage_logs.app_id IS 'Application that made this API call';
COMMENT ON COLUMN usage_logs.tenant_id IS 'Tenant that owns the app (denormalized for fast queries)';
COMMENT ON COLUMN usage_logs.pii_detected IS 'TRUE if DataPrivacyShield detected and removed PII from prompt';
COMMENT ON COLUMN usage_logs.provider IS 'AI provider used (anthropic, scaleway)';
COMMENT ON COLUMN usage_logs.model IS 'Specific AI model identifier';
COMMENT ON COLUMN usage_logs.tokens_used IS 'Number of tokens consumed by AI provider';
COMMENT ON COLUMN usage_logs.credits_deducted IS 'Credits charged to license';
COMMENT ON COLUMN usage_logs.response_status IS 'success or error';
COMMENT ON COLUMN usage_logs.error_type IS 'Error code if response_status is error, NULL otherwise';

-- ============================================================================
-- PART 4: MIGRATE DEMO DATA
-- ============================================================================

-- Create demo app for demo tenant
INSERT INTO apps (id, tenant_id, app_name, allowed_origins)
VALUES (
    '00000000-0000-0000-0000-000000000010'::UUID,
    '00000000-0000-0000-0000-000000000001'::UUID,  -- Demo tenant
    'Demo App - AGB Generator',
    ARRAY['http://localhost:3000', 'http://localhost:8000', 'https://demo.example.com']
)
ON CONFLICT (id) DO NOTHING;

-- Migrate existing licenses to demo app
UPDATE licenses
SET app_id = '00000000-0000-0000-0000-000000000010'::UUID
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'::UUID
  AND app_id IS NULL;

-- Insert demo usage logs (for testing analytics)
INSERT INTO usage_logs (license_id, app_id, tenant_id, prompt_length, pii_detected, provider, model, tokens_used, credits_deducted, response_status)
SELECT 
    l.id as license_id,
    '00000000-0000-0000-0000-000000000010'::UUID as app_id,
    '00000000-0000-0000-0000-000000000001'::UUID as tenant_id,
    (50 + (random() * 200)::INTEGER) as prompt_length,  -- Random 50-250
    (random() > 0.8) as pii_detected,  -- 20% chance
    CASE WHEN random() > 0.5 THEN 'anthropic' ELSE 'scaleway' END as provider,
    CASE WHEN random() > 0.5 
        THEN 'claude-3-5-sonnet-20241022' 
        ELSE 'llama-3.1-70b' 
    END as model,
    (50 + (random() * 150)::INTEGER) as tokens_used,  -- Random 50-200
    (50 + (random() * 150)::INTEGER) as credits_deducted,
    CASE WHEN random() > 0.95 THEN 'error' ELSE 'success' END as response_status
FROM licenses l
CROSS JOIN generate_series(1, 10)  -- Create 10 demo log entries
WHERE l.license_key = 'lic_demo_valid_123';

-- ============================================================================
-- PART 5: VERIFICATION QUERIES
-- ============================================================================

-- Verify apps table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM apps WHERE id = '00000000-0000-0000-0000-000000000010'::UUID) THEN
        RAISE EXCEPTION 'Demo app not created';
    END IF;
END $$;

-- Verify licenses migration
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM licenses WHERE tenant_id = '00000000-0000-0000-0000-000000000001'::UUID AND app_id IS NULL) THEN
        RAISE EXCEPTION 'Licenses not migrated to demo app';
    END IF;
END $$;

-- Verify usage_logs
DO $$
DECLARE
    log_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO log_count FROM usage_logs;
    IF log_count < 5 THEN
        RAISE WARNING 'Only % usage log entries created (expected at least 5)', log_count;
    END IF;
END $$;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed successfully';
    RAISE NOTICE '   - Created apps table with % entries', (SELECT COUNT(*) FROM apps);
    RAISE NOTICE '   - Updated licenses table (app_id column added)';
    RAISE NOTICE '   - Created usage_logs table with % entries', (SELECT COUNT(*) FROM usage_logs);
    RAISE NOTICE '   - Migrated % licenses to demo app', (SELECT COUNT(*) FROM licenses WHERE app_id IS NOT NULL);
END $$;
