-- Migration: Extended Model Pricing Schema
-- Erweitert die Preisstruktur für alle Provider
-- Version: DB-011
-- Date: 2025-12-08

-- Erweitere model_pricing Tabelle falls nicht vorhanden
CREATE TABLE IF NOT EXISTS model_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Model Identification
    provider VARCHAR(50) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    model_name VARCHAR(200) NOT NULL,

    -- Pricing (per 1M tokens, in USD cents)
    input_price_per_1m INTEGER NOT NULL,
    output_price_per_1m INTEGER NOT NULL,

    -- Our markup (percentage)
    markup_percentage DECIMAL(5,2) DEFAULT 30.00,

    -- Calculated sell prices
    sell_input_price_per_1m INTEGER GENERATED ALWAYS AS (
        ROUND(input_price_per_1m * (1 + markup_percentage / 100))
    ) STORED,
    sell_output_price_per_1m INTEGER GENERATED ALWAYS AS (
        ROUND(output_price_per_1m * (1 + markup_percentage / 100))
    ) STORED,

    -- Model Capabilities
    context_length INTEGER DEFAULT 8192,
    max_output_tokens INTEGER DEFAULT 4096,
    supports_vision BOOLEAN DEFAULT false,
    supports_streaming BOOLEAN DEFAULT true,
    supports_function_calling BOOLEAN DEFAULT false,

    -- Data Residency
    region VARCHAR(50) DEFAULT 'global',
    data_residency VARCHAR(10) DEFAULT 'GLOBAL',

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_deprecated BOOLEAN DEFAULT false,
    deprecated_date DATE,
    replacement_model_id VARCHAR(100),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(provider, model_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_model_pricing_provider ON model_pricing(provider);
CREATE INDEX IF NOT EXISTS idx_model_pricing_active ON model_pricing(is_active);
CREATE INDEX IF NOT EXISTS idx_model_pricing_region ON model_pricing(data_residency);
CREATE INDEX IF NOT EXISTS idx_model_pricing_vision ON model_pricing(supports_vision) WHERE supports_vision = true;

-- Insert alle Modelle
INSERT INTO model_pricing (provider, model_id, model_name, input_price_per_1m, output_price_per_1m, context_length, max_output_tokens, supports_vision, data_residency, region) VALUES
-- Anthropic Direct
('anthropic', 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 300, 1500, 200000, 8192, true, 'US', 'us-east-1'),
('anthropic', 'claude-3-opus-20240229', 'Claude 3 Opus', 1500, 7500, 200000, 4096, true, 'US', 'us-east-1'),
('anthropic', 'claude-3-haiku-20240307', 'Claude 3 Haiku', 25, 125, 200000, 4096, true, 'US', 'us-east-1'),

-- Vertex AI Claude (EU)
('vertex_claude', 'claude-3-5-sonnet-v2@20241022', 'Claude 3.5 Sonnet v2 (Vertex)', 300, 1500, 200000, 8192, true, 'EU', 'europe-west3'),
('vertex_claude', 'claude-3-opus@20240229', 'Claude 3 Opus (Vertex)', 1500, 7500, 200000, 4096, true, 'EU', 'europe-west3'),
('vertex_claude', 'claude-3-sonnet@20240229', 'Claude 3 Sonnet (Vertex)', 300, 1500, 200000, 4096, true, 'EU', 'europe-west3'),
('vertex_claude', 'claude-3-haiku@20240307', 'Claude 3 Haiku (Vertex)', 25, 125, 200000, 4096, true, 'EU', 'europe-west3'),
('vertex_claude', 'claude-3-5-haiku@20241022', 'Claude 3.5 Haiku (Vertex)', 100, 500, 200000, 8192, false, 'EU', 'europe-west3'),

-- Vertex AI Gemini (EU)
('vertex_gemini', 'gemini-2.0-flash-001', 'Gemini 2.0 Flash', 10, 40, 1048576, 8192, true, 'EU', 'europe-west3'),
('vertex_gemini', 'gemini-1.5-pro-002', 'Gemini 1.5 Pro', 125, 500, 2097152, 8192, true, 'EU', 'europe-west3'),
('vertex_gemini', 'gemini-1.5-flash-002', 'Gemini 1.5 Flash', 10, 40, 1048576, 8192, true, 'EU', 'europe-west3'),

-- Scaleway (EU)
('scaleway', 'llama-3.1-8b-instruct', 'Llama 3.1 8B', 10, 10, 131072, 8192, false, 'EU', 'fr-par'),
('scaleway', 'llama-3.3-70b-instruct', 'Llama 3.3 70B', 50, 50, 131072, 8192, false, 'EU', 'fr-par'),
('scaleway', 'mistral-small-3.2-24b-instruct-2506', 'Mistral Small 3.2', 20, 20, 131072, 8192, false, 'EU', 'fr-par'),
('scaleway', 'qwen3-235b-a22b-instruct-2507', 'Qwen3 235B', 80, 80, 131072, 8192, false, 'EU', 'fr-par')
ON CONFLICT (provider, model_id) DO UPDATE SET
    model_name = EXCLUDED.model_name,
    input_price_per_1m = EXCLUDED.input_price_per_1m,
    output_price_per_1m = EXCLUDED.output_price_per_1m,
    context_length = EXCLUDED.context_length,
    supports_vision = EXCLUDED.supports_vision,
    data_residency = EXCLUDED.data_residency,
    updated_at = NOW();

-- Trigger
CREATE TRIGGER update_model_pricing_updated_at
    BEFORE UPDATE ON model_pricing
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE model_pricing IS 'Comprehensive pricing and capabilities for all LLM models across providers';
COMMENT ON COLUMN model_pricing.input_price_per_1m IS 'Provider cost per 1M input tokens in USD cents';
COMMENT ON COLUMN model_pricing.output_price_per_1m IS 'Provider cost per 1M output tokens in USD cents';
COMMENT ON COLUMN model_pricing.markup_percentage IS 'Our markup percentage (default 30%)';
COMMENT ON COLUMN model_pricing.sell_input_price_per_1m IS 'Calculated sell price per 1M input tokens (with markup)';
COMMENT ON COLUMN model_pricing.sell_output_price_per_1m IS 'Calculated sell price per 1M output tokens (with markup)';
COMMENT ON COLUMN model_pricing.data_residency IS 'Data residency compliance (EU, US, GLOBAL)';
COMMENT ON COLUMN model_pricing.region IS 'Provider region identifier';
COMMENT ON COLUMN model_pricing.is_deprecated IS 'Model is deprecated and should not be used for new requests';
