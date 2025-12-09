-- Migration 010: Add Role-Based Access Control (RBAC)
-- Part of ADMIN-008
--
-- Creates roles table and user_roles junction table for multi-tenant RBAC

-- Create roles enum type
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('owner', 'admin', 'member', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create roles table for custom role definitions (future extensibility)
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    role user_role NOT NULL DEFAULT 'viewer',
    custom_role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    granted_by UUID,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique user-tenant combination
    UNIQUE(user_id, tenant_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_tenant_id ON user_roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role);

-- Insert default system roles
INSERT INTO roles (name, description, permissions, is_system_role) VALUES
    ('owner', 'Full access to tenant resources, can delete tenant', '["*"]'::jsonb, TRUE),
    ('admin', 'Manage users, apps, and settings', '["users:*", "apps:*", "settings:*", "analytics:read"]'::jsonb, TRUE),
    ('member', 'Create and manage own apps', '["apps:create", "apps:read", "apps:update", "analytics:read"]'::jsonb, TRUE),
    ('viewer', 'Read-only access', '["apps:read", "analytics:read"]'::jsonb, TRUE)
ON CONFLICT (name) DO NOTHING;

-- Enable RLS on user_roles
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- RLS policies for user_roles
CREATE POLICY "user_roles_tenant_isolation" ON user_roles
    FOR ALL
    USING (tenant_id::text = current_setting('app.current_tenant_id', true));

-- Service role bypass for user_roles
CREATE POLICY "user_roles_service_role_bypass" ON user_roles
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Function to check if user has permission
CREATE OR REPLACE FUNCTION has_permission(
    p_user_id UUID,
    p_tenant_id UUID,
    p_permission TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_role user_role;
    v_permissions JSONB;
BEGIN
    -- Get user's role for tenant
    SELECT role INTO v_role
    FROM user_roles
    WHERE user_id = p_user_id
      AND tenant_id = p_tenant_id
      AND is_active = TRUE
      AND (expires_at IS NULL OR expires_at > NOW());

    IF v_role IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Owner has all permissions
    IF v_role = 'owner' THEN
        RETURN TRUE;
    END IF;

    -- Get permissions for role
    SELECT permissions INTO v_permissions
    FROM roles
    WHERE name = v_role::text;

    -- Check for wildcard or specific permission
    IF v_permissions ? '*' THEN
        RETURN TRUE;
    END IF;

    -- Check for exact match or wildcard match (e.g., "apps:*" matches "apps:delete")
    RETURN v_permissions ? p_permission
        OR v_permissions ? (split_part(p_permission, ':', 1) || ':*');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's role for a tenant
CREATE OR REPLACE FUNCTION get_user_role(
    p_user_id UUID,
    p_tenant_id UUID
) RETURNS user_role AS $$
DECLARE
    v_role user_role;
BEGIN
    SELECT role INTO v_role
    FROM user_roles
    WHERE user_id = p_user_id
      AND tenant_id = p_tenant_id
      AND is_active = TRUE
      AND (expires_at IS NULL OR expires_at > NOW());

    RETURN v_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to assign role to user
CREATE OR REPLACE FUNCTION assign_role(
    p_user_id UUID,
    p_tenant_id UUID,
    p_role user_role,
    p_granted_by UUID DEFAULT NULL,
    p_expires_at TIMESTAMPTZ DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_role_id UUID;
BEGIN
    INSERT INTO user_roles (user_id, tenant_id, role, granted_by, expires_at)
    VALUES (p_user_id, p_tenant_id, p_role, p_granted_by, p_expires_at)
    ON CONFLICT (user_id, tenant_id)
    DO UPDATE SET
        role = p_role,
        granted_by = p_granted_by,
        expires_at = p_expires_at,
        is_active = TRUE,
        updated_at = NOW()
    RETURNING id INTO v_role_id;

    RETURN v_role_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to revoke user's role
CREATE OR REPLACE FUNCTION revoke_role(
    p_user_id UUID,
    p_tenant_id UUID
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE user_roles
    SET is_active = FALSE,
        updated_at = NOW()
    WHERE user_id = p_user_id
      AND tenant_id = p_tenant_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_user_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_roles_updated_at ON user_roles;
CREATE TRIGGER user_roles_updated_at
    BEFORE UPDATE ON user_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_roles_updated_at();

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_roles TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON roles TO service_role;
GRANT EXECUTE ON FUNCTION has_permission TO service_role;
GRANT EXECUTE ON FUNCTION get_user_role TO service_role;
GRANT EXECUTE ON FUNCTION assign_role TO service_role;
GRANT EXECUTE ON FUNCTION revoke_role TO service_role;
