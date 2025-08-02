-- =============================================================================
-- SOFI AI - MISSING DATABASE TABLES FIX
-- =============================================================================
-- This script creates missing tables that are causing PIN validation errors

-- 1. CREATE PIN_ATTEMPTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.pin_attempts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    attempt_count INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_attempt TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add RLS (Row Level Security)
ALTER TABLE public.pin_attempts ENABLE ROW LEVEL SECURITY;

-- Create policy for pin_attempts
CREATE POLICY "Users can access their own pin attempts" ON public.pin_attempts
    FOR ALL USING (auth.uid() = user_id);

-- 2. ADD MISSING COLUMNS TO USERS TABLE (if they don't exist)
-- =============================================================================
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS pin_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS pin_locked_until TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS pin_set_at TIMESTAMPTZ;

-- 3. CREATE INDEXES FOR PERFORMANCE
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_pin_attempts_user_id ON public.pin_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_pin_attempts_locked_until ON public.pin_attempts(locked_until);
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON public.users(whatsapp_number);

-- 4. UPDATE EXISTING USERS TO HAVE PROPER PIN STRUCTURE
-- =============================================================================
UPDATE public.users 
SET pin_attempts = 0 
WHERE pin_attempts IS NULL;

-- =============================================================================
-- VERIFICATION QUERIES (Run these to check if tables exist)
-- =============================================================================

-- Check if pin_attempts table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'pin_attempts'
) AS pin_attempts_exists;

-- Check users table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'users' 
AND column_name IN ('pin_hash', 'pin_attempts', 'pin_locked_until', 'pin_set_at')
ORDER BY ordinal_position;

-- Count existing users with PIN data
SELECT 
    COUNT(*) as total_users,
    COUNT(pin_hash) as users_with_pin,
    COUNT(pin_attempts) as users_with_attempts_column
FROM public.users;
