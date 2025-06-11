-- Add missing columns for enhanced onboarding
-- Run this in Supabase SQL Editor

-- Add country column if it doesn't exist
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS country VARCHAR(100);

-- Add email column if it doesn't exist  
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Add comments to track changes
COMMENT ON COLUMN public.users.country IS 'User country for KYC compliance';
COMMENT ON COLUMN public.users.email IS 'User email address for notifications';

-- Verify the columns were added
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('country', 'email', 'phone', 'pin', 'address', 'city', 'state')
ORDER BY column_name;
