-- Create settings table for fee configuration
CREATE TABLE IF NOT EXISTS public.settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default fee settings
INSERT INTO public.settings (key, value, description) VALUES
('fee_tier_1_amount', '5000', 'Maximum amount for tier 1 fee (Naira)'),
('fee_tier_1_fee', '10', 'Fee for transfers up to tier 1 amount (Naira)'),
('fee_tier_2_amount', '50000', 'Maximum amount for tier 2 fee (Naira)'),
('fee_tier_2_fee', '25', 'Fee for transfers up to tier 2 amount (Naira)'),
('fee_tier_3_fee', '50', 'Fee for transfers above tier 2 amount (Naira)'),
('paystack_fee', '10', 'Paystack fee per transfer (Naira)'),
('min_transfer_amount', '100', 'Minimum transfer amount (Naira)'),
('max_transfer_amount', '1000000', 'Maximum transfer amount (Naira)')
ON CONFLICT (key) DO NOTHING;

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_settings_updated_at ON public.settings;
CREATE TRIGGER update_settings_updated_at
    BEFORE UPDATE ON public.settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE public.settings TO postgres;
GRANT ALL PRIVILEGES ON SEQUENCE public.settings_id_seq TO postgres;

-- Display created settings
SELECT key, value, description FROM public.settings ORDER BY key;
