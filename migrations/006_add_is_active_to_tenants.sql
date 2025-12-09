-- Migration to add missing is_active column to tenants table
-- This was added to 001 but seemingly not applied to the running instance

ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL;

-- Notify PostgREST to reload schema
NOTIFY pgrst, 'reload schema';
