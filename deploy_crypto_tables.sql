-- DEPLOY CRYPTO & REVENUE TRACKING TABLES
-- Execute this in Supabase SQL Editor

-- 1. Crypto Rates Table (for rate history tracking)
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

-- 2. Crypto Trades Table (transaction tracking)
CREATE TABLE IF NOT EXISTS crypto_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT', 'ETH')),
    crypto_amount NUMERIC NOT NULL,
    naira_equivalent NUMERIC NOT NULL,
    conversion_rate_used NUMERIC NOT NULL,
    profit_made NUMERIC DEFAULT 0,
    transaction_hash TEXT,
    status TEXT DEFAULT 'completed',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Financial Summary Table (main revenue tracking)
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

-- 4. Bank Transactions Table (if missing)
CREATE TABLE IF NOT EXISTS bank_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id TEXT NOT NULL,
    transaction_reference TEXT UNIQUE NOT NULL,
    amount NUMERIC NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('credit', 'debit', 'transfer')),
    account_number TEXT,
    bank_name TEXT,
    recipient_name TEXT,
    narration TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    webhook_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Transfer Charges Table (fee tracking)
CREATE TABLE IF NOT EXISTS transfer_charges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transfer_amount NUMERIC NOT NULL,
    fee_amount NUMERIC NOT NULL,
    transaction_reference TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert initial financial summary record
INSERT INTO sofi_financial_summary (id) VALUES (uuid_generate_v4())
ON CONFLICT DO NOTHING;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_crypto_rates_timestamp ON crypto_rates(timestamp);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_user ON crypto_trades(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_user ON transfer_charges(telegram_chat_id);

-- Enable Row Level Security (RLS)
ALTER TABLE crypto_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow service role access)
CREATE POLICY "Enable all operations for service role" ON crypto_rates FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON crypto_trades FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON sofi_financial_summary FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON bank_transactions FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON transfer_charges FOR ALL USING (true);

-- Verify tables created
SELECT 
    table_name,
    'Created successfully' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('crypto_rates', 'crypto_trades', 'sofi_financial_summary', 'bank_transactions', 'transfer_charges');
