-- Create settings table for fee calculator
CREATE TABLE IF NOT EXISTS public.settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default fee settings
INSERT INTO public.settings (key, value, description) VALUES
(
    'fee_structure',
    '{
        "transfer": {
            "fixed_fee": 10.00,
            "percentage_fee": 0.5,
            "max_fee": 100.00,
            "min_fee": 10.00
        },
        "airtime": {
            "commission_percentage": 2.0,
            "min_commission": 5.00,
            "max_commission": 50.00
        },
        "data": {
            "commission_percentage": 3.0,
            "min_commission": 5.00,
            "max_commission": 100.00
        },
        "crypto": {
            "buy_spread": 1.5,
            "sell_spread": 1.5,
            "min_spread": 0.5,
            "max_spread": 3.0
        }
    }'::jsonb,
    'Default fee structure for all transaction types'
),
(
    'daily_limits',
    '{
        "individual_transfer_limit": 500000.00,
        "daily_transfer_limit": 2000000.00,
        "airtime_daily_limit": 50000.00,
        "data_daily_limit": 50000.00,
        "crypto_daily_limit": 1000000.00
    }'::jsonb,
    'Daily transaction limits for users'
),
(
    'business_settings',
    '{
        "company_name": "Sofi AI",
        "support_email": "support@sofi-ai.com",
        "support_phone": "+234-800-SOFI-AI",
        "website": "https://sofi-ai.com",
        "business_hours": "24/7 AI Support Available"
    }'::jsonb,
    'Business information and contact details'
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_settings_key ON public.settings(key);

-- Set up RLS policies
ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;

-- Allow read access to authenticated users
CREATE POLICY "Allow read access to settings" ON public.settings
    FOR SELECT
    USING (true);

-- Only allow admin updates (you can modify this based on your admin system)
CREATE POLICY "Allow admin updates to settings" ON public.settings
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

COMMENT ON TABLE public.settings IS 'Configuration settings for Sofi AI system including fees, limits, and business info';
