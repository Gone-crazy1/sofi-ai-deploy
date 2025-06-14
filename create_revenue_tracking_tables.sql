
-- Sofi AI Revenue Tracking System - Complete Database Schema
-- Run these commands in your Supabase SQL Editor

-- 1. Main Financial Summary Table
CREATE TABLE IF NOT EXISTS sofi_financial_summary (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    total_revenue NUMERIC DEFAULT 0,
    total_crypto_received_usdt NUMERIC DEFAULT 0,
    total_crypto_received_btc NUMERIC DEFAULT 0,
    total_naira_debited_for_crypto NUMERIC DEFAULT 0,
    total_crypto_profit NUMERIC DEFAULT 0,
    total_transfer_revenue NUMERIC DEFAULT 0,
    total_airtime_revenue NUMERIC DEFAULT 0,
    total_data_revenue NUMERIC DEFAULT 0,
    total_crypto_debit NUMERIC DEFAULT 0,
    total_airtime_amount_sold NUMERIC DEFAULT 0,
    total_data_amount_sold NUMERIC DEFAULT 0,
    total_crypto_naira_paid NUMERIC DEFAULT 0,
    total_conversion_rate_avg NUMERIC DEFAULT 0,
    total_transfer_fee_collected NUMERIC DEFAULT 0,
    total_deposit_fee_collected NUMERIC DEFAULT 0,
    total_personal_withdrawal NUMERIC DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Crypto Trades Tracking
CREATE TABLE IF NOT EXISTS crypto_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT', 'ETH')),
    crypto_amount NUMERIC NOT NULL,
    naira_equivalent NUMERIC NOT NULL,
    conversion_rate_used NUMERIC NOT NULL,
    profit_made_on_trade NUMERIC DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Airtime Sales Tracking
CREATE TABLE IF NOT EXISTS airtime_sales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    network TEXT NOT NULL CHECK (network IN ('MTN', 'Airtel', 'Glo', '9mobile')),
    amount_sold NUMERIC NOT NULL,
    sale_price NUMERIC NOT NULL,
    cost_price NUMERIC NOT NULL,
    profit NUMERIC GENERATED ALWAYS AS (sale_price - cost_price) STORED,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Data Sales Tracking
CREATE TABLE IF NOT EXISTS data_sales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    network TEXT NOT NULL CHECK (network IN ('MTN', 'Airtel', 'Glo', '9mobile')),
    bundle_size TEXT NOT NULL,
    amount_sold NUMERIC NOT NULL,
    sale_price NUMERIC NOT NULL,
    cost_price NUMERIC NOT NULL,
    profit NUMERIC GENERATED ALWAYS AS (sale_price - cost_price) STORED,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Transfer Charges Tracking
CREATE TABLE IF NOT EXISTS transfer_charges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transfer_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Deposit Fees Tracking (New)
CREATE TABLE IF NOT EXISTS deposit_fees (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    deposit_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    fee_type TEXT DEFAULT 'bank_deposit',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_crypto_trades_chat_id ON crypto_trades(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_timestamp ON crypto_trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_airtime_sales_chat_id ON airtime_sales(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_data_sales_chat_id ON data_sales(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_chat_id ON transfer_charges(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_deposit_fees_chat_id ON deposit_fees(telegram_chat_id);

-- 8. Initialize the main summary record (run once)
INSERT INTO sofi_financial_summary DEFAULT VALUES 
ON CONFLICT DO NOTHING;

-- 9. Revenue calculation function
CREATE OR REPLACE FUNCTION calculate_total_revenue()
RETURNS NUMERIC AS $$
DECLARE
    revenue NUMERIC := 0;
BEGIN
    SELECT 
        COALESCE(SUM(profit_made_on_trade), 0) +
        COALESCE((SELECT SUM(profit) FROM airtime_sales), 0) +
        COALESCE((SELECT SUM(profit) FROM data_sales), 0) +
        COALESCE((SELECT SUM(fee_charged) FROM transfer_charges), 0) +
        COALESCE((SELECT SUM(fee_charged) FROM deposit_fees), 0)
    INTO revenue
    FROM crypto_trades;
    
    RETURN revenue;
END;
$$ LANGUAGE plpgsql;

-- 10. Update summary trigger (optional)
CREATE OR REPLACE FUNCTION update_financial_summary()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sofi_financial_summary 
    SET 
        total_revenue = calculate_total_revenue(),
        total_crypto_profit = (SELECT COALESCE(SUM(profit_made_on_trade), 0) FROM crypto_trades),
        total_airtime_revenue = (SELECT COALESCE(SUM(profit), 0) FROM airtime_sales),
        total_data_revenue = (SELECT COALESCE(SUM(profit), 0) FROM data_sales),
        total_transfer_fee_collected = (SELECT COALESCE(SUM(fee_charged), 0) FROM transfer_charges),
        total_deposit_fee_collected = (SELECT COALESCE(SUM(fee_charged), 0) FROM deposit_fees),
        last_updated = NOW()
    WHERE id = (SELECT id FROM sofi_financial_summary LIMIT 1);
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Enable RLS (Row Level Security) for all tables
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE airtime_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposit_fees ENABLE ROW LEVEL SECURITY;

-- Create policies to allow service role access
CREATE POLICY "Service role can manage financial summary" ON sofi_financial_summary
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage crypto trades" ON crypto_trades
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage airtime sales" ON airtime_sales
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage data sales" ON data_sales
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage transfer charges" ON transfer_charges
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage deposit fees" ON deposit_fees
    FOR ALL USING (auth.role() = 'service_role');
