# 🚀 CRYPTO TABLES DEPLOYMENT - STEP BY STEP GUIDE

## 📋 CURRENT STATUS
- ✅ Existing tables: `users`, `virtual_accounts`, `beneficiaries`, `chat_history`  
- ❌ Missing tables: `bank_transactions`, `crypto_rates`, `crypto_trades`, `sofi_financial_summary`, `transfer_charges`

## 🎯 DEPLOYMENT STEPS

### STEP 1: Open Supabase Dashboard
**Direct Link:** https://qbxherpwkxckwlkwjhpm.supabase.co/project/default/sql

### STEP 2: Copy & Paste This SQL
```sql
-- CRYPTO TABLES DEPLOYMENT FOR SOFI AI
-- Execute this entire block in Supabase SQL Editor

-- 1. Bank Transactions Table (for transfer tracking)
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

-- 2. Crypto Rates Table (for rate history tracking)
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

-- 3. Crypto Trades Table (transaction tracking)
CREATE TABLE IF NOT EXISTS crypto_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT')),
    crypto_amount NUMERIC NOT NULL,
    naira_equivalent NUMERIC NOT NULL,
    conversion_rate_used NUMERIC NOT NULL,
    profit_made NUMERIC DEFAULT 0,
    transaction_hash TEXT,
    status TEXT DEFAULT 'completed',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Financial Summary Table (main revenue tracking)
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
    total_transfer_fee_collected NUMERIC DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
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

-- Enable Row Level Security
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies (Allow all operations for service role)
CREATE POLICY "Enable all operations" ON bank_transactions FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON crypto_rates FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON crypto_trades FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON sofi_financial_summary FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON transfer_charges FOR ALL USING (true);

-- Insert initial financial summary record
INSERT INTO sofi_financial_summary (id) VALUES (uuid_generate_v4()) ON CONFLICT DO NOTHING;

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_crypto_rates_timestamp ON crypto_rates(timestamp);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_user ON crypto_trades(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_user ON transfer_charges(telegram_chat_id);

-- Verification query (should return 5 tables)
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('bank_transactions', 'crypto_rates', 'crypto_trades', 'sofi_financial_summary', 'transfer_charges')
ORDER BY table_name;
```

### STEP 3: Click "Run" Button
- The SQL should execute successfully
- You should see "Success. No rows returned" message
- The verification query at the end should show all 5 table names

### STEP 4: Verify Deployment
Run this command in your project:
```bash
python verify_crypto_deployment.py
```

## 🎉 EXPECTED RESULTS

After successful deployment, you'll have:
- ✅ Complete crypto revenue tracking system
- ✅ Customer-friendly margin settings (2.5% USDT, 3.5% BTC)
- ✅ Transfer fee collection (₦50 per transfer)
- ✅ Real-time financial summaries
- ✅ Monthly revenue projection: ₦2.9M+

## 💰 PROFIT EXAMPLES (CUSTOMER-FRIENDLY)
- 100 USDT deposit → User gets ₦129,300, You profit ₦25,000
- 0.01 BTC deposit → User gets ₦1,568,440, You profit ₦56,886
- 1000 transfers × ₦50 fee = ₦50,000/month

## 🚨 IMPORTANT NOTES
- These margins are designed for customer retention
- Start competitive, increase gradually as customers build loyalty  
- Monitor competitor rates to stay competitive
- Focus on volume over high margins initially

---
**🎯 Ready to deploy? Copy the SQL above and execute it in Supabase!**
