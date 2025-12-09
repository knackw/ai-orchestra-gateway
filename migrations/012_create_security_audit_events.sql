-- Migration: Create security_audit_events table for frontend security auditing
-- Version: 012
-- Date: 2025-12-08
-- Description: SEC-020 - Frontend Audit Logging for security-relevant user actions

-- ============================================================================
-- CREATE SECURITY_AUDIT_EVENTS TABLE
-- ============================================================================

-- Security audit events track all security-relevant frontend actions
CREATE TABLE IF NOT EXISTS security_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User/Tenant association
    user_id UUID,  -- NULL for unauthenticated events (login failures)
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,  -- NULL for unauthenticated events

    -- Event details
    event_type TEXT NOT NULL,  -- LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, etc.
    event_category TEXT NOT NULL,  -- 'authentication', 'authorization', 'settings', 'admin'
    severity TEXT NOT NULL DEFAULT 'info',  -- 'info', 'warning', 'critical'

    -- Client metadata
    ip_address INET,
    user_agent TEXT,
    client_version TEXT,

    -- Event context (JSON for flexible schema)
    details JSONB DEFAULT '{}'::jsonb,

    -- Success/Failure
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,

    -- Timestamp (immutable, no updated_at)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast querying and analytics
CREATE INDEX IF NOT EXISTS idx_security_audit_events_user ON security_audit_events(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_tenant ON security_audit_events(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_type ON security_audit_events(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_category ON security_audit_events(event_category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_severity ON security_audit_events(severity, created_at DESC) WHERE severity IN ('warning', 'critical');
CREATE INDEX IF NOT EXISTS idx_security_audit_events_date ON security_audit_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_ip ON security_audit_events(ip_address, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_failures ON security_audit_events(event_type, success, created_at DESC) WHERE success = false;

-- Enable Row Level Security
ALTER TABLE security_audit_events ENABLE ROW LEVEL SECURITY;

-- Policy: Allow INSERT only (for audit service)
DROP POLICY IF EXISTS security_audit_events_insert_only ON security_audit_events;
CREATE POLICY security_audit_events_insert_only ON security_audit_events
    FOR INSERT
    WITH CHECK (true);

-- Policy: Allow SELECT for analytics (authenticated users see their own events)
DROP POLICY IF EXISTS security_audit_events_select_own ON security_audit_events;
CREATE POLICY security_audit_events_select_own ON security_audit_events
    FOR SELECT
    USING (
        -- Service role can see everything
        auth.role() = 'service_role'
        OR
        -- Users can see their own events
        user_id = auth.uid()::uuid
    );

-- Policy: Prevent UPDATE (immutability)
DROP POLICY IF EXISTS security_audit_events_immutable ON security_audit_events;
CREATE POLICY security_audit_events_immutable ON security_audit_events
    FOR UPDATE
    USING (false);

-- Policy: Prevent DELETE (immutability)
DROP POLICY IF EXISTS security_audit_events_no_delete ON security_audit_events;
CREATE POLICY security_audit_events_no_delete ON security_audit_events
    FOR DELETE
    USING (false);

-- Comments
COMMENT ON TABLE security_audit_events IS 'Immutable audit trail of security-relevant frontend events. UPDATE and DELETE operations are blocked via RLS policies.';
COMMENT ON COLUMN security_audit_events.user_id IS 'User who performed the action (NULL for unauthenticated events)';
COMMENT ON COLUMN security_audit_events.tenant_id IS 'Tenant associated with the event (NULL for unauthenticated events)';
COMMENT ON COLUMN security_audit_events.event_type IS 'Specific event type (LOGIN_SUCCESS, LOGOUT, PASSWORD_CHANGE, etc.)';
COMMENT ON COLUMN security_audit_events.event_category IS 'High-level category: authentication, authorization, settings, admin';
COMMENT ON COLUMN security_audit_events.severity IS 'Event severity: info, warning, critical';
COMMENT ON COLUMN security_audit_events.ip_address IS 'Client IP address for security tracking';
COMMENT ON COLUMN security_audit_events.user_agent IS 'Browser user agent string';
COMMENT ON COLUMN security_audit_events.details IS 'Additional event context as JSON';
COMMENT ON COLUMN security_audit_events.success IS 'Whether the action succeeded';
COMMENT ON COLUMN security_audit_events.error_message IS 'Error message if action failed';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
BEGIN
    -- Verify table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'security_audit_events') THEN
        RAISE EXCEPTION 'security_audit_events table not created';
    END IF;

    -- Verify indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'security_audit_events' AND indexname = 'idx_security_audit_events_user') THEN
        RAISE EXCEPTION 'User index not created';
    END IF;

    RAISE NOTICE '✅ Migration 012 completed successfully';
    RAISE NOTICE '   - Created security_audit_events table';
    RAISE NOTICE '   - Added 8 performance indexes';
    RAISE NOTICE '   - Enabled RLS with immutability policies';
END $$;
