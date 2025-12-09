-- Migration: Create analytics views for usage monitoring
-- Version: 007
-- Date: 2025-12-05
-- Description: Adds views for time-series analysis of usage logs

-- Drop view if exists
DROP VIEW IF EXISTS daily_usage_stats;

-- Create daily usage stats view
-- Aggregates logs by day and provider to reduce runtime computation
CREATE OR REPLACE VIEW daily_usage_stats AS
SELECT
    DATE_TRUNC('day', created_at) as usage_date,
    provider,
    COUNT(*) as request_count,
    SUM(tokens_used) as total_tokens,
    SUM(credits_deducted) as total_credits,
    ROUND(AVG(tokens_used), 2) as avg_tokens_per_request
FROM
    usage_logs
GROUP BY
    DATE_TRUNC('day', created_at),
    provider
ORDER BY
    usage_date DESC;

-- Grant permissions (safe for authenticated users, RLS still applies on underlying table if not view owner)
-- But views run with owner permissions usually.
-- For simple dashboard, we query this via service role usually, or grant explicit select.
GRANT SELECT ON daily_usage_stats TO authenticated, service_role;

-- Comment
COMMENT ON VIEW daily_usage_stats IS 'Aggregated daily usage statistics by provider';
