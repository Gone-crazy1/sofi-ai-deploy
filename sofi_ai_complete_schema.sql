-- SOFI AI COMPLETE DATABASE SCHEMA
-- Run this in your Supabase SQL editor to create all required tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE (Main user data with OPay virtual accounts)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_id TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    opay_account_number TEXT UNIQUE,
    opay_account_name TEXT,
    opay_bank_name TEXT DEFAULT 'OPay',
    bvn TEXT,
    is_verified BOOLEAN DEFAULT false,
    daily_limit DECIMAL(15,2) DEFAULT 200000.00,
    total_balance DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TRANSACTIONS TABLE (All user transactions)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    telegram_id TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('deposit', 'transfer', 'crypto_buy', 'crypto_sell', 'airtime', 'data')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    reference TEXT UNIQUE,
    recipient_name TEXT,
    recipient_account TEXT,
    recipient_bank TEXT,
    description TEXT,
    fees DECIMAL(15,2) DEFAULT 0.00,
    webhook_data JSONB,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PROFITS TABLE (Track all profit sources)
CREATE TABLE IF NOT EXISTS profits (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source TEXT NOT NULL CHECK (source IN ('deposit', 'transfer', 'crypto', 'airtime', 'data')),
    amount DECIMAL(15,2) NOT NULL,
    details TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. SETTINGS TABLE (Admin configurable fees and rates)
CREATE TABLE IF NOT EXISTS settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default fee settings
INSERT INTO settings (key, value, description) VALUES
('deposit_fee_naira', '50', 'Sofi fee for deposits in Naira'),
('transfer_fee_naira', '10', 'Sofi fee for bank transfers in Naira'),
('crypto_deposit_fee_usd', '1', 'Sofi fee for crypto deposits in USD'),
('crypto_buy_rate', '1550', 'Rate for buying crypto (USD to Naira)'),
('crypto_sell_rate', '1600', 'Rate for selling crypto (USD to Naira)'),
('opay_deposit_fee', '10', 'OPay deposit fee (hidden from user)'),
('opay_transfer_fee', '20', 'OPay transfer fee'),
('daily_limit_unverified', '200000', 'Daily limit for unverified users'),
('daily_limit_verified', '1000000', 'Daily limit for verified users'),
('airtime_commission_rate', '3', 'Commission rate for airtime sales (%)'),
('data_commission_rate', '5', 'Commission rate for data sales (%)')
ON CONFLICT (key) DO NOTHING;

-- 5. ADMIN_LOGS TABLE (Track admin queries and actions)
CREATE TABLE IF NOT EXISTS admin_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    admin_telegram_id TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    result TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. CRYPTO_TRANSACTIONS TABLE (Crypto specific transactions)
CREATE TABLE IF NOT EXISTS crypto_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    telegram_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT', 'ETH')),
    crypto_amount DECIMAL(20,8) NOT NULL,
    naira_equivalent DECIMAL(15,2) NOT NULL,
    exchange_rate DECIMAL(10,2) NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('buy', 'sell', 'deposit')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    reference TEXT UNIQUE,
    wallet_address TEXT,
    tx_hash TEXT,
    fees_usd DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. NOTIFICATION_LOGS TABLE (Track sent notifications)
CREATE TABLE IF NOT EXISTS notification_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    telegram_id TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    transaction_reference TEXT,
    message_content TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending'))
);

-- 8. AIRTIME_TRANSACTIONS TABLE (Airtime purchases)
CREATE TABLE IF NOT EXISTS airtime_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    telegram_id TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    network TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    commission DECIMAL(15,2) DEFAULT 0.00,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    reference TEXT UNIQUE,
    provider_reference TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. USER_DAILY_LIMITS TABLE (Track daily spending per user)
CREATE TABLE IF NOT EXISTS user_daily_limits (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    telegram_id TEXT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    total_transferred DECIMAL(15,2) DEFAULT 0.00,
    limit_amount DECIMAL(15,2) DEFAULT 200000.00,
    transactions_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_telegram_id ON transactions(telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_profits_date ON profits(date);
CREATE INDEX IF NOT EXISTS idx_profits_source ON profits(source);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON crypto_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_user_id ON notification_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_airtime_transactions_user_id ON airtime_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_daily_limits_user_date ON user_daily_limits(user_id, date);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE profits ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE airtime_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_daily_limits ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (telegram_id = current_setting('app.current_user_telegram_id', true));

CREATE POLICY "Service can manage users" ON users
    FOR ALL USING (true);

-- RLS Policies for transactions table
CREATE POLICY "Users can view own transactions" ON transactions
    FOR SELECT USING (telegram_id = current_setting('app.current_user_telegram_id', true));

CREATE POLICY "Service can manage transactions" ON transactions
    FOR ALL USING (true);

-- RLS Policies for other tables (service can manage all)
CREATE POLICY "Service can manage profits" ON profits FOR ALL USING (true);
CREATE POLICY "Service can manage crypto_transactions" ON crypto_transactions FOR ALL USING (true);
CREATE POLICY "Service can manage notification_logs" ON notification_logs FOR ALL USING (true);
CREATE POLICY "Service can manage airtime_transactions" ON airtime_transactions FOR ALL USING (true);
CREATE POLICY "Service can manage user_daily_limits" ON user_daily_limits FOR ALL USING (true);

-- Create or replace function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_transactions_updated_at ON transactions;
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_crypto_transactions_updated_at ON crypto_transactions;
CREATE TRIGGER update_crypto_transactions_updated_at
    BEFORE UPDATE ON crypto_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_airtime_transactions_updated_at ON airtime_transactions;
CREATE TRIGGER update_airtime_transactions_updated_at
    BEFORE UPDATE ON airtime_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_daily_limits_updated_at ON user_daily_limits;
CREATE TRIGGER update_user_daily_limits_updated_at
    BEFORE UPDATE ON user_daily_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views for analytics
CREATE OR REPLACE VIEW daily_profit_summary AS
SELECT 
    date,
    SUM(amount) as total_profit,
    COUNT(*) as profit_entries,
    SUM(CASE WHEN source = 'deposit' THEN amount ELSE 0 END) as deposit_profit,
    SUM(CASE WHEN source = 'transfer' THEN amount ELSE 0 END) as transfer_profit,
    SUM(CASE WHEN source = 'crypto' THEN amount ELSE 0 END) as crypto_profit,
    SUM(CASE WHEN source = 'airtime' THEN amount ELSE 0 END) as airtime_profit
FROM profits
GROUP BY date
ORDER BY date DESC;

CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_verified = true THEN 1 END) as verified_users,
    COUNT(CASE WHEN is_verified = false THEN 1 END) as unverified_users,
    SUM(total_balance) as total_wallet_balance,
    AVG(total_balance) as average_balance
FROM users;

CREATE OR REPLACE VIEW daily_transaction_summary AS
SELECT 
    date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_volume,
    COUNT(CASE WHEN type = 'deposit' THEN 1 END) as deposits_count,
    COUNT(CASE WHEN type = 'transfer' THEN 1 END) as transfers_count,
    COUNT(CASE WHEN type = 'crypto_buy' THEN 1 END) as crypto_buys_count,
    COUNT(CASE WHEN type = 'airtime' THEN 1 END) as airtime_count,
    SUM(CASE WHEN type = 'deposit' THEN amount ELSE 0 END) as deposit_volume,
    SUM(CASE WHEN type = 'transfer' THEN amount ELSE 0 END) as transfer_volume
FROM transactions
WHERE status = 'success'
GROUP BY date
ORDER BY date DESC;

-- Grant necessary permissions
GRANT SELECT ON daily_profit_summary TO authenticated, anon;
GRANT SELECT ON user_statistics TO authenticated, anon;
GRANT SELECT ON daily_transaction_summary TO authenticated, anon;

-- Success message
SELECT 'Sofi AI database schema setup complete!' as message,
       'Tables created: users, transactions, profits, settings, crypto_transactions, notification_logs, airtime_transactions, user_daily_limits, admin_logs' as tables_created;
