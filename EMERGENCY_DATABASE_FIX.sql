-- 🚨 EMERGENCY FIX: Add Missing Columns to Users Table
-- Copy and paste this entire SQL script into your Supabase SQL Editor

-- Step 1: Add missing columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS last_name TEXT,
ADD COLUMN IF NOT EXISTS bvn TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS signup_source TEXT DEFAULT 'web',
ADD COLUMN IF NOT EXISTS flow_token TEXT,
ADD COLUMN IF NOT EXISTS registration_completed BOOLEAN DEFAULT FALSE;

-- Step 2: Add missing timestamp columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Step 3: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_first_name ON users(first_name);
CREATE INDEX IF NOT EXISTS idx_users_last_name ON users(last_name);
CREATE INDEX IF NOT EXISTS idx_users_bvn ON users(bvn);
CREATE INDEX IF NOT EXISTS idx_users_flow_token ON users(flow_token);
CREATE INDEX IF NOT EXISTS idx_users_signup_source ON users(signup_source);

-- Step 4: Update existing users with default values
UPDATE users 
SET 
    signup_source = 'web',
    registration_completed = TRUE,
    created_at = COALESCE(created_at, NOW()),
    updated_at = NOW()
WHERE signup_source IS NULL OR registration_completed IS NULL;

-- Step 5: Verify the schema update
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
