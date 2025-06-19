-- Enhanced Notification System Database Schema
-- Run this in your Supabase SQL editor to create tables for notifications

-- Create notification_logs table to track sent notifications
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    notification_type TEXT NOT NULL, -- 'deposit_alert', 'transfer_alert', 'airtime_alert', etc.
    transaction_reference TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'sent', -- 'sent', 'failed', 'pending'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notification_logs_user_id ON notification_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type);
CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at ON notification_logs(sent_at);

-- Create airtime_transactions table if it doesn't exist
CREATE TABLE IF NOT EXISTS airtime_transactions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    reference TEXT UNIQUE NOT NULL,
    phone_number TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    network TEXT,
    status TEXT DEFAULT 'pending',
    webhook_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for airtime_transactions
CREATE INDEX IF NOT EXISTS idx_airtime_transactions_user_id ON airtime_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_airtime_transactions_reference ON airtime_transactions(reference);
CREATE INDEX IF NOT EXISTS idx_airtime_transactions_status ON airtime_transactions(status);

-- Update virtual_accounts table to ensure balance column exists
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS balance DECIMAL(15,2) DEFAULT 0.00;

-- Update bank_transactions table to include additional fields for enhanced notifications
ALTER TABLE bank_transactions 
ADD COLUMN IF NOT EXISTS sender_name TEXT,
ADD COLUMN IF NOT EXISTS sender_bank TEXT,
ADD COLUMN IF NOT EXISTS recipient_name TEXT,
ADD COLUMN IF NOT EXISTS recipient_bank TEXT,
ADD COLUMN IF NOT EXISTS recipient_account TEXT,
ADD COLUMN IF NOT EXISTS network TEXT; -- for airtime transactions

-- Create or update RLS policies for notification_logs
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;

-- Policy for users to see their own notification logs
CREATE POLICY IF NOT EXISTS "Users can view own notification logs" ON notification_logs
    FOR SELECT USING (user_id = auth.uid()::text);

-- Policy for service to insert notification logs
CREATE POLICY IF NOT EXISTS "Service can insert notification logs" ON notification_logs
    FOR INSERT WITH CHECK (true);

-- Create or update RLS policies for airtime_transactions
ALTER TABLE airtime_transactions ENABLE ROW LEVEL SECURITY;

-- Policy for users to see their own airtime transactions
CREATE POLICY IF NOT EXISTS "Users can view own airtime transactions" ON airtime_transactions
    FOR SELECT USING (user_id = auth.uid()::text);

-- Policy for service to insert airtime transactions
CREATE POLICY IF NOT EXISTS "Service can insert airtime transactions" ON airtime_transactions
    FOR INSERT WITH CHECK (true);

-- Policy for service to update airtime transactions
CREATE POLICY IF NOT EXISTS "Service can update airtime transactions" ON airtime_transactions
    FOR UPDATE USING (true);

-- Create function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_airtime_transactions_updated_at ON airtime_transactions;
CREATE TRIGGER update_airtime_transactions_updated_at
    BEFORE UPDATE ON airtime_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_virtual_accounts_updated_at ON virtual_accounts;
CREATE TRIGGER update_virtual_accounts_updated_at
    BEFORE UPDATE ON virtual_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bank_transactions_updated_at ON bank_transactions;
CREATE TRIGGER update_bank_transactions_updated_at
    BEFORE UPDATE ON bank_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample notification preferences (optional)
CREATE TABLE IF NOT EXISTS user_notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    deposit_alerts BOOLEAN DEFAULT true,
    transfer_alerts BOOLEAN DEFAULT true,
    airtime_alerts BOOLEAN DEFAULT true,
    low_balance_alerts BOOLEAN DEFAULT true,
    daily_summary BOOLEAN DEFAULT false,
    low_balance_threshold DECIMAL(15,2) DEFAULT 1000.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- RLS for notification preferences
ALTER TABLE user_notification_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can manage own notification preferences" ON user_notification_preferences
    FOR ALL USING (user_id = auth.uid()::text);

-- Create trigger for notification preferences updated_at
DROP TRIGGER IF EXISTS update_user_notification_preferences_updated_at ON user_notification_preferences;
CREATE TRIGGER update_user_notification_preferences_updated_at
    BEFORE UPDATE ON user_notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for transaction summary (optional, for analytics)
CREATE OR REPLACE VIEW user_transaction_summary AS
SELECT 
    bt.user_id,
    DATE(bt.created_at) as transaction_date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN bt.transaction_type = 'credit' THEN bt.amount ELSE 0 END) as total_credits,
    SUM(CASE WHEN bt.transaction_type = 'debit' THEN bt.amount ELSE 0 END) as total_debits,
    SUM(CASE WHEN bt.transaction_type = 'credit' THEN bt.amount ELSE -bt.amount END) as net_change
FROM bank_transactions bt
WHERE bt.status = 'success'
GROUP BY bt.user_id, DATE(bt.created_at)
ORDER BY transaction_date DESC;

-- Grant necessary permissions
GRANT SELECT ON user_transaction_summary TO authenticated;
GRANT SELECT ON user_transaction_summary TO anon;

-- Success message
SELECT 'Enhanced notification system database schema setup complete!' as message;
