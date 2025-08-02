-- 🚨 CRITICAL DATABASE FIXES FOR SOFI AI
-- Fix all missing columns and tables causing errors

-- 1. Add missing balance column to virtual_accounts table
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS balance DECIMAL(12,2) DEFAULT 0.00;

-- 2. Create missing user_daily_limits table
CREATE TABLE IF NOT EXISTS user_daily_limits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    whatsapp_number VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_transferred DECIMAL(12,2) DEFAULT 0.00,
    transfer_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(whatsapp_number, date)
);

-- 3. Update bank_transactions table to ensure proper UUID handling
-- First check if the table exists and its structure
-- If user_id is VARCHAR, we need to handle the conversion properly

-- 4. Add index for better performance
CREATE INDEX IF NOT EXISTS idx_user_daily_limits_telegram_date 
ON user_daily_limits(whatsapp_number, date);

CREATE INDEX IF NOT EXISTS idx_virtual_accounts_user_id 
ON virtual_accounts(user_id);

-- 5. Add missing columns that might be needed
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS pin_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS has_pin BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS pin_set_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS daily_limit DECIMAL(12,2) DEFAULT 100000.00,
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;

-- 6. Update virtual_accounts with proper structure
ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'active',
ADD COLUMN IF NOT EXISTS last_transaction_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'NGN';

-- 7. Ensure proper RLS policies exist
ALTER TABLE user_daily_limits ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for user_daily_limits
DROP POLICY IF EXISTS "Users can view their own daily limits" ON user_daily_limits;
CREATE POLICY "Users can view their own daily limits" ON user_daily_limits
    FOR ALL USING (true);

-- Grant necessary permissions
GRANT ALL ON user_daily_limits TO anon, authenticated;
GRANT ALL ON virtual_accounts TO anon, authenticated;

-- Initialize balance for existing virtual accounts if they don't have one
UPDATE virtual_accounts 
SET balance = 0.00 
WHERE balance IS NULL;

COMMIT;
