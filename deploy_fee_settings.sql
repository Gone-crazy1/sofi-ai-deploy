-- SOFI AI WALLET - COMPREHENSIVE FEE SETTINGS UPDATE
-- Execute this in your Supabase SQL editor to configure all fee settings

-- Update settings table with exact fee structure from specifications
INSERT INTO settings (key, value, description) VALUES
('sofi_deposit_fee', '50', 'Sofi deposit fee charged to user (₦50)'),
('opay_deposit_fee', '10', 'OPay processing fee for deposits (hidden from user)'),
('sofi_transfer_fee', '10', 'Sofi service fee for transfers (₦10)'),
('opay_transfer_fee', '20', 'OPay processing fee for transfers (₦20)'),
('crypto_buy_rate', '1550', 'Exchange rate when buying crypto from users ($1 = ₦1550)'),
('crypto_sell_rate', '1600', 'Exchange rate when selling crypto to users ($1 = ₦1600)'),
('crypto_deposit_fee_usd', '1', 'Crypto deposit processing fee ($1)'),
('airtime_commission_rate', '3', 'Commission rate for airtime purchases (3%)'),
('data_commission_rate', '5', 'Commission rate for data purchases (5%)'),
('daily_limit_unverified', '200000', 'Daily transaction limit for unverified users (₦200,000)'),
('daily_limit_verified', '1000000', 'Daily transaction limit for verified users (₦1,000,000)')
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    updated_at = NOW();

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
CREATE INDEX IF NOT EXISTS idx_profits_date ON profits(date);
CREATE INDEX IF NOT EXISTS idx_profits_source ON profits(source);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

-- Add comments to tables for clarity
COMMENT ON TABLE settings IS 'Admin-configurable fee settings for Sofi AI Wallet';
COMMENT ON TABLE profits IS 'Daily profit tracking by source (deposit, transfer, crypto, etc.)';

-- Verify settings are correct
SELECT key, value, description FROM settings ORDER BY key;
