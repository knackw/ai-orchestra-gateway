-- Migration: Create billing functions for atomic credit deduction
-- Version: 002
-- Description: Implements PostgreSQL RPC function for race-condition-free credit management

-- Drop function if exists (for re-running migration)
DROP FUNCTION IF EXISTS deduct_credits(TEXT, INTEGER);

-- Create atomic credit deduction function
CREATE OR REPLACE FUNCTION deduct_credits(
    p_license_key TEXT,
    p_amount INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_current_balance INTEGER;
    v_is_active BOOLEAN;
    v_expires_at TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Lock the license row and get current state
    SELECT 
        credits_remaining,
        is_active,
        expires_at
    INTO 
        v_current_balance,
        v_is_active,
        v_expires_at
    FROM licenses
    WHERE license_key = p_license_key
    FOR UPDATE;
    
    -- Check if license exists
    IF NOT FOUND THEN
        RAISE EXCEPTION 'INVALID_LICENSE: License key not found';
    END IF;
    
    -- Check if license is active
    IF NOT v_is_active THEN
        RAISE EXCEPTION 'INACTIVE_LICENSE: License is not active';
    END IF;
    
    -- Check if license is expired
    IF v_expires_at IS NOT NULL AND v_expires_at < NOW() THEN
        RAISE EXCEPTION 'EXPIRED_LICENSE: License has expired';
    END IF;
    
    -- Check if sufficient credits
    IF v_current_balance < p_amount THEN
        RAISE EXCEPTION 'INSUFFICIENT_CREDITS: Current balance % is less than required %', 
            v_current_balance, p_amount;
    END IF;
    
    -- Deduct credits and update timestamp
    UPDATE licenses
    SET 
        credits_remaining = credits_remaining - p_amount,
        updated_at = NOW()
    WHERE license_key = p_license_key;
    
    -- Return new balance
    RETURN v_current_balance - p_amount;
END;
$$ LANGUAGE plpgsql;

-- Add comment explaining the function
COMMENT ON FUNCTION deduct_credits(TEXT, INTEGER) IS 
'Atomically deducts credits from a license. Uses row-level locking to prevent race conditions. Returns new balance or raises exception on errors.';
