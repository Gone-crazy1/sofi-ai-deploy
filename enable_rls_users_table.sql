-- Enable Row Level Security (RLS) on the users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow service role full access (for your backend)
CREATE POLICY "Service role has full access" ON public.users
FOR ALL USING (true)
WITH CHECK (true);

-- Create a policy to allow users to only see their own data
CREATE POLICY "Users can view own profile" ON public.users
FOR SELECT USING (auth.uid()::text = telegram_chat_id::text);

-- Create a policy to allow users to update their own data
CREATE POLICY "Users can update own profile" ON public.users
FOR UPDATE USING (auth.uid()::text = telegram_chat_id::text)
WITH CHECK (auth.uid()::text = telegram_chat_id::text);

-- Optional: Allow authenticated users to insert their own data
CREATE POLICY "Users can insert own profile" ON public.users
FOR INSERT WITH CHECK (auth.uid()::text = telegram_chat_id::text);

-- Verify RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'users' AND schemaname = 'public';
