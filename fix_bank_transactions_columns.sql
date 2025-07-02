-- Fix bank_transactions table to support both column name formats
-- Add the missing recipient_account column

ALTER TABLE bank_transactions 
ADD COLUMN IF NOT EXISTS recipient_account TEXT,
ADD COLUMN IF NOT EXISTS account_number TEXT,
ADD COLUMN IF NOT EXISTS bank_name TEXT;
