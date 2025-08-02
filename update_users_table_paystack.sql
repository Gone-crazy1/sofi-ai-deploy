-- Update Supabase users table to support Paystack virtual accounts
-- This adds the missing columns needed for the new account system

-- Add Paystack-specific columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS account_name TEXT,
ADD COLUMN IF NOT EXISTS account_number TEXT,
ADD COLUMN IF NOT EXISTS bank_name TEXT DEFAULT 'Wema Bank',
ADD COLUMN IF NOT EXISTS bank_code TEXT DEFAULT '035',
ADD COLUMN IF NOT EXISTS account_reference TEXT,
ADD COLUMN IF NOT EXISTS paystack_customer_id TEXT,
ADD COLUMN IF NOT EXISTS paystack_customer_code TEXT,
ADD COLUMN IF NOT EXISTS pin_hash TEXT,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS platform TEXT DEFAULT 'whatsapp',
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_users_account_number ON users(account_number);
CREATE INDEX IF NOT EXISTS idx_users_paystack_customer_code ON users(paystack_customer_code);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- Update any existing users to have proper status
UPDATE users SET status = 'active' WHERE status IS NULL;
UPDATE users SET platform = 'whatsapp' WHERE platform IS NULL AND whatsapp_number IS NOT NULL;

-- Add constraint to ensure account numbers are unique
ALTER TABLE users ADD CONSTRAINT unique_account_number UNIQUE (account_number);

COMMENT ON COLUMN users.account_name IS 'Virtual account name from Paystack';
COMMENT ON COLUMN users.account_number IS 'Virtual account number from Paystack';
COMMENT ON COLUMN users.bank_name IS 'Bank name for virtual account (default: Wema Bank)';
COMMENT ON COLUMN users.bank_code IS 'Bank code for virtual account (default: 035)';
COMMENT ON COLUMN users.paystack_customer_id IS 'Paystack customer numeric ID';
COMMENT ON COLUMN users.paystack_customer_code IS 'Paystack customer code (CUS_...)';
COMMENT ON COLUMN users.metadata IS 'Additional user metadata as JSON';
COMMENT ON COLUMN users.platform IS 'Platform where user was created (whatsapp, web, app)';
COMMENT ON COLUMN users.status IS 'User account status (active, suspended, pending)';
