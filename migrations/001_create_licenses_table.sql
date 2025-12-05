-- Migration: Create licenses table for API key validation
-- Date: 2025-12-03
-- Version: 0.1.6

-- Create tenants table (if not exists)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create licenses table
CREATE TABLE IF NOT EXISTS licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_key TEXT UNIQUE NOT NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    credits_remaining INTEGER DEFAULT 1000 NOT NULL,
    credits_total INTEGER DEFAULT 1000 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fast license_key lookups
CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key);

-- Create index for tenant lookups
CREATE INDEX IF NOT EXISTS idx_licenses_tenant ON licenses(tenant_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to licenses table
DROP TRIGGER IF EXISTS update_licenses_updated_at ON licenses;
CREATE TRIGGER update_licenses_updated_at
    BEFORE UPDATE ON licenses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to tenants table  
DROP TRIGGER IF EXISTS update_tenants_updated_at ON tenants;
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert demo tenant for testing
INSERT INTO tenants (id, name, email)
VALUES (
    '00000000-0000-0000-0000-000000000001'::UUID,
    'Demo Tenant',
    'demo@example.com'
)
ON CONFLICT (email) DO NOTHING;

-- Insert demo license keys for testing
INSERT INTO licenses (license_key, tenant_id, is_active, expires_at, credits_remaining, credits_total)
VALUES
    -- Valid license (active, no expiry)
    ('lic_demo_valid_123', '00000000-0000-0000-0000-000000000001'::UUID, true, NULL, 1000, 1000),
    -- Valid license (active, expires in future)
    ('lic_demo_expiring_456', '00000000-0000-0000-0000-000000000001'::UUID, true, NOW() + INTERVAL '30 days', 500, 1000),
    -- Inactive license
    ('lic_demo_inactive_789', '00000000-0000-0000-0000-000000000001'::UUID, false, NULL, 100, 1000),
    -- Expired license
    ('lic_demo_expired_012', '00000000-0000-0000-0000-000000000001'::UUID, true, NOW() - INTERVAL '1 day', 1000, 1000),
    -- License with no credits
    ('lic_demo_nocredits_345', '00000000-0000-0000-0000-000000000001'::UUID, true, NULL, 0, 1000)
ON CONFLICT (license_key) DO NOTHING;

-- Add comment
COMMENT ON TABLE licenses IS 'API license keys for tenant authentication and billing';
COMMENT ON COLUMN licenses.license_key IS 'Unique license key for API authentication';
COMMENT ON COLUMN licenses.is_active IS 'Whether the license is currently active';
COMMENT ON COLUMN licenses.expires_at IS 'License expiration date (NULL = never expires)';
COMMENT ON COLUMN licenses.credits_remaining IS 'Remaining API credits for this license';
COMMENT ON COLUMN licenses.credits_total IS 'Total API credits allocated to this license';
