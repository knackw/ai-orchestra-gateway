-- Migration: Add Vertex AI (Google Cloud) Claude and Gemini models with regional pricing
-- Version: 012
-- Date: 2025-12-08
-- Description: Extends model_pricing table with region and data_residency columns,
--              adds Vertex AI Claude models and Gemini models with EU data residency

BEGIN;

-- ============================================================================
-- PART 1: ALTER MODEL_PRICING TABLE (ADD REGION AND DATA_RESIDENCY COLUMNS)
-- ============================================================================

-- Create model_pricing table if it doesn't exist yet
CREATE TABLE IF NOT EXISTS model_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(50) NOT NULL,
    tasks TEXT[] NOT NULL,  -- ['chat', 'vision', 'audio', 'embeddings']

    -- Einkaufspreise (Purchase prices)
    input_price_ek DECIMAL(10, 6) NOT NULL,   -- €/Million Tokens
    output_price_ek DECIMAL(10, 6) NOT NULL,  -- €/Million Tokens

    -- Verkaufspreise (Selling prices to customers)
    input_price_vk DECIMAL(10, 6),
    output_price_vk DECIMAL(10, 6),

    -- Audio-specific (€/Minute)
    audio_price_ek DECIMAL(10, 6),
    audio_price_vk DECIMAL(10, 6),

    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- active, deprecated, preview
    is_enabled BOOLEAN DEFAULT TRUE,

    -- Metadata
    context_window INTEGER,
    max_output_tokens INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add region column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'model_pricing'
        AND column_name = 'region'
    ) THEN
        ALTER TABLE model_pricing ADD COLUMN region VARCHAR(50);
        COMMENT ON COLUMN model_pricing.region IS 'Cloud region where the model is deployed (e.g., europe-west3, us-central1)';
    END IF;
END $$;

-- Add data_residency column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'model_pricing'
        AND column_name = 'data_residency'
    ) THEN
        ALTER TABLE model_pricing ADD COLUMN data_residency VARCHAR(20) DEFAULT 'global';
        COMMENT ON COLUMN model_pricing.data_residency IS 'Data residency guarantee: eu (EU only), us (US only), global (no guarantee)';
    END IF;
END $$;

-- Add constraint to ensure data_residency is valid
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'model_pricing_data_residency_check'
    ) THEN
        ALTER TABLE model_pricing ADD CONSTRAINT model_pricing_data_residency_check
        CHECK (data_residency IN ('eu', 'us', 'global'));
    END IF;
END $$;

-- ============================================================================
-- PART 2: INSERT VERTEX AI CLAUDE MODELS
-- ============================================================================

-- Vertex AI Claude Models (Google Cloud Platform with EU data residency)
-- All prices are per million tokens (input and output)
-- Default selling prices (VK) set to NULL to use margin calculation or manual setting

INSERT INTO model_pricing (
    model_id,
    provider,
    tasks,
    input_price_ek,
    output_price_ek,
    input_price_vk,
    output_price_vk,
    status,
    is_enabled,
    region,
    data_residency,
    context_window,
    max_output_tokens
) VALUES
    -- Claude 3.5 Sonnet v2 (Latest version, best for production)
    (
        'claude-3-5-sonnet-v2@20241022',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        3.00,
        15.00,
        4.00,
        20.00,
        'active',
        true,
        'europe-west3',
        'eu',
        200000,
        8192
    ),
    -- Claude 3.5 Sonnet v1 (Original version)
    (
        'claude-3-5-sonnet@20240620',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        3.00,
        15.00,
        4.00,
        20.00,
        'active',
        true,
        'europe-west3',
        'eu',
        200000,
        8192
    ),
    -- Claude 3 Opus (Most capable, highest cost)
    (
        'claude-3-opus@20240229',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        15.00,
        75.00,
        20.00,
        100.00,
        'active',
        true,
        'europe-west3',
        'eu',
        200000,
        4096
    ),
    -- Claude 3 Sonnet (Balanced performance and cost)
    (
        'claude-3-sonnet@20240229',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        3.00,
        15.00,
        4.00,
        20.00,
        'active',
        true,
        'europe-west3',
        'eu',
        200000,
        4096
    ),
    -- Claude 3 Haiku (Fastest, most cost-effective)
    (
        'claude-3-haiku@20240307',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        0.25,
        1.25,
        0.35,
        1.75,
        'active',
        true,
        'europe-west3',
        'eu',
        200000,
        4096
    )
ON CONFLICT (model_id) DO UPDATE SET
    provider = EXCLUDED.provider,
    tasks = EXCLUDED.tasks,
    input_price_ek = EXCLUDED.input_price_ek,
    output_price_ek = EXCLUDED.output_price_ek,
    input_price_vk = EXCLUDED.input_price_vk,
    output_price_vk = EXCLUDED.output_price_vk,
    status = EXCLUDED.status,
    is_enabled = EXCLUDED.is_enabled,
    region = EXCLUDED.region,
    data_residency = EXCLUDED.data_residency,
    context_window = EXCLUDED.context_window,
    max_output_tokens = EXCLUDED.max_output_tokens,
    updated_at = NOW();

-- ============================================================================
-- PART 3: INSERT VERTEX AI GEMINI MODELS
-- ============================================================================

-- Vertex AI Gemini Models (Google's native models)
-- All prices are per million tokens (input and output)

INSERT INTO model_pricing (
    model_id,
    provider,
    tasks,
    input_price_ek,
    output_price_ek,
    input_price_vk,
    output_price_vk,
    status,
    is_enabled,
    region,
    data_residency,
    context_window,
    max_output_tokens
) VALUES
    -- Gemini 2.0 Flash (Latest, fastest, most cost-effective)
    (
        'gemini-2.0-flash-001',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        0.075,
        0.30,
        0.10,
        0.40,
        'active',
        true,
        'europe-west3',
        'eu',
        1000000,
        8192
    ),
    -- Gemini 1.5 Pro (Most capable, balanced cost)
    (
        'gemini-1.5-pro-002',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        1.25,
        5.00,
        1.75,
        7.00,
        'active',
        true,
        'europe-west3',
        'eu',
        2000000,
        8192
    ),
    -- Gemini 1.5 Flash (Fast and cost-effective)
    (
        'gemini-1.5-flash-002',
        'vertex_ai',
        ARRAY['chat', 'vision'],
        0.075,
        0.30,
        0.10,
        0.40,
        'active',
        true,
        'europe-west3',
        'eu',
        1000000,
        8192
    )
ON CONFLICT (model_id) DO UPDATE SET
    provider = EXCLUDED.provider,
    tasks = EXCLUDED.tasks,
    input_price_ek = EXCLUDED.input_price_ek,
    output_price_ek = EXCLUDED.output_price_ek,
    input_price_vk = EXCLUDED.input_price_vk,
    output_price_vk = EXCLUDED.output_price_vk,
    status = EXCLUDED.status,
    is_enabled = EXCLUDED.is_enabled,
    region = EXCLUDED.region,
    data_residency = EXCLUDED.data_residency,
    context_window = EXCLUDED.context_window,
    max_output_tokens = EXCLUDED.max_output_tokens,
    updated_at = NOW();

-- ============================================================================
-- PART 4: CREATE INDEXES FOR NEW COLUMNS
-- ============================================================================

-- Index for filtering by region
CREATE INDEX IF NOT EXISTS idx_model_pricing_region ON model_pricing(region);

-- Index for filtering by data residency
CREATE INDEX IF NOT EXISTS idx_model_pricing_data_residency ON model_pricing(data_residency);

-- Composite index for provider and region queries
CREATE INDEX IF NOT EXISTS idx_model_pricing_provider_region ON model_pricing(provider, region);

-- ============================================================================
-- PART 5: ADD COMMENTS
-- ============================================================================

COMMENT ON TABLE model_pricing IS 'AI model pricing and metadata for multi-provider support (Anthropic, Scaleway, Vertex AI, etc.)';
COMMENT ON COLUMN model_pricing.model_id IS 'Unique model identifier (e.g., claude-3-5-sonnet-v2@20241022)';
COMMENT ON COLUMN model_pricing.provider IS 'AI provider name (anthropic, scaleway, vertex_ai, openai, etc.)';
COMMENT ON COLUMN model_pricing.input_price_ek IS 'Purchase price (Einkaufspreis) per million input tokens in EUR';
COMMENT ON COLUMN model_pricing.output_price_ek IS 'Purchase price (Einkaufspreis) per million output tokens in EUR';
COMMENT ON COLUMN model_pricing.input_price_vk IS 'Selling price (Verkaufspreis) per million input tokens in EUR';
COMMENT ON COLUMN model_pricing.output_price_vk IS 'Selling price (Verkaufspreis) per million output tokens in EUR';

-- ============================================================================
-- PART 6: VERIFICATION
-- ============================================================================

-- Verify Vertex AI Claude models were inserted
DO $$
DECLARE
    claude_count INTEGER;
    gemini_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO claude_count
    FROM model_pricing
    WHERE provider = 'vertex_ai' AND model_id LIKE 'claude-%';

    SELECT COUNT(*) INTO gemini_count
    FROM model_pricing
    WHERE provider = 'vertex_ai' AND model_id LIKE 'gemini-%';

    IF claude_count < 5 THEN
        RAISE EXCEPTION 'Expected at least 5 Vertex AI Claude models, found %', claude_count;
    END IF;

    IF gemini_count < 3 THEN
        RAISE EXCEPTION 'Expected at least 3 Vertex AI Gemini models, found %', gemini_count;
    END IF;

    RAISE NOTICE 'Migration 012 completed successfully:';
    RAISE NOTICE '  - Added region and data_residency columns';
    RAISE NOTICE '  - Inserted % Vertex AI Claude models', claude_count;
    RAISE NOTICE '  - Inserted % Vertex AI Gemini models', gemini_count;
    RAISE NOTICE '  - Created indexes for region and data_residency';
    RAISE NOTICE '  - All models set to region: europe-west3, data_residency: eu';
END $$;

COMMIT;
