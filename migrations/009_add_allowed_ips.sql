-- Add allowed_ips column to tenants table for IP whitelisting
-- NULL = allow all IPs (default, backwards compatible)
-- Empty array = block all IPs
-- Array with values = whitelist only those IPs/CIDRs

ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS allowed_ips TEXT[];

COMMENT ON COLUMN tenants.allowed_ips IS 'IP whitelist for this tenant. NULL allows all IPs. Supports CIDR notation (e.g., 192.168.1.0/24).';
