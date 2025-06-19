-- 🔐 SECURE TRANSACTION VALIDATION TABLES
-- Creates tables needed for secure PIN verification and transaction validation

-- Table for tracking PIN attempts and account lockouts
CREATE TABLE IF NOT EXISTS pin_attempts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    failed_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    UNIQUE(user_id)
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_pin_attempts_user_id ON pin_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_pin_attempts_locked_until ON pin_attempts(locked_until);

-- Ensure virtual_accounts has balance column
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS balance DECIMAL(15,2) DEFAULT 0.00;

-- Update existing accounts to have 0 balance if NULL
UPDATE virtual_accounts 
SET balance = 0.00 
WHERE balance IS NULL;

-- Add transaction limits tracking (optional for future use)
CREATE TABLE IF NOT EXISTS daily_transaction_limits (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    transaction_date DATE DEFAULT CURRENT_DATE,
    transaction_count INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one record per user per day
    UNIQUE(user_id, transaction_date)
);

-- Index for daily limits
CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON daily_transaction_limits(user_id, transaction_date);

-- Add security audit log table
CREATE TABLE IF NOT EXISTS security_audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL, -- 'pin_attempt', 'account_locked', 'balance_check', etc.
    event_details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for audit log
CREATE INDEX IF NOT EXISTS idx_security_audit_user_id ON security_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_event_type ON security_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_security_audit_created_at ON security_audit_log(created_at);

-- Enable Row Level Security on sensitive tables
ALTER TABLE pin_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_transaction_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_audit_log ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only access their own data)
CREATE POLICY "Users can access their own PIN attempts" ON pin_attempts
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY "Users can access their own daily limits" ON daily_transaction_limits
    FOR ALL USING (auth.uid()::text = user_id);

CREATE POLICY "Users can access their own audit logs" ON security_audit_log
    FOR ALL USING (auth.uid()::text = user_id);

-- Grant necessary permissions
GRANT ALL ON pin_attempts TO authenticated;
GRANT ALL ON daily_transaction_limits TO authenticated;
GRANT ALL ON security_audit_log TO authenticated;

-- Comments for documentation
COMMENT ON TABLE pin_attempts IS 'Tracks PIN verification attempts and account lockouts for security';
COMMENT ON TABLE daily_transaction_limits IS 'Tracks daily transaction counts and amounts for limit enforcement';
COMMENT ON TABLE security_audit_log IS 'Logs security-related events for monitoring and compliance';

-- Insert test data for development (remove in production)
-- This creates a test PIN attempt record to verify the system works
-- In production, this would be created automatically when users attempt PIN verification
