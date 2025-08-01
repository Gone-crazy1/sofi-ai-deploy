-- 🔧 DATABASE FIXES FOR SOFI AI
-- Run these SQL commands in your Supabase SQL Editor to fix remaining issues

-- 1. Make bank_code nullable in bank_transactions (temporary fix)
ALTER TABLE bank_transactions 
ALTER COLUMN bank_code DROP NOT NULL;

-- 2. Add missing columns if they don't exist
ALTER TABLE bank_transactions 
ADD COLUMN IF NOT EXISTS bank_code VARCHAR(10),
ADD COLUMN IF NOT EXISTsS bank_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS account_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS transaction_type VARCHAR(20) DEFAULT 'credit';

-- 3. Create user_daily_limits table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_daily_limits (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    whatsapp_number TEXT NOT NULL,
    date DATE NOT NULL,
    total_transferred NUMERIC(15,2) DEFAULT 0.00,
    transfer_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(whatsapp_number, date)
);

-- 4. Create index for user_daily_limits
CREATE INDEX IF NOT EXISTS idx_user_daily_limits_telegram_date 
ON user_daily_limits (whatsapp_number, date);

-- 5. Update bank_transactions to handle both UUID and TEXT user_id
-- If your user_id column is TEXT, this should work
-- If it's UUID, the webhook fix should work

-- 6. Enable RLS on user_daily_limits
ALTER TABLE user_daily_limits ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS policy for user_daily_limits
CREATE POLICY "Allow all operations on user_daily_limits" ON user_daily_limits
FOR ALL USING (true) WITH CHECK (true);

-- 8. Grant permissions
GRANT ALL ON user_daily_limits TO anon, authenticated;

-- 9. Add Paystack specific columns if needed
ALTER TABLE bank_transactions 
ADD COLUMN IF NOT EXISTS paystack_reference VARCHAR(100),
ADD COLUMN IF NOT EXISTS paystack_status VARCHAR(50);

COMMIT;
