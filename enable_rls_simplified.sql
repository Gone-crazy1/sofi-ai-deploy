-- SIMPLIFIED RLS SETUP FOR SERVICE ROLE ACCESS
-- This approach allows your backend service role full access while blocking public access

-- Step 1: Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Step 2: Create policy for service role (your backend has full access)
-- Note: Replace 'service_role' with your actual service role if different
CREATE POLICY "Allow service role full access" ON public.users
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Step 3: Create policy to block all other access (including anonymous)
-- This ensures only your authenticated backend can access the data
CREATE POLICY "Block public access" ON public.users
FOR ALL 
TO anon, authenticated
USING (false)
WITH CHECK (false);

-- Step 4: Verify the setup
SELECT schemaname, tablename, rowsecurity, 
       CASE WHEN rowsecurity THEN 'Enabled' ELSE 'Disabled' END as rls_status
FROM pg_tables 
WHERE tablename = 'users' AND schemaname = 'public';

-- Step 5: Check existing policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'users' AND schemaname = 'public';
