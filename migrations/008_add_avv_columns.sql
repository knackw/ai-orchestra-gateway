-- Add AVV columns to tenants table
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS avv_signed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS avv_version TEXT;
