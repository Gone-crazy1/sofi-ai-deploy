-- DISABLE ROW LEVEL SECURITY FOR ALL TABLES
-- Run these commands in Supabase SQL Editor (Dashboard > SQL Editor)

-- Disable RLS for users table
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Disable RLS for virtual_accounts table  
ALTER TABLE virtual_accounts DISABLE ROW LEVEL SECURITY;

-- Disable RLS for bank_transactions table
ALTER TABLE bank_transactions DISABLE ROW LEVEL SECURITY;

-- Disable RLS for transfer_recipients table (if exists)
ALTER TABLE transfer_recipients DISABLE ROW LEVEL SECURITY;

-- Disable RLS for beneficiaries table (if exists)
ALTER TABLE beneficiaries DISABLE ROW LEVEL SECURITY;

-- Disable RLS for paystack_webhook_logs table (if exists)
ALTER TABLE paystack_webhook_logs DISABLE ROW LEVEL SECURITY;

-- Check RLS status for all tables
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'virtual_accounts', 'bank_transactions', 'transfer_recipients', 'beneficiaries', 'paystack_webhook_logs');

-- The rowsecurity column should show 'f' (false) for all tables after running the above commands
