-- Update users table to include all Flow fields
-- Run this in your Supabase SQL Editor

-- Add missing columns if they don't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS last_name TEXT,
ADD COLUMN IF NOT EXISTS bvn TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS signup_source TEXT DEFAULT 'web',
ADD COLUMN IF NOT EXISTS flow_token TEXT,
ADD COLUMN IF NOT EXISTS registration_completed BOOLEAN DEFAULT FALSE;

-- Add missing timestamp columns if they don't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_first_name ON users(first_name);
CREATE INDEX IF NOT EXISTS idx_users_last_name ON users(last_name);
CREATE INDEX IF NOT EXISTS idx_users_bvn ON users(bvn);
CREATE INDEX IF NOT EXISTS idx_users_flow_token ON users(flow_token);
CREATE INDEX IF NOT EXISTS idx_users_signup_source ON users(signup_source);

-- Add comments for documentation
COMMENT ON COLUMN users.first_name IS 'User first name from WhatsApp Flow';
COMMENT ON COLUMN users.last_name IS 'User last name from WhatsApp Flow';
COMMENT ON COLUMN users.bvn IS 'Bank Verification Number for user verification';
COMMENT ON COLUMN users.address IS 'User address information';
COMMENT ON COLUMN users.signup_source IS 'How user signed up (whatsapp_flow, web, etc)';
COMMENT ON COLUMN users.flow_token IS 'WhatsApp Flow token for tracking submissions';
COMMENT ON COLUMN users.registration_completed IS 'Whether user completed full registration';

-- Update existing users to have default values
UPDATE users 
SET 
    signup_source = 'web',
    registration_completed = TRUE,
    created_at = NOW(),
    updated_at = NOW()
WHERE signup_source IS NULL OR registration_completed IS NULL;

-- Show table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
