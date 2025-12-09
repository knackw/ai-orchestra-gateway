-- Migration 011: Add Invoices Table
-- Part of BILLING-005
--
-- Creates invoices table for tracking billing invoices

-- Create invoice status enum
DO $$ BEGIN
    CREATE TYPE invoice_status AS ENUM ('draft', 'pending', 'paid', 'overdue', 'cancelled', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Invoice details
    status invoice_status NOT NULL DEFAULT 'draft',
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',

    -- Amounts (in cents to avoid floating point issues)
    subtotal_cents INTEGER NOT NULL DEFAULT 0,
    tax_rate_percent DECIMAL(5,2) NOT NULL DEFAULT 19.00,
    tax_cents INTEGER NOT NULL DEFAULT 0,
    total_cents INTEGER NOT NULL DEFAULT 0,

    -- Credits purchased
    credits_purchased INTEGER NOT NULL DEFAULT 0,
    price_per_credit_cents INTEGER NOT NULL DEFAULT 1,

    -- Billing details
    billing_name VARCHAR(255),
    billing_email VARCHAR(255),
    billing_address TEXT,
    billing_vat_id VARCHAR(50),

    -- Payment info
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    paid_at TIMESTAMPTZ,

    -- Period
    period_start DATE,
    period_end DATE,
    due_date DATE,

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create invoice_items table for line items
CREATE TABLE IF NOT EXISTS invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,

    -- Item details
    description VARCHAR(500) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price_cents INTEGER NOT NULL DEFAULT 0,
    total_cents INTEGER NOT NULL DEFAULT 0,

    -- Optional metadata
    item_type VARCHAR(50),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Ordering
    sort_order INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_invoices_tenant_id ON invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);

-- Enable RLS
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;

-- RLS policies for invoices
CREATE POLICY "invoices_tenant_isolation" ON invoices
    FOR ALL
    USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY "invoices_service_role_bypass" ON invoices
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- RLS policies for invoice_items
CREATE POLICY "invoice_items_tenant_isolation" ON invoice_items
    FOR ALL
    USING (
        invoice_id IN (
            SELECT id FROM invoices
            WHERE tenant_id::text = current_setting('app.current_tenant_id', true)
        )
    );

CREATE POLICY "invoice_items_service_role_bypass" ON invoice_items
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Function to generate invoice number
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    v_year VARCHAR(4);
    v_sequence INTEGER;
    v_number VARCHAR(50);
BEGIN
    v_year := to_char(NOW(), 'YYYY');

    -- Get next sequence number for this year
    SELECT COALESCE(MAX(
        CAST(SUBSTRING(invoice_number FROM 'INV-' || v_year || '-(\d+)') AS INTEGER)
    ), 0) + 1 INTO v_sequence
    FROM invoices
    WHERE invoice_number LIKE 'INV-' || v_year || '-%';

    v_number := 'INV-' || v_year || '-' || LPAD(v_sequence::TEXT, 5, '0');

    RETURN v_number;
END;
$$ LANGUAGE plpgsql;

-- Function to create invoice
CREATE OR REPLACE FUNCTION create_invoice(
    p_tenant_id UUID,
    p_credits INTEGER,
    p_price_per_credit_cents INTEGER DEFAULT 1,
    p_tax_rate_percent DECIMAL DEFAULT 19.00,
    p_billing_name VARCHAR DEFAULT NULL,
    p_billing_email VARCHAR DEFAULT NULL,
    p_billing_address TEXT DEFAULT NULL,
    p_billing_vat_id VARCHAR DEFAULT NULL,
    p_due_days INTEGER DEFAULT 30
) RETURNS UUID AS $$
DECLARE
    v_invoice_id UUID;
    v_invoice_number VARCHAR(50);
    v_subtotal INTEGER;
    v_tax INTEGER;
    v_total INTEGER;
BEGIN
    -- Generate invoice number
    v_invoice_number := generate_invoice_number();

    -- Calculate amounts
    v_subtotal := p_credits * p_price_per_credit_cents;
    v_tax := ROUND(v_subtotal * p_tax_rate_percent / 100);
    v_total := v_subtotal + v_tax;

    -- Create invoice
    INSERT INTO invoices (
        invoice_number,
        tenant_id,
        status,
        subtotal_cents,
        tax_rate_percent,
        tax_cents,
        total_cents,
        credits_purchased,
        price_per_credit_cents,
        billing_name,
        billing_email,
        billing_address,
        billing_vat_id,
        due_date,
        period_start,
        period_end
    ) VALUES (
        v_invoice_number,
        p_tenant_id,
        'pending',
        v_subtotal,
        p_tax_rate_percent,
        v_tax,
        v_total,
        p_credits,
        p_price_per_credit_cents,
        p_billing_name,
        p_billing_email,
        p_billing_address,
        p_billing_vat_id,
        CURRENT_DATE + p_due_days,
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '30 days'
    ) RETURNING id INTO v_invoice_id;

    -- Add line item for credits
    INSERT INTO invoice_items (
        invoice_id,
        description,
        quantity,
        unit_price_cents,
        total_cents,
        item_type,
        sort_order
    ) VALUES (
        v_invoice_id,
        'AI Gateway Credits',
        p_credits,
        p_price_per_credit_cents,
        v_subtotal,
        'credits',
        1
    );

    RETURN v_invoice_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to mark invoice as paid
CREATE OR REPLACE FUNCTION mark_invoice_paid(
    p_invoice_id UUID,
    p_payment_method VARCHAR DEFAULT 'stripe',
    p_payment_reference VARCHAR DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    v_credits INTEGER;
    v_tenant_id UUID;
BEGIN
    -- Get invoice details
    SELECT credits_purchased, tenant_id
    INTO v_credits, v_tenant_id
    FROM invoices
    WHERE id = p_invoice_id AND status = 'pending';

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Update invoice status
    UPDATE invoices
    SET status = 'paid',
        paid_at = NOW(),
        payment_method = p_payment_method,
        payment_reference = p_payment_reference,
        updated_at = NOW()
    WHERE id = p_invoice_id;

    -- Add credits to license (assuming one license per tenant for simplicity)
    UPDATE licenses
    SET credits_remaining = credits_remaining + v_credits,
        updated_at = NOW()
    WHERE tenant_id = v_tenant_id AND is_active = TRUE;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS invoices_updated_at ON invoices;
CREATE TRIGGER invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_invoices_updated_at();

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON invoices TO service_role;
GRANT SELECT, INSERT, UPDATE ON invoice_items TO service_role;
GRANT EXECUTE ON FUNCTION generate_invoice_number TO service_role;
GRANT EXECUTE ON FUNCTION create_invoice TO service_role;
GRANT EXECUTE ON FUNCTION mark_invoice_paid TO service_role;
