-- SOFI AI COMPLETE DATABASE SCHEMA DEPLOYMENT
-- This includes all missing tables for the Sofi AI system

-- 1. Bank Transactions Table (Missing from transfer fixes)
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

-- 2. Main Financial Summary Table
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

-- 3. Crypto Trades Tracking
CREATE TABLE IF NOT EXISTS crypto_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT', 'ETH')),
    crypto_amount NUMERIC NOT NULL,
    naira_equivalent NUMERIC NOT NULL,
    conversion_rate_used NUMERIC NOT NULL,
    profit_made_on_trade NUMERIC DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Airtime Sales Tracking
CREATE TABLE IF NOT EXISTS airtime_sales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    network TEXT NOT NULL CHECK (network IN ('MTN', 'Airtel', 'Glo', '9mobile')),
    amount_sold NUMERIC NOT NULL,
    sale_price NUMERIC NOT NULL,
    cost_price NUMERIC NOT NULL,
    profit NUMERIC GENERATED ALWAYS AS (sale_price - cost_price) STORED,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Data Sales Tracking
CREATE TABLE IF NOT EXISTS data_sales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    network TEXT NOT NULL CHECK (network IN ('MTN', 'Airtel', 'Glo', '9mobile')),
    bundle_size TEXT NOT NULL,
    amount_sold NUMERIC NOT NULL,
    sale_price NUMERIC NOT NULL,
    cost_price NUMERIC NOT NULL,
    profit NUMERIC GENERATED ALWAYS AS (sale_price - cost_price) STORED,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Transfer Charges Tracking
CREATE TABLE IF NOT EXISTS transfer_charges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    transfer_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    transaction_reference TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Deposit Fees Tracking
CREATE TABLE IF NOT EXISTS deposit_fees (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    deposit_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    fee_type TEXT DEFAULT 'bank_deposit',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user_id ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_reference ON bank_transactions(transaction_reference);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_created_at ON bank_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_chat_id ON crypto_trades(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_timestamp ON crypto_trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_airtime_sales_chat_id ON airtime_sales(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_data_sales_chat_id ON data_sales(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_chat_id ON transfer_charges(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_deposit_fees_chat_id ON deposit_fees(whatsapp_number);

-- 9. Initialize the main summary record (run once)
INSERT INTO sofi_financial_summary DEFAULT VALUES 
ON CONFLICT DO NOTHING;

-- 10. Revenue calculation function
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

-- 11. Update summary trigger function
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

-- 12. Enable Row Level Security for all tables
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE airtime_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposit_fees ENABLE ROW LEVEL SECURITY;

-- 13. Create policies for service role access
CREATE POLICY "Allow service role full access to bank_transactions" ON bank_transactions
    FOR ALL USING (true);

CREATE POLICY "Allow service role full access to sofi_financial_summary" ON sofi_financial_summary
    FOR ALL USING (true);

CREATE POLICY "Allow service role full access to crypto_trades" ON crypto_trades
    FOR ALL USING (true);

CREATE POLICY "Allow service role full access to airtime_sales" ON airtime_sales
    FOR ALL USING (true);

CREATE POLICY "Allow service role full access to data_sales" ON data_sales
    FOR ALL USING (true);

CREATE POLICY "Allow service role full access to transfer_charges" ON transfer_charges
    FOR ALL USING (true);

CREATE POLICY "Allow service role full access to deposit_fees" ON deposit_fees
    FOR ALL USING (true);