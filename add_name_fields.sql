-- Add first_name and last_name fields for WhatsApp Flow compatibility
-- Run this in your Supabase SQL Editor

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS last_name TEXT;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_first_name ON users(first_name);
CREATE INDEX IF NOT EXISTS idx_users_last_name ON users(last_name);

-- Add comments for documentation
COMMENT ON COLUMN users.first_name IS 'User first name from WhatsApp Flow';
COMMENT ON COLUMN users.last_name IS 'User last name from WhatsApp Flow';

-- Update existing users to split full_name if needed (optional migration)
-- UPDATE users 
-- SET 
--     first_name = SPLIT_PART(full_name, ' ', 1),
--     last_name = CASE 
--         WHEN full_name LIKE '% %' THEN 
--             SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
--         ELSE ''
--     END
-- WHERE full_name IS NOT NULL 
--   AND (first_name IS NULL OR last_name IS NULL);
