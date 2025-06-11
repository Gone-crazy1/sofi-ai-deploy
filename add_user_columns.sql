-- Add missing columns to users table for complete onboarding
-- Run this in Supabase SQL Editor

-- Add country column
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS country VARCHAR(100);

-- Add email column  
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Add comment to track changes
COMMENT ON COLUMN public.users.country IS 'User country for KYC compliance';
COMMENT ON COLUMN public.users.email IS 'User email address for notifications';

-- Verify the columns were added
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('country', 'email')
ORDER BY column_name;
