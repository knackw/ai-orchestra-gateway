-- Migration: Model Pricing Schema
-- Version: 013 (DB-011)
-- Date: 2025-12-08
-- Description: Comprehensive model pricing with volume discounts and time-based pricing tiers

-- ============================================================================
-- PART 1: CREATE MODEL_PRICING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS model_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Model identification
    model_id TEXT NOT NULL,
    provider TEXT NOT NULL CHECK (provider IN ('anthropic', 'scaleway', 'vertex_ai', 'openai', 'google', 'other')),

    -- Pricing (per million tokens, in EUR cents)
    input_price_per_million DECIMAL(12,4) NOT NULL CHECK (input_price_per_million >= 0),
    output_price_per_million DECIMAL(12,4) NOT NULL CHECK (output_price_per_million >= 0),

    -- Currency
    currency TEXT DEFAULT 'EUR' CHECK (currency IN ('EUR', 'USD', 'GBP')),

    -- Effective date range for time-based pricing
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_until TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(model_id, provider, effective_from),
    CHECK (effective_until IS NULL OR effective_until > effective_from)
);

-- ============================================================================
-- PART 2: CREATE PRICING_TIERS TABLE (VOLUME DISCOUNTS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pricing_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Tenant association (NULL = applies to all tenants)
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

    -- Tier details
    tier_name TEXT NOT NULL,
    min_credits INTEGER NOT NULL CHECK (min_credits >= 0),

    -- Discount percentage (e.g., 10.00 for 10% discount)
    discount_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (discount_percent >= 0 AND discount_percent <= 100),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(tenant_id, tier_name)
);

-- ============================================================================
-- PART 3: CREATE INDEXES FOR MODEL_PRICING
-- ============================================================================

-- Index for model lookups
CREATE INDEX IF NOT EXISTS idx_model_pricing_model_id
    ON model_pricing(model_id);

-- Index for provider filtering
CREATE INDEX IF NOT EXISTS idx_model_pricing_provider
    ON model_pricing(provider);

-- Composite index for provider + model queries
CREATE INDEX IF NOT EXISTS idx_model_pricing_provider_model
    ON model_pricing(provider, model_id);

-- Index for current pricing (active date range)
CREATE INDEX IF NOT EXISTS idx_model_pricing_effective
    ON model_pricing(effective_from, effective_until)
    WHERE effective_until IS NULL OR effective_until > NOW();

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_model_pricing_dates
    ON model_pricing(effective_from DESC, effective_until DESC);

-- ============================================================================
-- PART 4: CREATE INDEXES FOR PRICING_TIERS
-- ============================================================================

-- Index for tenant lookups
CREATE INDEX IF NOT EXISTS idx_pricing_tiers_tenant_id
    ON pricing_tiers(tenant_id);

-- Index for credit threshold lookups
CREATE INDEX IF NOT EXISTS idx_pricing_tiers_min_credits
    ON pricing_tiers(min_credits);

-- Composite index for tier selection
CREATE INDEX IF NOT EXISTS idx_pricing_tiers_tenant_credits
    ON pricing_tiers(tenant_id, min_credits DESC);

-- ============================================================================
-- PART 5: ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE model_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE pricing_tiers ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PART 6: RLS POLICIES FOR MODEL_PRICING
-- ============================================================================

-- Policy: All authenticated users can SELECT pricing (read-only for tenants)
DROP POLICY IF EXISTS model_pricing_select_all ON model_pricing;
CREATE POLICY model_pricing_select_all ON model_pricing
    FOR SELECT
    USING (true);

-- Policy: Only service role can INSERT
DROP POLICY IF EXISTS model_pricing_service_insert ON model_pricing;
CREATE POLICY model_pricing_service_insert ON model_pricing
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Policy: Only service role can UPDATE
DROP POLICY IF EXISTS model_pricing_service_update ON model_pricing;
CREATE POLICY model_pricing_service_update ON model_pricing
    FOR UPDATE
    TO service_role
    USING (true);

-- Policy: Only service role can DELETE
DROP POLICY IF EXISTS model_pricing_service_delete ON model_pricing;
CREATE POLICY model_pricing_service_delete ON model_pricing
    FOR DELETE
    TO service_role
    USING (true);

-- ============================================================================
-- PART 7: RLS POLICIES FOR PRICING_TIERS
-- ============================================================================

-- Policy: Tenants can SELECT their own tiers and global tiers
DROP POLICY IF EXISTS pricing_tiers_select_own ON pricing_tiers;
CREATE POLICY pricing_tiers_select_own ON pricing_tiers
    FOR SELECT
    USING (
        -- Tenant's own tiers
        tenant_id = current_setting('app.current_tenant_id', true)::uuid
        OR
        -- Global tiers (NULL tenant_id)
        tenant_id IS NULL
    );

-- Policy: Service role can SELECT all
DROP POLICY IF EXISTS pricing_tiers_service_select_all ON pricing_tiers;
CREATE POLICY pricing_tiers_service_select_all ON pricing_tiers
    FOR SELECT
    TO service_role
    USING (true);

-- Policy: Service role can INSERT
DROP POLICY IF EXISTS pricing_tiers_service_insert ON pricing_tiers;
CREATE POLICY pricing_tiers_service_insert ON pricing_tiers
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Policy: Service role can UPDATE
DROP POLICY IF EXISTS pricing_tiers_service_update ON pricing_tiers;
CREATE POLICY pricing_tiers_service_update ON pricing_tiers
    FOR UPDATE
    TO service_role
    USING (true);

-- Policy: Service role can DELETE
DROP POLICY IF EXISTS pricing_tiers_service_delete ON pricing_tiers;
CREATE POLICY pricing_tiers_service_delete ON pricing_tiers
    FOR DELETE
    TO service_role
    USING (true);

-- ============================================================================
-- PART 8: INSERT DEFAULT MODEL PRICING
-- ============================================================================

-- Insert pricing for common models (as of December 2025)
INSERT INTO model_pricing (
    model_id,
    provider,
    input_price_per_million,
    output_price_per_million,
    currency,
    effective_from
) VALUES
    -- Anthropic Direct (US)
    ('claude-3-5-sonnet-20241022', 'anthropic', 300.0000, 1500.0000, 'EUR', '2024-10-22'),
    ('claude-3-opus-20240229', 'anthropic', 1500.0000, 7500.0000, 'EUR', '2024-02-29'),
    ('claude-3-sonnet-20240229', 'anthropic', 300.0000, 1500.0000, 'EUR', '2024-02-29'),
    ('claude-3-haiku-20240307', 'anthropic', 25.0000, 125.0000, 'EUR', '2024-03-07'),

    -- Vertex AI Claude (EU)
    ('claude-3-5-sonnet-v2@20241022', 'vertex_ai', 300.0000, 1500.0000, 'EUR', '2024-10-22'),
    ('claude-3-5-sonnet@20240620', 'vertex_ai', 300.0000, 1500.0000, 'EUR', '2024-06-20'),
    ('claude-3-opus@20240229', 'vertex_ai', 1500.0000, 7500.0000, 'EUR', '2024-02-29'),
    ('claude-3-sonnet@20240229', 'vertex_ai', 300.0000, 1500.0000, 'EUR', '2024-02-29'),
    ('claude-3-haiku@20240307', 'vertex_ai', 25.0000, 125.0000, 'EUR', '2024-03-07'),

    -- Vertex AI Gemini (EU)
    ('gemini-2.0-flash-001', 'vertex_ai', 7.5000, 30.0000, 'EUR', '2024-12-01'),
    ('gemini-1.5-pro-002', 'vertex_ai', 125.0000, 500.0000, 'EUR', '2024-05-01'),
    ('gemini-1.5-flash-002', 'vertex_ai', 7.5000, 30.0000, 'EUR', '2024-05-01'),

    -- Scaleway (EU)
    ('llama-3.1-8b-instruct', 'scaleway', 10.0000, 10.0000, 'EUR', '2024-07-01'),
    ('llama-3.3-70b-instruct', 'scaleway', 50.0000, 50.0000, 'EUR', '2024-12-01'),
    ('mistral-small-3.2-24b-instruct-2506', 'scaleway', 20.0000, 20.0000, 'EUR', '2025-06-01'),
    ('qwen3-235b-a22b-instruct-2507', 'scaleway', 80.0000, 80.0000, 'EUR', '2025-07-01')
ON CONFLICT (model_id, provider, effective_from) DO UPDATE SET
    input_price_per_million = EXCLUDED.input_price_per_million,
    output_price_per_million = EXCLUDED.output_price_per_million,
    currency = EXCLUDED.currency;

-- ============================================================================
-- PART 9: INSERT DEFAULT PRICING TIERS
-- ============================================================================

-- Global pricing tiers (apply to all tenants unless overridden)
INSERT INTO pricing_tiers (
    tenant_id,
    tier_name,
    min_credits,
    discount_percent
) VALUES
    (NULL, 'Starter', 0, 0.00),
    (NULL, 'Bronze', 10000, 5.00),
    (NULL, 'Silver', 50000, 10.00),
    (NULL, 'Gold', 100000, 15.00),
    (NULL, 'Platinum', 500000, 20.00),
    (NULL, 'Enterprise', 1000000, 25.00)
ON CONFLICT (tenant_id, tier_name) DO UPDATE SET
    min_credits = EXCLUDED.min_credits,
    discount_percent = EXCLUDED.discount_percent;

-- ============================================================================
-- PART 10: HELPER FUNCTIONS
-- ============================================================================

-- Function to get current pricing for a model
CREATE OR REPLACE FUNCTION get_current_model_pricing(
    p_model_id TEXT,
    p_provider TEXT
)
RETURNS TABLE (
    pricing_id UUID,
    input_price DECIMAL,
    output_price DECIMAL,
    currency TEXT,
    effective_from TIMESTAMPTZ,
    effective_until TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        input_price_per_million,
        output_price_per_million,
        model_pricing.currency,
        model_pricing.effective_from,
        model_pricing.effective_until
    FROM model_pricing
    WHERE model_pricing.model_id = p_model_id
        AND model_pricing.provider = p_provider
        AND model_pricing.effective_from <= NOW()
        AND (model_pricing.effective_until IS NULL OR model_pricing.effective_until > NOW())
    ORDER BY model_pricing.effective_from DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get applicable pricing tier for a tenant
CREATE OR REPLACE FUNCTION get_pricing_tier_for_tenant(
    p_tenant_id UUID,
    p_current_credits INTEGER
)
RETURNS TABLE (
    tier_id UUID,
    tier_name TEXT,
    min_credits INTEGER,
    discount_percent DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        pricing_tiers.tier_name,
        pricing_tiers.min_credits,
        pricing_tiers.discount_percent
    FROM pricing_tiers
    WHERE (
        pricing_tiers.tenant_id = p_tenant_id
        OR pricing_tiers.tenant_id IS NULL
    )
    AND pricing_tiers.min_credits <= p_current_credits
    ORDER BY
        CASE WHEN pricing_tiers.tenant_id = p_tenant_id THEN 0 ELSE 1 END,
        pricing_tiers.min_credits DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate discounted price
CREATE OR REPLACE FUNCTION calculate_discounted_price(
    p_base_price DECIMAL,
    p_tenant_id UUID,
    p_current_credits INTEGER
)
RETURNS DECIMAL AS $$
DECLARE
    v_discount_percent DECIMAL;
BEGIN
    -- Get applicable discount
    SELECT discount_percent INTO v_discount_percent
    FROM get_pricing_tier_for_tenant(p_tenant_id, p_current_credits);

    -- If no tier found, return base price
    IF v_discount_percent IS NULL THEN
        RETURN p_base_price;
    END IF;

    -- Apply discount
    RETURN p_base_price * (1 - v_discount_percent / 100.0);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get pricing history for a model
CREATE OR REPLACE FUNCTION get_model_pricing_history(
    p_model_id TEXT,
    p_provider TEXT
)
RETURNS TABLE (
    pricing_id UUID,
    input_price DECIMAL,
    output_price DECIMAL,
    currency TEXT,
    effective_from TIMESTAMPTZ,
    effective_until TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        input_price_per_million,
        output_price_per_million,
        model_pricing.currency,
        model_pricing.effective_from,
        model_pricing.effective_until
    FROM model_pricing
    WHERE model_pricing.model_id = p_model_id
        AND model_pricing.provider = p_provider
    ORDER BY model_pricing.effective_from DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- PART 11: COMMENTS
-- ============================================================================

COMMENT ON TABLE model_pricing IS 'Time-based pricing for AI models across all providers';
COMMENT ON TABLE pricing_tiers IS 'Volume-based discount tiers for tenants';

COMMENT ON COLUMN model_pricing.model_id IS 'Model identifier (e.g., claude-3-5-sonnet-20241022)';
COMMENT ON COLUMN model_pricing.provider IS 'AI provider: anthropic, scaleway, vertex_ai, openai, google, other';
COMMENT ON COLUMN model_pricing.input_price_per_million IS 'Price per million input tokens in currency specified';
COMMENT ON COLUMN model_pricing.output_price_per_million IS 'Price per million output tokens in currency specified';
COMMENT ON COLUMN model_pricing.currency IS 'Pricing currency: EUR, USD, GBP';
COMMENT ON COLUMN model_pricing.effective_from IS 'When this pricing becomes effective';
COMMENT ON COLUMN model_pricing.effective_until IS 'When this pricing expires (NULL = no expiration)';

COMMENT ON COLUMN pricing_tiers.tenant_id IS 'Reference to tenant, NULL for global tiers';
COMMENT ON COLUMN pricing_tiers.tier_name IS 'Tier name (e.g., Starter, Bronze, Silver, Gold)';
COMMENT ON COLUMN pricing_tiers.min_credits IS 'Minimum credits required to qualify for this tier';
COMMENT ON COLUMN pricing_tiers.discount_percent IS 'Discount percentage for this tier (0-100)';

COMMENT ON FUNCTION get_current_model_pricing IS 'Get current active pricing for a specific model';
COMMENT ON FUNCTION get_pricing_tier_for_tenant IS 'Get the applicable pricing tier for a tenant based on current credits';
COMMENT ON FUNCTION calculate_discounted_price IS 'Calculate price after applying volume discount';
COMMENT ON FUNCTION get_model_pricing_history IS 'Get complete pricing history for a model';

-- ============================================================================
-- PART 12: GRANT PERMISSIONS
-- ============================================================================

GRANT SELECT ON model_pricing TO service_role;
GRANT INSERT, UPDATE, DELETE ON model_pricing TO service_role;

GRANT SELECT ON pricing_tiers TO service_role;
GRANT INSERT, UPDATE, DELETE ON pricing_tiers TO service_role;

GRANT EXECUTE ON FUNCTION get_current_model_pricing TO service_role;
GRANT EXECUTE ON FUNCTION get_pricing_tier_for_tenant TO service_role;
GRANT EXECUTE ON FUNCTION calculate_discounted_price TO service_role;
GRANT EXECUTE ON FUNCTION get_model_pricing_history TO service_role;
