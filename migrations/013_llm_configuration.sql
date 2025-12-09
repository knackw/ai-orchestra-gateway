-- Migration: LLM Configuration Schema
-- Ermöglicht Tenant-spezifische LLM-Einstellungen
-- Version: DB-010
-- Date: 2025-12-08

-- Enum für LLM Provider
CREATE TYPE llm_provider AS ENUM ('anthropic', 'scaleway', 'vertex_claude', 'vertex_gemini', 'openai');

-- Enum für Priorität
CREATE TYPE provider_priority AS ENUM ('primary', 'secondary', 'fallback');

-- Haupt-Konfigurationstabelle
CREATE TABLE IF NOT EXISTS llm_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Provider Settings
    provider llm_provider NOT NULL DEFAULT 'anthropic',
    model VARCHAR(100) NOT NULL,
    priority provider_priority DEFAULT 'primary',

    -- Generation Parameters
    max_tokens INTEGER DEFAULT 1024,
    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
    top_p DECIMAL(3,2) DEFAULT 1.0 CHECK (top_p >= 0 AND top_p <= 1),

    -- Rate Limits
    requests_per_minute INTEGER DEFAULT 60,
    tokens_per_minute INTEGER DEFAULT 100000,

    -- Feature Flags
    streaming_enabled BOOLEAN DEFAULT true,
    vision_enabled BOOLEAN DEFAULT false,

    -- DSGVO
    eu_only BOOLEAN DEFAULT true,
    data_residency VARCHAR(10) DEFAULT 'EU',

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(tenant_id, name),
    UNIQUE(tenant_id, is_default) WHERE is_default = true
);

-- Indexes
CREATE INDEX idx_llm_config_tenant ON llm_configurations(tenant_id);
CREATE INDEX idx_llm_config_provider ON llm_configurations(provider);
CREATE INDEX idx_llm_config_active ON llm_configurations(is_active);

-- RLS
ALTER TABLE llm_configurations ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Tenants can only see their own configurations
CREATE POLICY llm_config_tenant_isolation ON llm_configurations
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::uuid
        OR current_setting('app.bypass_rls', true) = 'true'
    );

-- RLS Policy: Service role can see all
CREATE POLICY llm_config_service_role ON llm_configurations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Trigger für updated_at
CREATE TRIGGER update_llm_configurations_updated_at
    BEFORE UPDATE ON llm_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Default-Konfiguration für System
INSERT INTO llm_configurations (tenant_id, name, description, provider, model, is_default, is_active)
VALUES (NULL, 'System Default', 'Systemweite Standard-Konfiguration', 'vertex_claude', 'claude-3-5-sonnet-v2@20241022', true, true);

-- Comments
COMMENT ON TABLE llm_configurations IS 'Tenant-specific LLM configuration and model preferences';
COMMENT ON COLUMN llm_configurations.tenant_id IS 'Reference to tenant, NULL for system-wide defaults';
COMMENT ON COLUMN llm_configurations.provider IS 'LLM provider selection';
COMMENT ON COLUMN llm_configurations.priority IS 'Provider priority for fallback handling';
COMMENT ON COLUMN llm_configurations.eu_only IS 'Enforce EU-only data processing (DSGVO compliance)';
COMMENT ON COLUMN llm_configurations.data_residency IS 'Data residency requirement (e.g., EU, US, GLOBAL)';
