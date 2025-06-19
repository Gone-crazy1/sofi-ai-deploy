-- 🗄️ COMPLETE SOFI AI DATABASE SCHEMA
-- Deploy all missing tables for full functionality

-- 1. Create missing airtime_transactions table
CREATE TABLE IF NOT EXISTS airtime_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    network TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    profit_amount DECIMAL(10,2) DEFAULT 0,
    status TEXT DEFAULT 'pending',
    transaction_reference TEXT UNIQUE,
    api_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create missing data_transactions table  
CREATE TABLE IF NOT EXISTS data_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    network TEXT NOT NULL,
    data_plan TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    profit_amount DECIMAL(10,2) DEFAULT 0,
    status TEXT DEFAULT 'pending',
    transaction_reference TEXT UNIQUE,
    api_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create missing crypto_profits table
CREATE TABLE IF NOT EXISTS crypto_profits (
    id BIGSERIAL PRIMARY KEY,
    transaction_id TEXT REFERENCES crypto_transactions(id),
    user_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL,
    buy_rate DECIMAL(15,2) NOT NULL,
    sell_rate DECIMAL(15,2) NOT NULL,
    profit_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Ensure admin_profit_summary view exists
CREATE OR REPLACE VIEW admin_profit_summary AS
SELECT 
    COALESCE(SUM(profit_amount), 0) as total_profit_earned,
    COALESCE((SELECT SUM(withdrawal_amount) FROM admin_withdrawals WHERE status = 'completed'), 0) as total_withdrawn,
    COALESCE(SUM(profit_amount), 0) - COALESCE((SELECT SUM(withdrawal_amount) FROM admin_withdrawals WHERE status = 'completed'), 0) as available_profit,
    COUNT(*) as total_profit_transactions,
    MAX(created_at) as last_profit_date
FROM admin_profits;

-- 5. Add missing columns to existing tables
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

ALTER TABLE virtual_accounts ADD COLUMN IF NOT EXISTS balance DECIMAL(15,2) DEFAULT 0;
ALTER TABLE virtual_accounts ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 6. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_virtual_accounts_user_id ON virtual_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user_id ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_profits_created_at ON admin_profits(created_at);
CREATE INDEX IF NOT EXISTS idx_airtime_transactions_user_id ON airtime_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_data_transactions_user_id ON data_transactions(user_id);

-- 7. Create notification_settings table for user preferences
CREATE TABLE IF NOT EXISTS notification_settings (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    transaction_alerts BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Create system_settings table for admin configuration
CREATE TABLE IF NOT EXISTS system_settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('transfer_fee_percentage', '1.5', 'Percentage fee for transfers'),
('crypto_margin_percentage', '2.0', 'Profit margin for crypto trades'),
('airtime_margin_percentage', '3.0', 'Profit margin for airtime purchases'),
('data_margin_percentage', '5.0', 'Profit margin for data purchases'),
('min_transfer_amount', '100', 'Minimum transfer amount in NGN'),
('max_transfer_amount', '500000', 'Maximum transfer amount in NGN'),
('daily_transfer_limit', '2000000', 'Daily transfer limit per user'),
('admin_chat_ids', '[]', 'JSON array of admin Telegram chat IDs')
ON CONFLICT (setting_key) DO NOTHING;

-- 9. Enable Row Level Security (RLS) for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE virtual_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE airtime_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_transactions ENABLE ROW LEVEL SECURITY;

-- 10. Create RLS policies for user data protection
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid()::text = telegram_id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid()::text = telegram_id);

CREATE POLICY "Users can view own accounts" ON virtual_accounts FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can view own transactions" ON bank_transactions FOR SELECT USING (auth.uid()::text = user_id);

-- Grant necessary permissions (run as admin)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO anon;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_virtual_accounts_updated_at BEFORE UPDATE ON virtual_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_airtime_transactions_updated_at BEFORE UPDATE ON airtime_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_data_transactions_updated_at BEFORE UPDATE ON data_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
