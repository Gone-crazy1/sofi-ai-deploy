-- Complete WhatsApp Integration Schema Update
-- Add all missing columns needed for WhatsApp account creation
-- Run this ONCE in your Supabase SQL Editor

-- Add BVN column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS bvn TEXT;

-- Add WhatsApp specific columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS whatsapp_phone TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Add Paystack virtual account columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS ninepsb_account_number TEXT,
ADD COLUMN IF NOT EXISTS ninepsb_bank_name TEXT DEFAULT 'Wema Bank',
ADD COLUMN IF NOT EXISTS ninepsb_bank_code TEXT DEFAULT '035',
ADD COLUMN IF NOT EXISTS ninepsb_wallet_created BOOLEAN DEFAULT false;

-- Add Paystack customer info columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS paystack_customer_code TEXT,
ADD COLUMN IF NOT EXISTS paystack_customer_id TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_bvn ON users(bvn);
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_phone ON users(whatsapp_phone);
CREATE INDEX IF NOT EXISTS idx_users_ninepsb_account ON users(ninepsb_account_number);
CREATE INDEX IF NOT EXISTS idx_users_paystack_customer ON users(paystack_customer_code);

-- Comments for documentation
COMMENT ON COLUMN users.bvn IS 'Bank Verification Number for user verification';
COMMENT ON COLUMN users.whatsapp_phone IS 'WhatsApp phone number for WhatsApp users';
COMMENT ON COLUMN users.address IS 'User address information';
COMMENT ON COLUMN users.notes IS 'Additional user metadata as JSON';
COMMENT ON COLUMN users.ninepsb_account_number IS 'Virtual account number from banking provider';
COMMENT ON COLUMN users.ninepsb_bank_name IS 'Bank name for virtual account';
COMMENT ON COLUMN users.ninepsb_bank_code IS 'Bank code for virtual account';
COMMENT ON COLUMN users.paystack_customer_code IS 'Paystack customer code (CUS_...)';
COMMENT ON COLUMN users.paystack_customer_id IS 'Paystack customer numeric ID';

-- Update any existing users to have proper defaults
UPDATE users SET ninepsb_wallet_created = false WHERE ninepsb_wallet_created IS NULL;
