-- Fix Sharp AI database issues
-- Add missing last_message column to user_profiles table

-- Add the missing last_message column
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS last_message TEXT;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_profiles' 
AND column_name = 'last_message';

-- Test query to ensure the table works properly
SELECT COUNT(*) as total_profiles FROM user_profiles;
