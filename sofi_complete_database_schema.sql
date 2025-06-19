-- Complete Sofi AI Database Schema
-- This creates all the tables based on the project logic

-- 1. Main users table (corrected structure)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    opay_account_number TEXT UNIQUE,
    opay_account_name TEXT,
    opay_bank_name TEXT DEFAULT 'OPay Digital Services Limited',
    bvn TEXT,
    is_verified BOOLEAN DEFAULT false,
    daily_limit DECIMAL(15,2) DEFAULT 200000.00,
    total_balance DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Transactions table (enhanced)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_id TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('deposit', 'transfer', 'airtime', 'data', 'crypto_buy', 'crypto_sell', 'withdrawal')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'cancelled')),
    reference TEXT UNIQUE,
    recipient_name TEXT,
    recipient_account TEXT,
    recipient_bank TEXT,
    narration TEXT,
    fee DECIMAL(15,2) DEFAULT 0.00,
    webhook_data JSONB,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Profits tracking table
CREATE TABLE IF NOT EXISTS profits (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL CHECK (source IN ('transfer', 'airtime', 'data', 'crypto', 'withdrawal')),
    amount DECIMAL(15,2) NOT NULL,
    transaction_id INTEGER REFERENCES transactions(id),
    user_id INTEGER REFERENCES users(id),
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Admin logs table
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_telegram_id TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    response_data JSONB,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Crypto transactions table
CREATE TABLE IF NOT EXISTS crypto_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT', 'ETH')),
    crypto_amount DECIMAL(20,8) NOT NULL,
    naira_amount DECIMAL(15,2) NOT NULL,
    exchange_rate DECIMAL(15,2) NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('buy', 'sell')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    wallet_address TEXT,
    reference TEXT UNIQUE,
    profit DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Airtime/Data transactions table
CREATE TABLE IF NOT EXISTS utility_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_id TEXT NOT NULL,
    service_type TEXT NOT NULL CHECK (service_type IN ('airtime', 'data')),
    network TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    plan_name TEXT, -- for data plans
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    reference TEXT UNIQUE,
    commission DECIMAL(15,2) DEFAULT 0.00,
    webhook_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. Daily limits tracking
CREATE TABLE IF NOT EXISTS daily_limits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_id TEXT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    total_transferred DECIMAL(15,2) DEFAULT 0.00,
    limit_amount DECIMAL(15,2) DEFAULT 200000.00,
    limit_reached BOOLEAN DEFAULT false,
    upgrade_prompted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- 8. Notification preferences (from previous implementation)
CREATE TABLE IF NOT EXISTS user_notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    telegram_id TEXT NOT NULL,
    deposit_alerts BOOLEAN DEFAULT true,
    transfer_alerts BOOLEAN DEFAULT true,
    airtime_alerts BOOLEAN DEFAULT true,
    low_balance_alerts BOOLEAN DEFAULT true,
    daily_summary BOOLEAN DEFAULT false,
    limit_alerts BOOLEAN DEFAULT true,
    low_balance_threshold DECIMAL(15,2) DEFAULT 1000.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 9. Business metrics cache (for admin dashboard)
CREATE TABLE IF NOT EXISTS business_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE DEFAULT CURRENT_DATE,
    total_profit DECIMAL(15,2) DEFAULT 0.00,
    new_users_count INTEGER DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    total_volume DECIMAL(15,2) DEFAULT 0.00,
    transfer_profit DECIMAL(15,2) DEFAULT 0.00,
    airtime_profit DECIMAL(15,2) DEFAULT 0.00,
    crypto_profit DECIMAL(15,2) DEFAULT 0.00,
    active_users INTEGER DEFAULT 0,
    cached_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(metric_date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_telegram_id ON transactions(telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON daily_limits(user_id, date);
CREATE INDEX IF NOT EXISTS idx_profits_date ON profits(date);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON crypto_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_utility_transactions_user_id ON utility_transactions(user_id);

-- Enable RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE utility_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notification_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (telegram_id = auth.jwt() ->> 'telegram_id');

CREATE POLICY "Service can manage users" ON users
    FOR ALL WITH CHECK (true);

-- RLS Policies for transactions
CREATE POLICY "Users can view own transactions" ON transactions
    FOR SELECT USING (telegram_id = auth.jwt() ->> 'telegram_id');

CREATE POLICY "Service can manage transactions" ON transactions
    FOR ALL WITH CHECK (true);

-- Similar policies for other tables
CREATE POLICY "Service can manage crypto_transactions" ON crypto_transactions
    FOR ALL WITH CHECK (true);

CREATE POLICY "Service can manage utility_transactions" ON utility_transactions
    FOR ALL WITH CHECK (true);

CREATE POLICY "Service can manage daily_limits" ON daily_limits
    FOR ALL WITH CHECK (true);

CREATE POLICY "Service can manage user_notification_preferences" ON user_notification_preferences
    FOR ALL WITH CHECK (true);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_crypto_transactions_updated_at BEFORE UPDATE ON crypto_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_utility_transactions_updated_at BEFORE UPDATE ON utility_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_daily_limits_updated_at BEFORE UPDATE ON daily_limits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_notification_preferences_updated_at BEFORE UPDATE ON user_notification_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Functions for business metrics calculation
CREATE OR REPLACE FUNCTION calculate_daily_profit(target_date DATE DEFAULT CURRENT_DATE)
RETURNS DECIMAL(15,2) AS $$
BEGIN
    RETURN COALESCE((
        SELECT SUM(amount) 
        FROM profits 
        WHERE date = target_date
    ), 0.00);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_new_users_count(target_date DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE((
        SELECT COUNT(*) 
        FROM users 
        WHERE DATE(created_at) = target_date
    ), 0);
END;
$$ LANGUAGE plpgsql;

-- Sample admin user (replace with your actual Telegram ID)
INSERT INTO admin_logs (admin_telegram_id, action, details) 
VALUES ('YOUR_ADMIN_TELEGRAM_ID', 'system_setup', 'Sofi AI database schema initialized')
ON CONFLICT DO NOTHING;

-- Success message
SELECT 
    'Sofi AI Complete Database Schema Created Successfully!' as message,
    'Tables: users, transactions, profits, admin_logs, crypto_transactions, utility_transactions, daily_limits' as tables_created,
    'Ready for: User onboarding, Daily limits, Admin dashboard, Profit tracking' as features_enabled;
