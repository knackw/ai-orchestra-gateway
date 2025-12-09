-- Migration: Create add_credits function
-- Description: Adds credits to a license atomically.

CREATE OR REPLACE FUNCTION add_credits(license_key_param TEXT, credits_to_add INT)
RETURNS VOID AS $$
DECLARE
    license_record RECORD;
BEGIN
    -- Lock the license row for atomic update
    SELECT * INTO license_record
    FROM licenses
    WHERE license_key = license_key_param
    FOR UPDATE;

    -- Check if license exists
    IF NOT FOUND THEN
        RAISE EXCEPTION 'INVALID_LICENSE: License key % not found.', license_key_param;
    END IF;

    -- Add credits (allow even if expired/inactive, as top-up might reactivate logic later)
    UPDATE licenses
    SET credits_remaining = credits_remaining + credits_to_add,
        updated_at = NOW()
    WHERE license_key = license_key_param;

    -- Return success (implicitly void)
END;
$$ LANGUAGE plpgsql;
