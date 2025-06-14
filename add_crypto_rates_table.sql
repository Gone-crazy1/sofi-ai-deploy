-- Add crypto_rates table to track rate history and margins
-- Run this in Supabase SQL Editor after the main revenue tracking tables

-- Crypto Rates History Table
CREATE TABLE IF NOT EXISTS crypto_rates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    btc_market_rate NUMERIC NOT NULL,
    btc_sofi_rate NUMERIC NOT NULL,
    usdt_market_rate NUMERIC NOT NULL,
    usdt_sofi_rate NUMERIC NOT NULL,
    source TEXT DEFAULT 'coingecko',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_crypto_rates_timestamp ON crypto_rates(timestamp);

-- Enable RLS
ALTER TABLE crypto_rates ENABLE ROW LEVEL SECURITY;

-- Policy for service role access
CREATE POLICY "Allow service role full access to crypto_rates" ON crypto_rates
    FOR ALL USING (true);

-- Update the crypto_trades table to include more profit tracking details
-- (This enhances the existing table from the revenue system)
ALTER TABLE crypto_trades ADD COLUMN IF NOT EXISTS market_rate NUMERIC;
ALTER TABLE crypto_trades ADD COLUMN IF NOT EXISTS sofi_rate NUMERIC;
ALTER TABLE crypto_trades ADD COLUMN IF NOT EXISTS rate_margin_percentage NUMERIC;

-- Create a view for easy profit analysis
CREATE OR REPLACE VIEW crypto_profit_analysis AS
SELECT 
    ct.id,
    ct.telegram_chat_id,
    ct.crypto_type,
    ct.crypto_amount,
    ct.naira_equivalent,
    ct.market_rate,
    ct.sofi_rate,
    ct.profit_made_on_trade,
    (ct.market_rate - ct.sofi_rate) as rate_difference,
    ((ct.market_rate - ct.sofi_rate) / ct.market_rate * 100) as profit_margin_percentage,
    ct.timestamp
FROM crypto_trades ct
WHERE ct.market_rate IS NOT NULL AND ct.sofi_rate IS NOT NULL
ORDER BY ct.timestamp DESC;
