-- Migration: LLM Configuration Schema
-- Version: 012 (DB-010)
-- Date: 2025-12-08
-- Description: Tenant-specific LLM configuration with model preferences, generation parameters, and EU compliance settings

-- ============================================================================
-- PART 1: CREATE LLM_CONFIGURATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS llm_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Tenant association (NULL = global/system default)
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

    -- Model identification
    provider TEXT NOT NULL CHECK (provider IN ('anthropic', 'scaleway', 'vertex_ai', 'openai', 'google', 'other')),
    model_id TEXT NOT NULL,
    display_name TEXT NOT NULL,

    -- Status flags
    is_enabled BOOLEAN DEFAULT true,
    is_eu_compliant BOOLEAN DEFAULT false,

    -- Token limits
    max_tokens INTEGER DEFAULT 4096 CHECK (max_tokens > 0 AND max_tokens <= 200000),

    -- Cost structure (in EUR cents per 1000 tokens)
    cost_per_1k_input_tokens DECIMAL(10,4) DEFAULT 0.0000 CHECK (cost_per_1k_input_tokens >= 0),
    cost_per_1k_output_tokens DECIMAL(10,4) DEFAULT 0.0000 CHECK (cost_per_1k_output_tokens >= 0),

    -- Fallback priority (lower = higher priority)
    priority INTEGER DEFAULT 100 CHECK (priority >= 0 AND priority <= 1000),

    -- Model-specific configuration overrides (JSON)
    config_overrides JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(tenant_id, provider, model_id)
);

-- ============================================================================
-- PART 2: CREATE INDEXES
-- ============================================================================

-- Index for tenant lookups
CREATE INDEX IF NOT EXISTS idx_llm_configurations_tenant_id
    ON llm_configurations(tenant_id);

-- Index for provider filtering
CREATE INDEX IF NOT EXISTS idx_llm_configurations_provider
    ON llm_configurations(provider);

-- Index for enabled models
CREATE INDEX IF NOT EXISTS idx_llm_configurations_enabled
    ON llm_configurations(is_enabled)
    WHERE is_enabled = true;

-- Index for EU-compliant models
CREATE INDEX IF NOT EXISTS idx_llm_configurations_eu_compliant
    ON llm_configurations(is_eu_compliant)
    WHERE is_eu_compliant = true;

-- Composite index for priority-based selection
CREATE INDEX IF NOT EXISTS idx_llm_configurations_priority
    ON llm_configurations(tenant_id, is_enabled, priority)
    WHERE is_enabled = true;

-- Index for global defaults
CREATE INDEX IF NOT EXISTS idx_llm_configurations_global
    ON llm_configurations(provider, model_id)
    WHERE tenant_id IS NULL;

-- ============================================================================
-- PART 3: ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE llm_configurations ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PART 4: RLS POLICIES FOR TENANT ISOLATION
-- ============================================================================

-- Policy: Tenants can SELECT their own configurations and global defaults
DROP POLICY IF EXISTS llm_configurations_select_own ON llm_configurations;
CREATE POLICY llm_configurations_select_own ON llm_configurations
    FOR SELECT
    USING (
        -- Tenant's own configurations
        tenant_id = current_setting('app.current_tenant_id', true)::uuid
        OR
        -- Global configurations (NULL tenant_id)
        tenant_id IS NULL
    );

-- Policy: Service role can SELECT all
DROP POLICY IF EXISTS llm_configurations_service_select_all ON llm_configurations;
CREATE POLICY llm_configurations_service_select_all ON llm_configurations
    FOR SELECT
    USING (current_setting('request.jwt.claim.role', true) = 'service_role');

-- Policy: Tenants can INSERT configurations for themselves
DROP POLICY IF EXISTS llm_configurations_insert_own ON llm_configurations;
CREATE POLICY llm_configurations_insert_own ON llm_configurations
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Service role can INSERT (including global configs)
DROP POLICY IF EXISTS llm_configurations_service_insert ON llm_configurations;
CREATE POLICY llm_configurations_service_insert ON llm_configurations
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Policy: Tenants can UPDATE their own configurations
DROP POLICY IF EXISTS llm_configurations_update_own ON llm_configurations;
CREATE POLICY llm_configurations_update_own ON llm_configurations
    FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Service role can UPDATE all
DROP POLICY IF EXISTS llm_configurations_service_update ON llm_configurations;
CREATE POLICY llm_configurations_service_update ON llm_configurations
    FOR UPDATE
    TO service_role
    USING (true);

-- Policy: Tenants can DELETE their own configurations
DROP POLICY IF EXISTS llm_configurations_delete_own ON llm_configurations;
CREATE POLICY llm_configurations_delete_own ON llm_configurations
    FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);

-- Policy: Service role can DELETE all
DROP POLICY IF EXISTS llm_configurations_service_delete ON llm_configurations;
CREATE POLICY llm_configurations_service_delete ON llm_configurations
    FOR DELETE
    TO service_role
    USING (true);

-- ============================================================================
-- PART 5: TRIGGERS
-- ============================================================================

-- Trigger for automatic updated_at timestamp
DROP TRIGGER IF EXISTS llm_configurations_updated_at ON llm_configurations;
CREATE TRIGGER llm_configurations_updated_at
    BEFORE UPDATE ON llm_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PART 6: INSERT DEFAULT GLOBAL CONFIGURATIONS
-- ============================================================================

-- Insert default global configurations for common models
INSERT INTO llm_configurations (
    tenant_id,
    provider,
    model_id,
    display_name,
    is_enabled,
    is_eu_compliant,
    max_tokens,
    cost_per_1k_input_tokens,
    cost_per_1k_output_tokens,
    priority,
    config_overrides
) VALUES
    -- Anthropic Claude 3.5 Sonnet (US)
    (
        NULL,
        'anthropic',
        'claude-3-5-sonnet-20241022',
        'Claude 3.5 Sonnet',
        true,
        false,
        8192,
        0.3000,
        1.5000,
        10,
        '{"supports_vision": true, "region": "us-east-1"}'::jsonb
    ),
    -- Vertex AI Claude 3.5 Sonnet (EU)
    (
        NULL,
        'vertex_ai',
        'claude-3-5-sonnet-v2@20241022',
        'Claude 3.5 Sonnet v2 (EU)',
        true,
        true,
        8192,
        0.3000,
        1.5000,
        1,
        '{"supports_vision": true, "region": "europe-west3", "data_residency": "eu"}'::jsonb
    ),
    -- Vertex AI Claude 3 Opus (EU)
    (
        NULL,
        'vertex_ai',
        'claude-3-opus@20240229',
        'Claude 3 Opus (EU)',
        true,
        true,
        4096,
        1.5000,
        7.5000,
        5,
        '{"supports_vision": true, "region": "europe-west3", "data_residency": "eu"}'::jsonb
    ),
    -- Vertex AI Claude 3 Haiku (EU)
    (
        NULL,
        'vertex_ai',
        'claude-3-haiku@20240307',
        'Claude 3 Haiku (EU)',
        true,
        true,
        4096,
        0.0250,
        0.1250,
        20,
        '{"supports_vision": true, "region": "europe-west3", "data_residency": "eu"}'::jsonb
    ),
    -- Vertex AI Gemini 2.0 Flash (EU)
    (
        NULL,
        'vertex_ai',
        'gemini-2.0-flash-001',
        'Gemini 2.0 Flash (EU)',
        true,
        true,
        8192,
        0.0075,
        0.0300,
        30,
        '{"supports_vision": true, "region": "europe-west3", "data_residency": "eu", "context_window": 1000000}'::jsonb
    ),
    -- Scaleway Llama 3.3 70B (EU)
    (
        NULL,
        'scaleway',
        'llama-3.3-70b-instruct',
        'Llama 3.3 70B (EU)',
        true,
        true,
        8192,
        0.0500,
        0.0500,
        40,
        '{"region": "fr-par", "data_residency": "eu"}'::jsonb
    )
ON CONFLICT (tenant_id, provider, model_id) DO NOTHING;

-- ============================================================================
-- PART 7: HELPER FUNCTIONS
-- ============================================================================

-- Function to get default LLM configuration for a tenant
CREATE OR REPLACE FUNCTION get_default_llm_config(p_tenant_id UUID)
RETURNS TABLE (
    config_id UUID,
    provider TEXT,
    model_id TEXT,
    display_name TEXT,
    max_tokens INTEGER,
    cost_per_1k_input DECIMAL,
    cost_per_1k_output DECIMAL,
    config_overrides JSONB
) AS $$
BEGIN
    RETURN QUERY
    -- First try to get tenant-specific enabled configuration with highest priority
    SELECT
        id,
        llm_configurations.provider,
        llm_configurations.model_id,
        llm_configurations.display_name,
        llm_configurations.max_tokens,
        llm_configurations.cost_per_1k_input_tokens,
        llm_configurations.cost_per_1k_output_tokens,
        llm_configurations.config_overrides
    FROM llm_configurations
    WHERE llm_configurations.tenant_id = p_tenant_id
        AND llm_configurations.is_enabled = true
    ORDER BY llm_configurations.priority ASC
    LIMIT 1;

    -- If no tenant-specific config, fall back to global default
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT
            id,
            llm_configurations.provider,
            llm_configurations.model_id,
            llm_configurations.display_name,
            llm_configurations.max_tokens,
            llm_configurations.cost_per_1k_input_tokens,
            llm_configurations.cost_per_1k_output_tokens,
            llm_configurations.config_overrides
        FROM llm_configurations
        WHERE llm_configurations.tenant_id IS NULL
            AND llm_configurations.is_enabled = true
        ORDER BY llm_configurations.priority ASC
        LIMIT 1;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get EU-compliant LLM configurations
CREATE OR REPLACE FUNCTION get_eu_compliant_llm_configs(p_tenant_id UUID)
RETURNS TABLE (
    config_id UUID,
    provider TEXT,
    model_id TEXT,
    display_name TEXT,
    max_tokens INTEGER,
    priority INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        llm_configurations.provider,
        llm_configurations.model_id,
        llm_configurations.display_name,
        llm_configurations.max_tokens,
        llm_configurations.priority
    FROM llm_configurations
    WHERE (
        llm_configurations.tenant_id = p_tenant_id
        OR llm_configurations.tenant_id IS NULL
    )
    AND llm_configurations.is_enabled = true
    AND llm_configurations.is_eu_compliant = true
    ORDER BY
        CASE WHEN llm_configurations.tenant_id = p_tenant_id THEN 0 ELSE 1 END,
        llm_configurations.priority ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- PART 8: COMMENTS
-- ============================================================================

COMMENT ON TABLE llm_configurations IS 'Tenant-specific LLM model configurations with pricing, limits, and EU compliance settings';
COMMENT ON COLUMN llm_configurations.tenant_id IS 'Reference to tenant, NULL for global/system-wide defaults';
COMMENT ON COLUMN llm_configurations.provider IS 'LLM provider: anthropic, scaleway, vertex_ai, openai, google, other';
COMMENT ON COLUMN llm_configurations.model_id IS 'Model identifier (e.g., claude-3-5-sonnet-20241022)';
COMMENT ON COLUMN llm_configurations.display_name IS 'Human-readable model name';
COMMENT ON COLUMN llm_configurations.is_enabled IS 'Whether this configuration is active and can be used';
COMMENT ON COLUMN llm_configurations.is_eu_compliant IS 'Whether this model meets EU data residency requirements (GDPR)';
COMMENT ON COLUMN llm_configurations.max_tokens IS 'Maximum tokens allowed for this model';
COMMENT ON COLUMN llm_configurations.cost_per_1k_input_tokens IS 'Cost in EUR cents per 1000 input tokens';
COMMENT ON COLUMN llm_configurations.cost_per_1k_output_tokens IS 'Cost in EUR cents per 1000 output tokens';
COMMENT ON COLUMN llm_configurations.priority IS 'Fallback priority (lower = higher priority, 0-1000)';
COMMENT ON COLUMN llm_configurations.config_overrides IS 'Model-specific settings (JSON): region, data_residency, supports_vision, etc.';
COMMENT ON FUNCTION get_default_llm_config IS 'Get default LLM configuration for a tenant (tenant-specific or global fallback)';
COMMENT ON FUNCTION get_eu_compliant_llm_configs IS 'Get all EU-compliant LLM configurations for a tenant, ordered by priority';

-- ============================================================================
-- PART 9: GRANT PERMISSIONS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON llm_configurations TO service_role;
GRANT EXECUTE ON FUNCTION get_default_llm_config TO service_role;
GRANT EXECUTE ON FUNCTION get_eu_compliant_llm_configs TO service_role;
